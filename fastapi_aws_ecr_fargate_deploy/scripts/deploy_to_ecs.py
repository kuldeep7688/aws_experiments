import boto3
import json

with open("../config.json") as f:
    config = json.load(f)

AWS_REGION = config["AWS_REGION"]
CLUSTER_NAME = config["CLUSTER_NAME"]
TASK_FAMILY = config["TASK_FAMILY"]
SERVICE_NAME = config["SERVICE_NAME"]
CONTAINER_NAME = config["CONTAINER_NAME"]
CPU = config["CPU"]
MEMORY = config["MEMORY"]
DESIRED_COUNT = config["DESIRED_COUNT"]
ACCOUNT_ID = boto3.client("sts").get_caller_identity()["Account"]
ECR_URI = f"{ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{config['ECR_REPO']}:latest"

ecs_client = boto3.client("ecs", region_name=AWS_REGION)
alb_client = boto3.client("elbv2", region_name=AWS_REGION)

# Create ECS Cluster
try:
    ecs_client.create_cluster(clusterName=CLUSTER_NAME)
    print(f"ECS Cluster '{CLUSTER_NAME}' created.")
except ecs_client.exceptions.ClusterAlreadyExistsException:
    print("Cluster already exists.")

# Register Task Definition
task_definition = ecs_client.register_task_definition(
    family=TASK_FAMILY,
    networkMode="awsvpc",
    requiresCompatibilities=["FARGATE"],
    executionRoleArn=f"arn:aws:iam::{ACCOUNT_ID}:role/ecsTaskExecutionRole",
    cpu=CPU,
    memory=MEMORY,
    containerDefinitions=[
        {
            "name": CONTAINER_NAME,
            "image": ECR_URI,
            "portMappings": [{"containerPort": 8000, "hostPort": 8000}],
            "essential": True,
        }
    ],
)
print("Task definition registered.")

# Create ECS Service
ecs_client.create_service(
    cluster=CLUSTER_NAME,
    serviceName=SERVICE_NAME,
    taskDefinition=TASK_FAMILY,
    desiredCount=DESIRED_COUNT,
    launchType="FARGATE",
    networkConfiguration={
        "awsvpcConfiguration": {
            "subnets": ["subnet-xxxxxxx"],  # Replace with actual subnet ID
            # Replace with actual security group ID
            "securityGroups": ["sg-xxxxxxx"],
            "assignPublicIp": "ENABLED",
        }
    },
)
print("ECS Service created.")
