package main

import (
	"fmt"
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

func main() {
	cfg := config.LoadConfig()
	store := storage.NewStorage(cfg)

	handler := func(msg models.VideoMessage) error {
		logger.Logger.Println("Processing:", msg.VideoID)

		inputFile := fmt.Sprintf("/tmp/%s.mp4", msg.VideoID)
		outputFile := fmt.Sprintf("/tmp/%s.mp3", msg.VideoID)

		// 1. Download
		err := store.DownloadFile(msg.FilePath, inputFile)
		if err != nil {
			logger.Logger.Println("Download failed:", err)
			return err
		}

		// 2. Convert
		err = converter.ConvertToAudio(inputFile, outputFile)
		if err != nil {
			logger.Logger.Println("Conversion failed:", err)
			return err
		}

		// 3. Upload
		outputKey := fmt.Sprintf("%s.mp3", msg.VideoID)
		err = store.UploadFile(outputFile, outputKey)
		if err != nil {
			logger.Logger.Println("Upload failed:", err)
			return err
		}

		logger.Logger.Println("Audio ready:", outputKey)

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
