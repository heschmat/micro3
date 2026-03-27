package storage

import (
	"context"
	"errors"
	"fmt"
	"os"
	"strings"

	"converter-service/config"
	"converter-service/logger"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/credentials"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/aws/smithy-go"
)

type Storage struct {
	Client *s3.Client
	Config *config.Config
}

func NewStorage(cfg *config.Config) *Storage {

	// ✅ EXPLICIT credentials (fixes your issue)
	creds := aws.NewCredentialsCache(
		credentials.NewStaticCredentialsProvider(
			cfg.S3AccessKey,
			cfg.S3SecretKey,
			"",
		),
	)

	client := s3.New(s3.Options{
		BaseEndpoint: aws.String(cfg.S3Endpoint),
		Region:       "us-east-1",
		Credentials:  creds,
		UsePathStyle: true, // required for MinIO
	})

	return &Storage{
		Client: client,
		Config: cfg,
	}
}

func (s *Storage) DownloadFile(key, localPath string) error {
	logger.Logger.Printf("Downloading key=%s localPath=%s", key, localPath)

	outFile, err := os.Create(localPath)
	if err != nil {
		return err
	}
	defer outFile.Close()

	resp, err := s.Client.GetObject(context.TODO(), &s3.GetObjectInput{
		Bucket: &s.Config.InputBucket,
		Key:    &key,
	})
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	_, err = outFile.ReadFrom(resp.Body)
	return err
}

func (s *Storage) UploadFile(localPath, key string) error {
	logger.Logger.Printf("Uploading key=%s localPath=%s", key, localPath)

	file, err := os.Open(localPath)
	if err != nil {
		return err
	}
	defer file.Close()

	_, err = s.Client.PutObject(context.TODO(), &s3.PutObjectInput{
		Bucket: &s.Config.OutputBucket,
		Key:    &key,
		Body:   file,
	})

	return err
}

func (s *Storage) OutputFileExists(key string) (bool, error) {
	_, err := s.Client.HeadObject(context.TODO(), &s3.HeadObjectInput{
		Bucket: &s.Config.OutputBucket,
		Key:    &key,
	})
	if err == nil {
		return true, nil
	}

	if IsNotFoundError(err) {
		return false, nil
	}

	return false, err
}

func IsNotFoundError(err error) bool {
	if err == nil {
		return false
	}

	var apiErr smithy.APIError
	if errors.As(err, &apiErr) {
		code := apiErr.ErrorCode()
		if code == "NoSuchKey" || code == "NotFound" || code == "NoSuchBucket" {
			return true
		}
	}

	msg := strings.ToLower(err.Error())
	return strings.Contains(msg, "no such key") || strings.Contains(msg, "not found")
}

func WrapInputDownloadError(err error, key string) error {
	if IsNotFoundError(err) {
		return fmt.Errorf("input file not found in object storage: %s", key)
	}
	return err
}
