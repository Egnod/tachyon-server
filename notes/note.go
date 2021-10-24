package notes

type Note struct {
	// Basic
	Sign string `mapstructure:"sign"`

	Name string `mapstructure:"name"`
	Text string `mapstructure:"text"`

	// Advanced
	MaxVisits     uint16 `mapstructure:"max_visits"`
	CurrentVisits uint16 `mapstructure:"current_visits"`

	IsEncrypted  bool   `mapstructure:"is_encrypted"`
	PasswordHash string `mapstructure:"password_hash"`
}
