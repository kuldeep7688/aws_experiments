import boto3
import json
import subprocess

with open("../config.json") as f:
    config = json.load(f)

AWS_REGION = config["AWS_REGION"]
ECR_REPO = config["ECR_REPO"]

ecr_client = boto3.client("ecr", region_name=AWS_REGION)

# Create ECR repository if not exists
try:
    response = ecr_client.create_repository(repositoryName=ECR_REPO)
    print(f"Created ECR repository: {response['repository']['repositoryUri']}")
except ecr_client.exceptions.RepositoryAlreadyExistsException:
    print("Repository already exists.")

# Authenticate Docker
ACCOUNT_ID = boto3.client("sts").get_caller_identity()["Account"]
ECR_URI = f"{ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{ECR_REPO}"

subprocess.run(
    f"aws ecr get-login-password --region {AWS_REGION} | docker login --username AWS --password-stdin {ECR_URI}", shell=True)

# Build and push Docker image
subprocess.run(f"docker build -t {ECR_REPO} ../app", shell=True)
subprocess.run(f"docker tag {ECR_REPO}:latest {ECR_URI}:latest", shell=True)
subprocess.run(f"docker push {ECR_URI}:latest", shell=True)

print(f"Image pushed to {ECR_URI}")
