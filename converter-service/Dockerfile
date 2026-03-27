FROM golang:1.25 AS builder

WORKDIR /app
COPY . .

RUN go build -o app .

FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app/app .

CMD ["./app"]