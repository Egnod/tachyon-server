package db

import "github.com/IBM/cloudant-go-sdk/cloudantv1"

func GetDBClient() *cloudantv1.CloudantV1 {
	client, err := cloudantv1.NewCloudantV1UsingExternalConfig(
		&cloudantv1.CloudantV1Options{
			ServiceName: "TACHYON_DB",
		},
	)

	if err != nil {
		panic(err)
	}

	return client
}
