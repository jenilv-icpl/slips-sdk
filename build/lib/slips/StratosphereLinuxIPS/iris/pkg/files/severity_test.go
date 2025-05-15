package files

import (
	"testing"

	"github.com/pkg/errors"
	"github.com/stretchr/testify/assert"
)

func TestSeverityFromString(t *testing.T) {
	tests := []struct {
		input    string
		expected Severity
		err      error
	}{
		{"MINOR", MINOR, nil},
		{"major", MAJOR, nil},
		{"CRITICAL", CRITICAL, nil},
		{"critical", CRITICAL, nil},
		{"unknown", UNDEFINED, errors.New("unknown severity: unknown")},
	}

	for _, test := range tests {
		t.Run(test.input, func(t *testing.T) {
			result, err := SeverityFromString(test.input)

			if test.err != nil {
				assert.EqualError(t, err, test.err.Error())
			} else {
				assert.NoError(t, err)
			}

			assert.Equal(t, test.expected, result)
		})
	}
}

func TestSeverityString(t *testing.T) {
	tests := []struct {
		input    Severity
		expected string
	}{
		{MINOR, "MINOR"},
		{MAJOR, "MAJOR"},
		{CRITICAL, "CRITICAL"},
		{UNDEFINED, "unknown"},
	}

	for _, test := range tests {
		t.Run(test.input.String(), func(t *testing.T) {
			result := test.input.String()
			assert.Equal(t, test.expected, result)
		})
	}
}

func TestAllFileSeverities(t *testing.T) {
	expected := [3]Severity{MINOR, MAJOR, CRITICAL}
	result := AllFileSeverities()

	// Ensure the length matches
	assert.Equal(t, len(expected), len(result))

	// Ensure values match
	for i, severity := range expected {
		assert.Equal(t, severity, result[i])
	}
}
