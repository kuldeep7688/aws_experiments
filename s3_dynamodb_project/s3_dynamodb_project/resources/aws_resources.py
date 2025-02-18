from dagster import resource
import boto3

# from dagster_aws.s3 import S3Resource


# s3_resource = S3Resource()


@resource
def s3_client_resource():
    return boto3.client("s3")


@resource
def sqs_client_resource():
    return boto3.client("sqs")


@resource
def dynamodb_client_resource():
    return boto3.client("dynamodb")
