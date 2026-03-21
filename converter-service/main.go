package main

import (
	"fmt"
	"net/http"
	"net/url"
	"os"

	"converter-service/config"
	"converter-service/converter"
	"converter-service/logger"
	"converter-service/models"
	"converter-service/queue"
	"converter-service/storage"
)

func publishAudioReady(cfg *config.Config, videoID, audioPath string) error {
	return queue.PublishAudioReady(cfg.RabbitMQHost, videoID, audioPath)
}

func updateVideoStatus(videoID, status, outputPath, errMsg string) {
	// baseURL := "http://upload-service:8000/videos/" + videoID
	baseURL := "http://localhost:8000/videos/" + videoID

	params := url.Values{}
	params.Add("status", status)

	if outputPath != "" {
		params.Add("output_path", outputPath)
	}
	if errMsg != "" {
		params.Add("error", errMsg)
	}

	fullURL := baseURL + "?" + params.Encode()

	req, _ := http.NewRequest(http.MethodPatch, fullURL, nil)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		logger.Logger.Println("Failed to update status:", err)
		return
	}
	defer resp.Body.Close()
}

func main() {
	cfg := config.LoadConfig()
	store := storage.NewStorage(cfg)

	handler := func(msg models.VideoMessage) error {
		logger.Logger.Println("Processing:", msg.VideoID)

		inputFile := fmt.Sprintf("/tmp/%s.mp4", msg.VideoID)
		outputFile := fmt.Sprintf("/tmp/%s.mp3", msg.VideoID)

		updateVideoStatus(msg.VideoID, "processing", "", "")

		// 1. Download
		err := store.DownloadFile(msg.FilePath, inputFile)
		if err != nil {
			logger.Logger.Println("Download failed:", err)
			updateVideoStatus(msg.VideoID, "failed", "", err.Error())
			return err
		}

		// 2. Convert
		err = converter.ConvertToAudio(inputFile, outputFile)
		if err != nil {
			logger.Logger.Println("Conversion failed:", err)
			updateVideoStatus(msg.VideoID, "failed", "", err.Error())
			return err
		}

		// 3. Upload
		outputKey := fmt.Sprintf("%s.mp3", msg.VideoID)
		err = store.UploadFile(outputFile, outputKey)
		if err != nil {
			logger.Logger.Println("Upload failed:", err)
			updateVideoStatus(msg.VideoID, "failed", "", err.Error())
			return err
		}

		logger.Logger.Println("Audio ready:", outputKey)
		updateVideoStatus(msg.VideoID, "completed", outputKey, "")

		// Publish audio_ready event
		err = publishAudioReady(cfg, msg.VideoID, outputKey)
		if err != nil {
			logger.Logger.Println("Failed to publish audio_ready:", err)
			return err
		}

		// cleanup
		os.Remove(inputFile)
		os.Remove(outputFile)

		return nil
	}

	queue.StartConsumer(cfg, handler)
}
