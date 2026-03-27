package logger

import (
	"log"
	"os"
)

var Logger = log.New(os.Stdout, "[converter-service] ", log.LstdFlags|log.Lmicroseconds)
