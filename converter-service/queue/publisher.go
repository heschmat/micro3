package queue

import (
	"encoding/json"
	"net/url"

	"converter-service/config"
	"converter-service/logger"

	amqp "github.com/rabbitmq/amqp091-go"
)

func PublishAudioReady(cfg *config.Config, videoID, audioPath string) error {
	u := url.URL{
		Scheme: "amqp",
		User:   url.UserPassword(cfg.RabbitMQUser, cfg.RabbitMQPass),
		Host:   cfg.RabbitMQHost + ":5672",
	}

	conn, err := amqp.Dial(u.String())
	if err != nil {
		return err
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		return err
	}
	defer ch.Close()

	_, err = ch.QueueDeclare(
		cfg.AudioReadyQueue,
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return err
	}

	message := map[string]string{
		"video_id":   videoID,
		"audio_path": audioPath,
	}

	body, err := json.Marshal(message)
	if err != nil {
		return err
	}

	logger.Logger.Printf("Publishing audio_ready event body=%s", string(body))

	return ch.Publish(
		"",
		cfg.AudioReadyQueue,
		false,
		false,
		amqp.Publishing{
			ContentType:  "application/json",
			DeliveryMode: amqp.Persistent,
			Body:         body,
		},
	)
}
