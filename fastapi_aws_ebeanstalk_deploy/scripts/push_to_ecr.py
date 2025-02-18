import boto3
import os
import json
import subprocess


# load config
config = json.load(open("../config.json"))

AWS_REGION = config["AWS_REGION"]
ECR_REPO_NAME = config["ECR_REPO_NAME"]

ecr_client = boto3.client("ecr", region_name=AWS_REGION)


# Create ECR Repository if it doesn't exist
try:
    response = ecr_client.create_repository(
        repositoryName=ECR_REPO_NAME,
        imageTagMutability="MUTABLE",
    )
    print(f"Created ECR repository: {response['repository']['repositoryUri']}")
except ecr_client.exceptions.RepositoryAlreadyExistsException:
    print(f"ECR repository {ECR_REPO_NAME} already exists.")


# authenticate Docker to ECR
ACCOUNT_ID = boto3.client("sts").get_caller_identity()["Account"]
ECR_URI = f"{ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{ECR_REPO_NAME}"

subprocess.run(
    f"aws ecr get-login-password --region {AWS_REGION} | docker login --username AWS --password-stdin {ECR_URI}", shell=True, check=True)

# Build and push Docker image
subprocess.run(
    f"docker build -t {ECR_REPO_NAME} ../app", shell=True, check=True)
subprocess.run(
    f"docker tag {ECR_REPO_NAME}:latest {ECR_URI}:latest", shell=True, check=True)
subprocess.run(f"docker push {ECR_URI}:latest", shell=True, check=True)
print(f"Successfully pushed {ECR_REPO_NAME} to ECR repository {ECR_URI}")
