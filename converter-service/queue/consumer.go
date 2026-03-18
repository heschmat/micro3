package queue

import (
	"encoding/json"

	"converter-service/config"
	"converter-service/logger"
	"converter-service/models"

	amqp "github.com/rabbitmq/amqp091-go"
)

func StartConsumer(cfg *config.Config, handler func(models.VideoMessage) error) {
	conn, err := amqp.Dial("amqp://guest:guest@" + cfg.RabbitMQHost + ":5672/")
	if err != nil {
		logger.Logger.Fatal("Failed to connect to RabbitMQ:", err)
	}

	ch, err := conn.Channel()
	if err != nil {
		logger.Logger.Fatal(err)
	}

	q, err := ch.QueueDeclare(
		"video_jobs",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		logger.Logger.Fatal(err)
	}

	msgs, err := ch.Consume(
		q.Name,
		"",
		false, // manual ack
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		logger.Logger.Fatal(err)
	}

	logger.Logger.Println("Waiting for messages...")

	for msg := range msgs {
		var videoMsg models.VideoMessage

		err := json.Unmarshal(msg.Body, &videoMsg)
		if err != nil {
			logger.Logger.Println("Invalid message:", err)
			msg.Nack(false, false)
			continue
		}

		err = handler(videoMsg)

		if err != nil {
			logger.Logger.Println("Processing failed, requeueing:", err)
			msg.Nack(false, true) // requeue
		} else {
			msg.Ack(false)
		}
	}
}
