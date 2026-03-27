package converter

import (
	"context"
	"fmt"
	"os/exec"
	"time"

	"converter-service/logger"
	"converter-service/models"
)

func ConvertToAudio(inputPath, outputPath string, timeout time.Duration) error {
	logger.Logger.Printf("Starting conversion input=%s output=%s timeout=%s", inputPath, outputPath, timeout)

	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	// cmd := exec.Command("ffmpeg", "-i", inputPath, outputPath)
	cmd := exec.CommandContext(
		ctx,
		"ffmpeg",
		"-y",
		"-i", inputPath,
		"-vn",
		"-acodec", "libmp3lame",
		outputPath,
	)

	output, err := cmd.CombinedOutput()

	if ctx.Err() == context.DeadlineExceeded {
		return fmt.Errorf("ffmpeg timed out after %s", timeout)
	}

	if err != nil {
		logger.Logger.Printf("FFmpeg error output=%s", string(output))

		// Permanent-style conversion failure for bad media input.
		return models.NewPermanentErrorf("ffmpeg failed: %v", err)
	}

	logger.Logger.Printf("Conversion completed output=%s", outputPath)
	return nil
}
