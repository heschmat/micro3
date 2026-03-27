package models

import "fmt"

type PermanentError struct {
	Err error
}

func (e *PermanentError) Error() string {
	return e.Err.Error()
}

func (e *PermanentError) Unwrap() error {
	return e.Err
}

func NewPermanentError(err error) error {
	if err == nil {
		return nil
	}
	return &PermanentError{Err: err}
}

func IsPermanentError(err error) bool {
	if err == nil {
		return false
	}

	_, ok := err.(*PermanentError)
	return ok
}

func NewPermanentErrorf(format string, args ...any) error {
	return &PermanentError{
		Err: fmt.Errorf(format, args...),
	}
}
