package main

import (
	"fmt"
	"github.com/getsentry/sentry-go"
	sentryecho "github.com/getsentry/sentry-go/echo"
	"net/http"
	"os"
	"tachyon/notes"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

type (
	noteCreateResponse struct {
		Sign string `json:"sign"`
	}
	noteCreateRequest struct {
		// Basic
		Name string `json:"name"`
		Text string `json:"text"`

		// Advanced
		MaxVisits uint16 `json:"max_number_visits"`

		IsEncrypted bool   `json:"is_encrypted"`
		Password    string `json:"encrypt_password"`
	}
	noteReadResponse struct {
		Name string `json:"name"`
		Text string `json:"message"`
	}
	health struct {
		ServerTime string `json:"server_time"`
	}
)

func createNote(c echo.Context) error {
	request := &noteCreateRequest{
		MaxVisits:   0,
		IsEncrypted: false,
		Password:    "",
	}

	if err := c.Bind(request); err != nil {
		return err
	}

	dao := notes.NewDAO()

	response := &noteCreateResponse{
		Sign: dao.Create(request.Name, request.Text, request.MaxVisits, request.IsEncrypted, request.Password),
	}

	return c.JSON(http.StatusCreated, response)
}

func getNote(c echo.Context) error {
	password := c.QueryParam("password")
	sign := c.Param("sign")

	dao := notes.NewDAO()
	noteContent, dbHTTPStatusCode, withError := dao.Read(sign, password)

	if withError {
		return c.NoContent(dbHTTPStatusCode)
	}

	return c.JSON(http.StatusOK, &noteReadResponse{Name: noteContent.Name, Text: noteContent.Message})
}

func healthCheck(c echo.Context) error {
	res := &health{
		ServerTime: time.Now().Format(time.RFC3339Nano),
	}
	return c.JSON(http.StatusOK, res)
}

func main() {
	if value, ok := os.LookupEnv("TACHYON_SENTRY_DSN"); ok {
		if err := sentry.Init(sentry.ClientOptions{
			Dsn: value,
		}); err != nil {
			fmt.Printf("Sentry initialization failed: %v\n", err)
		}
	}

	e := echo.New()

	e.Use(sentryecho.New(sentryecho.Options{}))

	// Middleware
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())
	e.Use(middleware.CORSWithConfig(middleware.CORSConfig{
		AllowOrigins: []string{"*"},
		AllowHeaders: []string{"*"},
		AllowMethods: []string{"*"},
	}))

	// Routes
	e.GET("/", healthCheck)

	notesEndpoints := e.Group("/api/note")
	notesEndpoints.POST("/", createNote)
	notesEndpoints.GET("/:sign/", getNote)

	port := os.Getenv("PORT")

	if port == "" {
		port = "1323"
	}

	e.Logger.Fatal(e.Start(":" + port))
}
