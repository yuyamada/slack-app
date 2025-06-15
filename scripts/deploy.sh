#!/bin/bash
set -e

S3_BUCKET="yuyamada-lambda"
S3_KEY="slack-app/package.zip"

cd app
poetry build-lambda
aws s3 cp package.zip s3://$S3_BUCKET/$S3_KEY
aws lambda update-function-code --function-name slackApp --s3-bucket $S3_BUCKET --s3-key $S3_KEY
