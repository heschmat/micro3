package config

import "os"

type Config struct {
	RabbitMQHost string

	S3Endpoint  string
	S3AccessKey string
	S3SecretKey string

	InputBucket  string
	OutputBucket string
}

func LoadConfig() *Config {
	return &Config{
		RabbitMQHost: getEnv("RABBITMQ_HOST", "localhost"),

		S3Endpoint:  getEnv("S3_ENDPOINT", "http://localhost:9000"),
		S3AccessKey: getEnv("S3_ACCESS_KEY", "minio"),
		S3SecretKey: getEnv("S3_SECRET_KEY", "minio123"),

		InputBucket:  getEnv("INPUT_BUCKET", "videos"),
		OutputBucket: getEnv("OUTPUT_BUCKET", "audios"),
	}
}

func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}
