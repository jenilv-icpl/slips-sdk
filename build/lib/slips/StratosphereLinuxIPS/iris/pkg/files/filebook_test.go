package files

import (
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"happystoic/p2pnetwork/pkg/org"
	"io/ioutil"
	"os"
	"testing"
	"time"
)

// Test for GetFileCid function
func TestGetFileCid(t *testing.T) {
	// Create a temporary file with some data
	fileName := "testfile.txt"
	content := []byte("This is a test file for generating CID")
	err := ioutil.WriteFile(fileName, content, 0644)
	require.NoError(t, err)
	defer func() {
		_ = os.Remove(fileName)
	}()

	// Get the CID from the file
	cid, err := GetFileCid(fileName)
	require.NoError(t, err)
	assert.NotNil(t, cid)
}

// Test for GetBytesCid function
func TestGetBytesCid(t *testing.T) {
	// Create some data to generate a CID
	data := []byte("This is some sample data")

	// Get the CID from the data
	cid, err := GetBytesCid(data)
	require.NoError(t, err)
	assert.NotNil(t, cid)
}

// Test for FileBook AddFile and Get methods
func TestFileBook(t *testing.T) {
	// Create a new FileBook
	fb := NewFileBook()

	// Create a test FileMeta
	cid1, err := GetBytesCid([]byte("File 1"))
	require.NoError(t, err)

	fileMeta := &FileMeta{
		ExpiredAt: time.Now().Add(time.Hour),
		Expired:   false,
		Available: true,
		Path:      "file1.txt",
		Rights:    []*org.Org{},
		Severity:  MINOR,
	}

	// Add the file to the FileBook
	err = fb.AddFile(cid1, fileMeta)
	require.NoError(t, err)

	// Retrieve the file and verify its details
	retrievedMeta := fb.Get(cid1)
	assert.NotNil(t, retrievedMeta)
	assert.Equal(t, fileMeta.Path, retrievedMeta.Path)
	assert.Equal(t, fileMeta.Severity, retrievedMeta.Severity)

	// Try adding the same file again and expect an error
	err = fb.AddFile(cid1, fileMeta)
	assert.Errorf(t, err, "file with cid %s already exists", cid1.String())
}
