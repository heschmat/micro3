package queue

import (
	"encoding/json"
	"fmt"
	"net/url"

	"converter-service/config"
	"converter-service/logger"
	"converter-service/models"

	amqp "github.com/rabbitmq/amqp091-go"
)

var retryDelaysMs = []int32{5000, 15000, 30000}

func StartConsumer(cfg *config.Config, handler func(models.VideoMessage) error) {
	// user := url.QueryEscape(cfg.RabbitMQUser)
	// pass := url.QueryEscape(cfg.RabbitMQPass)

	// conn, err := amqp.Dial(
	// 	fmt.Sprintf("amqp://%s:%s@%s:5672/", user, pass, cfg.RabbitMQHost),
	// )
	u := url.URL{
		Scheme: "amqp",
		User:   url.UserPassword(cfg.RabbitMQUser, cfg.RabbitMQPass),
		Host:   cfg.RabbitMQHost + ":5672",
	}

	conn, err := amqp.Dial(u.String())
	if err != nil {
		logger.Logger.Fatal("Failed to connect to RabbitMQ:", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		logger.Logger.Fatal("Failed to open channel:", err)
	}
	defer ch.Close()

	if err := ch.Qos(1, 0, false); err != nil {
		logger.Logger.Fatal("Failed to set QoS:", err)
	}

	if err := declareQueues(ch, cfg); err != nil {
		logger.Logger.Fatal("Failed to declare queues:", err)
	}

	msgs, err := ch.Consume(
		cfg.VideoJobsQueue,
		"",
		false,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		logger.Logger.Fatal("Failed to register consumer:", err)
	}

	logger.Logger.Printf("Waiting for messages queue=%s", cfg.VideoJobsQueue)

	for msg := range msgs {
		var videoMsg models.VideoMessage

		if err := json.Unmarshal(msg.Body, &videoMsg); err != nil {
			logger.Logger.Printf("Invalid message body=%s err=%v", string(msg.Body), err)

			// Invalid message should not be retried.
			if err := publishJSON(ch, cfg.VideoJobsDLQ, msg.Body); err != nil {
				logger.Logger.Printf("Failed to publish invalid message to DLQ err=%v", err)
				_ = msg.Nack(false, false)
				continue
			}

			_ = msg.Ack(false)
			continue
		}

		logger.Logger.Printf("Received message video_id=%s retry_count=%d", videoMsg.VideoID, videoMsg.RetryCount)

		err := handler(videoMsg)
		if err == nil {
			logger.Logger.Printf("Processed successfully video_id=%s", videoMsg.VideoID)
			_ = msg.Ack(false)
			continue
		}

		logger.Logger.Printf("Processing failed video_id=%s retry_count=%d err=%v", videoMsg.VideoID, videoMsg.RetryCount, err)

		if models.IsPermanentError(err) {
			logger.Logger.Printf("Permanent failure video_id=%s sending_to_dlq=true", videoMsg.VideoID)

			videoMsg.RetryCount++
			body, marshalErr := json.Marshal(videoMsg)
			if marshalErr != nil {
				logger.Logger.Printf("Failed to marshal permanent failure message video_id=%s err=%v", videoMsg.VideoID, marshalErr)
				_ = msg.Nack(false, false)
				continue
			}

			if err := publishJSON(ch, cfg.VideoJobsDLQ, body); err != nil {
				logger.Logger.Printf("Failed to publish permanent failure to DLQ video_id=%s err=%v", videoMsg.VideoID, err)
				_ = msg.Nack(false, false)
				continue
			}

			_ = msg.Ack(false)
			continue
		}

		if videoMsg.RetryCount < cfg.MaxRetries {
			videoMsg.RetryCount++

			retryQueueName, retryDelay := getRetryQueueName(videoMsg.RetryCount)
			body, marshalErr := json.Marshal(videoMsg)
			if marshalErr != nil {
				logger.Logger.Printf("Failed to marshal retry message video_id=%s err=%v", videoMsg.VideoID, marshalErr)
				_ = msg.Nack(false, false)
				continue
			}

			logger.Logger.Printf(
				"Scheduling retry video_id=%s attempt=%d delay_ms=%d queue=%s",
				videoMsg.VideoID,
				videoMsg.RetryCount,
				retryDelay,
				retryQueueName,
			)

			if err := publishJSON(ch, retryQueueName, body); err != nil {
				logger.Logger.Printf("Failed to publish retry message video_id=%s err=%v", videoMsg.VideoID, err)
				_ = msg.Nack(false, true)
				continue
			}

			_ = msg.Ack(false)
			continue
		}

		logger.Logger.Printf("Max retries reached video_id=%s sending_to_dlq=true", videoMsg.VideoID)

		videoMsg.RetryCount++
		body, marshalErr := json.Marshal(videoMsg)
		if marshalErr != nil {
			logger.Logger.Printf("Failed to marshal max-retry DLQ message video_id=%s err=%v", videoMsg.VideoID, marshalErr)
			_ = msg.Nack(false, false)
			continue
		}

		if err := publishJSON(ch, cfg.VideoJobsDLQ, body); err != nil {
			logger.Logger.Printf("Failed to publish max-retry message to DLQ video_id=%s err=%v", videoMsg.VideoID, err)
			_ = msg.Nack(false, false)
			continue
		}

		_ = msg.Ack(false)
	}
}

func declareQueues(ch *amqp.Channel, cfg *config.Config) error {
	_, err := ch.QueueDeclare(
		cfg.VideoJobsDLQ,
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return err
	}

	args := amqp.Table{
		"x-dead-letter-exchange":    "",
		"x-dead-letter-routing-key": cfg.VideoJobsDLQ,
	}

	_, err = ch.QueueDeclare(
		cfg.VideoJobsQueue,
		true,
		false,
		false,
		false,
		args,
	)
	if err != nil {
		return err
	}

	for i, ttl := range retryDelaysMs {
		queueName := fmt.Sprintf("%s_retry_%d", cfg.VideoJobsQueue, i+1)

		retryArgs := amqp.Table{
			"x-message-ttl":             ttl,
			"x-dead-letter-exchange":    "",
			"x-dead-letter-routing-key": cfg.VideoJobsQueue,
		}

		_, err := ch.QueueDeclare(
			queueName,
			true,
			false,
			false,
			false,
			retryArgs,
		)
		if err != nil {
			return err
		}
	}

	return nil
}

func getRetryQueueName(attempt int) (string, int32) {
	index := attempt - 1
	if index < 0 {
		index = 0
	}
	if index >= len(retryDelaysMs) {
		index = len(retryDelaysMs) - 1
	}

	return fmt.Sprintf("video_jobs_retry_%d", index+1), retryDelaysMs[index]
}

func publishJSON(ch *amqp.Channel, queueName string, body []byte) error {
	return ch.Publish(
		"",
		queueName,
		false,
		false,
		amqp.Publishing{
			ContentType:  "application/json",
			DeliveryMode: amqp.Persistent,
			Body:         body,
		},
	)
}
