package converter

import (
	"os/exec"

	"converter-service/logger"
)

func ConvertToAudio(inputPath, outputPath string) error {
	logger.Logger.Println("Starting conversion:", inputPath)

	cmd := exec.Command("ffmpeg", "-i", inputPath, outputPath)

	output, err := cmd.CombinedOutput()
	if err != nil {
		logger.Logger.Println("FFmpeg error:", string(output))
		return err
	}

	logger.Logger.Println("Conversion completed:", outputPath)
	return nil
}
