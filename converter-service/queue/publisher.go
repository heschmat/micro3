package queue

import (
	"encoding/json"

	"converter-service/logger"

	amqp "github.com/rabbitmq/amqp091-go"
)

func PublishAudioReady(rabbitHost, videoID, audioPath string) error {
	conn, err := amqp.Dial("amqp://guest:guest@" + rabbitHost + ":5672/")
	if err != nil {
		return err
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		return err
	}
	defer ch.Close()

	queueName := "audio_ready"

	_, err = ch.QueueDeclare(
		queueName,
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

	body, _ := json.Marshal(message)

	logger.Logger.Println("Publishing audio_ready event:", string(body))

	return ch.Publish(
		"",
		queueName,
		false,
		false,
		amqp.Publishing{
			ContentType: "application/json",
			Body:        body,
		},
	)
}
