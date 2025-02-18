import boto3
import json

# load config
config = json.load(open("../config.json"))

AWS_REGION = config["AWS_REGION"]
ECR_REPO_NAME = config["ECR_REPO_NAME"]
EB_APP_NAME = config["EB_APP_NAME"]
EB_ENV_NAME = config["EB_ENV_NAME"]
ACCOUNT_ID = boto3.client("sts").get_caller_identity()["Account"]
ECR_URI = f"{ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{ECR_REPO_NAME}"


# initialize Elastic Beanstalk client
eb_client = boto3.client("elasticbeanstalk", region_name=AWS_REGION)

# create application
try:
    eb_client.create_application(ApplicationName=EB_APP_NAME)
    print(f"Created Elastic Beanstalk application: {EB_APP_NAME}")
except Exception as e:
    print(e)
    print(f"Elastic Beanstalk application {EB_APP_NAME} already exists.")


# create environment
response = eb_client.create_environment(
    ApplicationName=EB_APP_NAME,
    EnvironmentName=EB_ENV_NAME,
    SolutionStackName="64bit Amazon Linux 2023 v4.3.2 running Docker",
    OptionSettings=[
        {"Namespace": "aws:autoscaling:launchconfiguration",
            "OptionName": "InstanceType", "Value": "t2.micro"},
        {"Namespace": "aws:autoscaling:asg", "OptionName": "MinSize",
            "Value": str(config["SCALE_MIN_INSTANCES"])},
        {"Namespace": "aws:autoscaling:asg", "OptionName": "MaxSize",
            "Value": str(config["SCALE_MAX_INSTANCES"])},
        {"Namespace": "aws:elasticbeanstalk:environment",
            "OptionName": "LoadBalancerType", "Value": "application"},
        {"Namespace": "aws:autoscaling:trigger",
            "OptionName": "MeasureName", "Value": "CPUUtilization"},
        {"Namespace": "aws:autoscaling:trigger", "OptionName": "UpperThreshold",
            "Value": str(config["CPU_TARGET_UTILIZATION"])},
        {"Namespace": "aws:autoscaling:launchconfiguration",
            "OptionName": "IamInstanceProfile", "Value": "aws-elasticbeanstalk-ec2-role"},
    ],
)
print(f"Created Elastic Beanstalk environment: {response}")
