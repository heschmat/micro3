package config

import (
	"os"
	"strconv"
)

type Config struct {
	RabbitMQHost string
	RabbitMQUser string
	RabbitMQPass string

	S3Endpoint  string
	S3AccessKey string
	S3SecretKey string

	InputBucket  string
	OutputBucket string

	UploadServiceURL string

	VideoJobsQueue  string
	AudioReadyQueue string
	VideoJobsDLQ    string

	MaxRetries           int
	FFmpegTimeoutSeconds int
}

func LoadConfig() *Config {
	return &Config{
		RabbitMQHost: getEnv("RABBITMQ_HOST", "localhost"),
		RabbitMQUser: getEnv("RABBITMQ_USER", "guest"),
		RabbitMQPass: getEnv("RABBITMQ_PASS", "guest"),

		S3Endpoint:  getEnv("S3_ENDPOINT", "http://localhost:9000"),
		S3AccessKey: getEnv("S3_ACCESS_KEY", "minio"),
		S3SecretKey: getEnv("S3_SECRET_KEY", "minio123"),

		InputBucket:  getEnv("INPUT_BUCKET", "videos"),
		OutputBucket: getEnv("OUTPUT_BUCKET", "audios"),

		UploadServiceURL: getEnv("UPLOAD_SERVICE_URL", "http://localhost:8000"),

		VideoJobsQueue:  getEnv("VIDEO_JOBS_QUEUE", "video_jobs"),
		AudioReadyQueue: getEnv("AUDIO_READY_QUEUE", "audio_ready"),
		VideoJobsDLQ:    getEnv("VIDEO_JOBS_DLQ", "video_jobs_dlq"),

		MaxRetries:           getEnvAsInt("MAX_RETRIES", 3),
		FFmpegTimeoutSeconds: getEnvAsInt("FFMPEG_TIMEOUT_SECONDS", 600),
	}
}

func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}

func getEnvAsInt(key string, fallback int) int {
	value, exists := os.LookupEnv(key)
	if !exists {
		return fallback
	}

	parsed, err := strconv.Atoi(value)
	if err != nil {
		return fallback
	}
	return parsed
}
