package notes

import (
	"encoding/base64"
	"fmt"
	"github.com/IBM/cloudant-go-sdk/cloudantv1"
	"github.com/google/uuid"
	"github.com/kevinburke/nacl"
	"github.com/kevinburke/nacl/secretbox"
	"github.com/mitchellh/mapstructure"
	"golang.org/x/crypto/blake2b"
	"net/http"
	"os"
	"strings"
	"tachyon/db"
	"tachyon/notes/utils"
)

type DAO struct {
	Client *cloudantv1.CloudantV1
	DBName string
}

type NoteContent struct {
	Name    string
	Message string
}

func getDBName() string {
	if value, ok := os.LookupEnv("TACHYON_DB_NOTES_BASE"); ok {
		return value
	}
	return "notes"
}

func NewDAO() DAO {
	dao := DAO{
		Client: db.GetDBClient(),
		DBName: getDBName(),
	}

	dao.prepareDB()

	return dao
}

func (dao *DAO) prepareDB() bool {
	dbName := dao.DBName

	_, putDatabaseResponse, err := dao.Client.PutDatabase(
		dao.Client.NewPutDatabaseOptions(dbName),
	)
	if err != nil {
		if putDatabaseResponse.StatusCode == http.StatusPreconditionFailed {
			fmt.Printf("Cannot create \"%s\" database, it already exists.\n", dbName)
		} else {
			panic(err)
		}
	}

	return true
}

func (dao *DAO) generateSign() string {
	return strings.Replace(uuid.New().String(), "-", "", -1)
}

func (dao *DAO) Create(name string, text string, maxVisits uint16, isEncrypted bool, password string) string {
	passwordHash := ""
	sign := dao.generateSign()

	if isEncrypted {
		key := blake2b.Sum256([]byte(password))
		naclKey := nacl.Key(key[:])
		box := secretbox.EasySeal([]byte(text), naclKey)

		text = base64.URLEncoding.EncodeToString(box)
		passwordHash, _ = utils.NewArgon2ID().Hash(password)
	}

	newNote := &Note{
		Sign:          sign,
		Name:          name,
		Text:          text,
		MaxVisits:     maxVisits,
		CurrentVisits: 0,
		IsEncrypted:   isEncrypted,
		PasswordHash:  passwordHash,
	}

	var result map[string]interface{}

	err := mapstructure.Decode(newNote, &result)

	if err != nil {
		panic(err)
	}

	newNoteDocument := cloudantv1.Document{
		ID: &sign,
	}
	newNoteDocument.SetProperties(result)

	postDocumentOption := dao.Client.NewPostDocumentOptions(
		dao.DBName,
	).SetDocument(&newNoteDocument)

	_, _, err = dao.Client.PostDocument(postDocumentOption)
	if err != nil {
		panic(err)
	}

	return sign
}

func (dao *DAO) Read(sign string, password string) (NoteContent, int, bool) {
	noteDocument, response, err := dao.Client.GetDocument(
		dao.Client.NewGetDocumentOptions(
			dao.DBName,
			sign,
		),
	)

	if err != nil {
		return NoteContent{Name: "", Message: ""}, response.StatusCode, true
	}

	var existsNote Note

	err = mapstructure.Decode(noteDocument.GetProperties(), &existsNote)

	if err != nil {
		panic(err)
	}

	text := existsNote.Text

	if existsNote.IsEncrypted {
		verified, err := utils.NewArgon2ID().Verify(password, existsNote.PasswordHash)

		if !verified || err != nil {
			return NoteContent{Name: "", Message: ""}, http.StatusUnauthorized, true
		}

		key := blake2b.Sum256([]byte(password))
		naclKey := nacl.Key(key[:])

		box, err := base64.URLEncoding.DecodeString(existsNote.Text)

		if err != nil {
			panic(err)
		}

		box, err = secretbox.EasyOpen(box, naclKey)

		if err != nil {
			panic(err)
		}

		text = string(box)
	}

	existsNote.CurrentVisits += 1

	noteDocument.SetProperty("current_visits", existsNote.CurrentVisits)

	postDocumentOption := dao.Client.NewPostDocumentOptions(
		dao.DBName,
	).SetDocument(noteDocument)

	noteUpdateDocument, response, err := dao.Client.PostDocument(
		postDocumentOption,
	)

	if err != nil {
		return NoteContent{Name: "", Message: ""}, response.StatusCode, true
	}

	if existsNote.MaxVisits != 0 {
		if existsNote.CurrentVisits >= existsNote.MaxVisits {
			_, response, err := dao.Client.DeleteDocument(
				dao.Client.NewDeleteDocumentOptions(
					dao.DBName,
					sign,
				).SetRev(*noteUpdateDocument.Rev),
			)
			if err != nil {
				return NoteContent{Name: "", Message: ""}, response.StatusCode, true
			}
		}
	}

	return NoteContent{Name: existsNote.Name, Message: text}, http.StatusOK, false
}
