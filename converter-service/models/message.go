package models

type VideoMessage struct {
	VideoID      string `json:"video_id"`
	FilePath     string `json:"file_path"`
	OutputFormat string `json:"output_format"`
}
