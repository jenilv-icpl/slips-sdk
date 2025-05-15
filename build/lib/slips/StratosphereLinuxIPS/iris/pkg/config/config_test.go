package config

import (
	"github.com/stretchr/testify/assert"
	"testing"
)

// Test Redis.validate()
func TestRedisValidate(t *testing.T) {
	tests := []struct {
		name    string
		config  Redis
		wantErr bool
	}{
		{"Valid Redis config", Redis{Host: "localhost", Tl2NlChannel: "updates"}, false},
		{"Missing host", Redis{Tl2NlChannel: "updates"}, true},
		{"Missing channel", Redis{Host: "localhost"}, true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.config.validate()
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

// Test Redis.setDefaults()
func TestRedisSetDefaults(t *testing.T) {
	redis := Redis{}
	redis.setDefaults()
	assert.Equal(t, uint(6379), redis.Port)
}

// Test ProtocolSettings.validate()
func TestProtocolSettingsValidate(t *testing.T) {
	ps := ProtocolSettings{
		FileShare: FileShareSettings{
			MetaSpreadSettings: map[string]SpreadStrategy{
				"invalid": {NumberOfPeers: -1, Until: -1, Every: -1},
			},
		},
	}
	err := ps.validate()
	assert.Error(t, err) // Invalid severity should trigger an error
}
