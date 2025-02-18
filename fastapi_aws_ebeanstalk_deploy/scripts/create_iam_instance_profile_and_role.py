import boto3
import json

iam_client = boto3.client("iam")

INSTANCE_PROFILE_NAME = "aws-elasticbeanstalk-ec2-role"
ROLE_NAME = "aws-elasticbeanstalk-ec2-role"

# Check if the instance profile exists
try:
    iam_client.get_instance_profile(InstanceProfileName=INSTANCE_PROFILE_NAME)
    print(f"Instance Profile {INSTANCE_PROFILE_NAME} already exists.")
except iam_client.exceptions.NoSuchEntityException:
    print(f"Creating Instance Profile: {INSTANCE_PROFILE_NAME}")

    # Create IAM Role
    iam_client.create_role(
        RoleName=ROLE_NAME,
        AssumeRolePolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        })
    )

    # Attach AWS Managed Policy for Beanstalk
    iam_client.attach_role_policy(
        RoleName=ROLE_NAME,
        PolicyArn="arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
    )

    # Create Instance Profile
    iam_client.create_instance_profile(
        InstanceProfileName=INSTANCE_PROFILE_NAME)

    # Attach role to instance profile
    iam_client.add_role_to_instance_profile(
        InstanceProfileName=INSTANCE_PROFILE_NAME,
        RoleName=ROLE_NAME
    )

    print(f"Instance Profile {INSTANCE_PROFILE_NAME} created and configured.")
