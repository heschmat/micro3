package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"
	"time"

	"converter-service/config"
	"converter-service/converter"
	"converter-service/logger"
	"converter-service/models"
	"converter-service/queue"
	"converter-service/storage"
)

type VideoStatusResponse struct {
	ID         string `json:"id"`
	Status     string `json:"status"`
	OutputPath string `json:"output_path"`
	Error      string `json:"error"`
}

func publishAudioReady(cfg *config.Config, videoID, audioPath string) error {
	return queue.PublishAudioReady(cfg, videoID, audioPath)
}

func updateVideoStatus(cfg *config.Config, videoID, status, outputPath, errMsg string) {
	baseURL := cfg.UploadServiceURL + "/videos/" + videoID

	params := url.Values{}
	params.Add("status", status)

	if outputPath != "" {
		params.Add("output_path", outputPath)
	}
	if errMsg != "" {
		params.Add("error", errMsg)
	}

	fullURL := baseURL + "?" + params.Encode()

	req, err := http.NewRequest(http.MethodPatch, fullURL, nil)
	if err != nil {
		logger.Logger.Printf("Failed to create PATCH request video_id=%s err=%v", videoID, err)
		return
	}

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		logger.Logger.Printf("Failed to update status video_id=%s status=%s err=%v", videoID, status, err)
		return
	}
	defer resp.Body.Close()

	logger.Logger.Printf("Updated video status video_id=%s status=%s", videoID, status)
}

func fetchVideoStatus(cfg *config.Config, videoID string) (*VideoStatusResponse, error) {
	endpoint := cfg.UploadServiceURL + "/videos/" + videoID

	req, err := http.NewRequest(http.MethodGet, endpoint, nil)
	if err != nil {
		return nil, err
	}

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("status lookup failed with http %d", resp.StatusCode)
	}

	var payload VideoStatusResponse
	if err := json.NewDecoder(resp.Body).Decode(&payload); err != nil {
		return nil, err
	}

	return &payload, nil
}

func alreadyCompleted(cfg *config.Config, store *storage.Storage, videoID, outputKey string) (bool, error) {
	status, err := fetchVideoStatus(cfg, videoID)
	if err == nil && status != nil {
		if status.Status == "completed" && status.OutputPath == outputKey {
			logger.Logger.Printf("Skipping duplicate message because DB already completed video_id=%s output=%s", videoID, outputKey)
			return true, nil
		}
	}

	exists, err := store.OutputFileExists(outputKey)
	if err != nil {
		return false, err
	}
	if exists {
		logger.Logger.Printf("Output already exists in storage video_id=%s output=%s", videoID, outputKey)
		updateVideoStatus(cfg, videoID, "completed", outputKey, "")
		return true, nil
	}

	return false, nil
}

func main() {
	cfg := config.LoadConfig()
	store := storage.NewStorage(cfg)

	handler := func(msg models.VideoMessage) error {
		outputKey := fmt.Sprintf("%s.mp3", msg.VideoID)
		inputFile := fmt.Sprintf("/tmp/%s.mp4", msg.VideoID)
		outputFile := fmt.Sprintf("/tmp/%s.mp3", msg.VideoID)

		logger.Logger.Printf(
			"Processing started video_id=%s file_path=%s retry_count=%d",
			msg.VideoID,
			msg.FilePath,
			msg.RetryCount,
		)

		defer func() {
			if err := os.Remove(inputFile); err == nil {
				logger.Logger.Printf("Removed temp input file video_id=%s path=%s", msg.VideoID, inputFile)
			}
			if err := os.Remove(outputFile); err == nil {
				logger.Logger.Printf("Removed temp output file video_id=%s path=%s", msg.VideoID, outputFile)
			}
		}()

		done, err := alreadyCompleted(cfg, store, msg.VideoID, outputKey)
		if err != nil {
			logger.Logger.Printf("Idempotency check failed video_id=%s err=%v", msg.VideoID, err)
			return err
		}
		if done {
			return nil
		}

		updateVideoStatus(cfg, msg.VideoID, "processing", "", "")
		err = store.DownloadFile(msg.FilePath, inputFile)
		if err != nil {
			err = storage.WrapInputDownloadError(err, msg.FilePath)
			logger.Logger.Printf("Download failed video_id=%s err=%v", msg.VideoID, err)
			updateVideoStatus(cfg, msg.VideoID, "failed", "", err.Error())

			if storage.IsNotFoundError(err) || err.Error() == fmt.Sprintf("input file not found in object storage: %s", msg.FilePath) {
				return models.NewPermanentError(err)
			}
			return err
		}

		updateVideoStatus(cfg, msg.VideoID, "converting", "", "")
		err = converter.ConvertToAudio(inputFile, outputFile, time.Duration(cfg.FFmpegTimeoutSeconds)*time.Second)
		if err != nil {
			logger.Logger.Printf("Conversion failed video_id=%s err=%v", msg.VideoID, err)
			updateVideoStatus(cfg, msg.VideoID, "failed", "", err.Error())
			return err
		}

		updateVideoStatus(cfg, msg.VideoID, "uploading", "", "")
		err = store.UploadFile(outputFile, outputKey)
		if err != nil {
			logger.Logger.Printf("Upload failed video_id=%s err=%v", msg.VideoID, err)
			updateVideoStatus(cfg, msg.VideoID, "failed", "", err.Error())
			return err
		}

		logger.Logger.Printf("Audio ready video_id=%s output=%s", msg.VideoID, outputKey)
		updateVideoStatus(cfg, msg.VideoID, "completed", outputKey, "")

		err = publishAudioReady(cfg, msg.VideoID, outputKey)
		if err != nil {
			logger.Logger.Printf("Failed to publish audio_ready video_id=%s err=%v", msg.VideoID, err)
			return err
		}

		logger.Logger.Printf("Processing completed video_id=%s", msg.VideoID)
		return nil
	}

	queue.StartConsumer(cfg, handler)
}
