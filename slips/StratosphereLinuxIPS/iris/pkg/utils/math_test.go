package utils

import (
	"testing"
	_ "testing"
)

func TestMax(t *testing.T) {
	tests := []struct {
		name string
		x    int
		y    int
		want int
	}{
		{
			name: "x is greater than y",
			x:    10,
			y:    5,
			want: 10,
		},
		{
			name: "y is greater than x",
			x:    3,
			y:    8,
			want: 8,
		},
		{
			name: "x equals y",
			x:    7,
			y:    7,
			want: 7,
		},
		{
			name: "negative numbers",
			x:    -4,
			y:    -2,
			want: -2,
		},
		{
			name: "mix of positive and negative",
			x:    -3,
			y:    4,
			want: 4,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := Max(tt.x, tt.y)
			if got != tt.want {
				t.Errorf("Max(%d, %d) = %d; want %d", tt.x, tt.y, got, tt.want)
			}
		})
	}
}
