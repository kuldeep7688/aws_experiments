import os
import json
import time
from dagster import asset, AssetIn
from s3_dynamodb_project.resources.aws_resources import s3_client_resource, sqs_client_resource, dynamodb_client_resource


# dynamo db schema
# {
#   "file_key": "uploaded/data.txt",
#   "status": "PROCESSING",
#   "timestamp": 1674050327,
#   "processed_file_key": "processed/data.txt",
#   "error_message": ""
# }

SOURCE_BUCKET = ""
PROCESSED_BUCKET = ""
SQS_QUEUE_URL = ""
DYNAMODB_TABLE_NAME = ""
LOCAL_DOWNLOAD_PATH = ""


@asset(
    required_resource_keys={"sqs"}
)
def check_sqs_for_new_records(context) -> str:
    """Polls SQS for new file records."""
    sqs_client = context.resources.sqs
    response = sqs_client.receive_message(
        QueueUrl=SQS_QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=5
    )
    messages = response.get("Messages", [])
    if not messages:
        context.log.info("No new SQS messages.")
        return None

    # Extract the file key from the SQS message
    message_body = json.loads(messages[0]["Body"])
    # Your SQS message might have more details. Adjust as needed:
    file_key = message_body.get("file_key")
    context.log.info(f"Received SQS message for file_key: {file_key}")

    return file_key


@asset(
    required_resource_keys={"s3", "dynamodb"},
    ins={"file_key": AssetIn("check_sqs_for_new_records")}
)
def download_and_preprocess_file(context, file_key: str) -> str:
    """
    Downloads the file from the source S3 bucket and performs perprocessing.
    Returns the processed file content as a string (or any structured data).
    """
    if not file_key:
        context.log.info("No file_key to response")

    s3_client = context.resources.s3
    dynamodb_client = context.resources.dynamodb

    # Mark record as PROCESSING
    dynamodb_client.update_item(
        TableName=DYNAMODB_TABLE_NAME,
        Key={"file_key": {"S": file_key}},
        UpdateExpression="SET #st = :s",
        ExpressionAttributeNames={"#st": "status"},
        ExpressionAttributeValues={":s": {"S": "PROCESSING"}},
    )

    # download file locally
    local_path = os.path.join(LOCAL_DOWNLOAD_PATH, os.path.basename(file_key))
    s3_client.download_file(SOURCE_BUCKET, file_key, local_path)

    # processing
    file_content = open(local_path, "r").read()
    file_content = file_content.upper()

    return file_content


@asset(
    required_resource_keys={"s3"},
    ins={"processed_content": AssetIn("download_and_preprocess_file")}
)
def upload_preprocessed_file(context, processed_content: str) -> str:
    """
    Uploads the preprocessed content to s3 bucket
    """

    if not processed_content:
        context.log.info("No processed content to upload.")
        return None

    s3_client = context.resources.s3
    # You can define a new S3 key based on a timestamp or a known pattern
    timestamp = int(time.time())
    processed_key = f"processed/processed_file_{timestamp}.txt"

    s3_client.put_object(
        Bucket=PROCESSED_BUCKET,
        Key=processed_key,
        Body=processed_content.encode("utf-8"),
    )
    context.log.info(
        f"Uploaded processed file to {PROCESSED_BUCKET}/{processed_key}")

    return processed_key


@asset(
    required_resource_keys={"dynamodb"},
    ins={
        "file_key": AssetIn("check_sqs_for_new_records"),
        "processed_file_key": AssetIn("upload_preprocessed_file")
    }
)
def update_dynamo_db_record(context, file_key: str, processed_file_key: str):
    """
    Updates the DynamoDB record with the processed file location and final status.
    """
    if not file_key or not processed_file_key:
        context.log.info(
            "No updates to DynamoDB. Missing file_key or processed_file_key.")
        return

    dynamodb_client = context.resources.dynamodb

    dynamodb_client.update_item(
        TableName=DYNAMODB_TABLE_NAME,
        Key={"file_key": {"S": file_key}},
        UpdateExpression="SET #st = :s, #pf = :p",
        ExpressionAttributeNames={
            "#st": "status", "#pf": "processed_file_key"},
        ExpressionAttributeValues={
            ":s": {"S": "COMPLETED"},
            ":p": {"S": processed_file_key},
        },
    )
    context.log.info(
        f"Updated DynamoDB record for {file_key} with {processed_file_key}.")
