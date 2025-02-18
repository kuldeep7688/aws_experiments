import boto3
import json
import time

# Load config
with open("../config.json") as f:
    config = json.load(f)

AWS_REGION = config["AWS_REGION"]
ECR_REPO = config["ECR_REPO"]
EB_APP_NAME = config["EB_APP_NAME"]
EB_ENV_NAME = config["EB_ENV_NAME"]
ACCOUNT_ID = boto3.client("sts").get_caller_identity()["Account"]
ECR_URI = f"{ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{ECR_REPO}"

# Initialize AWS Clients
eb_client = boto3.client("elasticbeanstalk", region_name=AWS_REGION)
ecr_client = boto3.client("ecr", region_name=AWS_REGION)

# Step 1: Get the latest pushed image URI from ECR
# List the images in the ECR repository, sorted by push time (descending)
response = ecr_client.describe_images(
    repositoryName=ECR_REPO,
    maxResults=1,
    filter={
        'tagStatus': 'TAGGED'
    }
)

# Get the URI of the most recently pushed image
latest_image = response['imageDetails'][0]
# Assuming we are using the tag that was applied
latest_image_uri = f"{ECR_URI}:{latest_image['imageTags'][0]}"

print(f"Latest image from ECR: {latest_image_uri}")

# Step 2: Create a new Elastic Beanstalk application version
# We don't need to upload new code; just create a version based on the current Docker image
response = eb_client.create_application_version(
    ApplicationName=EB_APP_NAME,
    VersionLabel=f"v{int(time.time())}",  # Versioning based on timestamp
    AutoCreateApplication=True
)
version_label = response["ApplicationVersion"]["VersionLabel"]
print(f"Created new application version: {version_label}")

# Step 3: Update the Elastic Beanstalk environment to use the latest Docker image
response = eb_client.update_environment(
    EnvironmentName=EB_ENV_NAME,
    VersionLabel=version_label,
    OptionSettings=[
        # Set the Docker image URI in the Elastic Beanstalk environment configuration
        {"Namespace": "aws:elasticbeanstalk:container:docker",
            "OptionName": "Image", "Value": latest_image_uri}
    ]
)
print(
    f"Elastic Beanstalk environment {EB_ENV_NAME} is being updated with the new version: {version_label}")
