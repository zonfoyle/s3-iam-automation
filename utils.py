import json
import boto3
import yaml
from botocore.exceptions import ClientError


def load_config(config_path="config.yaml"):
    """Load project configuration from YAML file."""
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def get_s3_client(region):
    """Create an S3 client for the specified AWS region."""
    return boto3.client("s3", region_name=region)


def get_iam_client():
    """Create an IAM client."""
    return boto3.client("iam")


def create_bucket(s3_client, bucket_name, region):
    """Create an S3 bucket if it does not already exist."""
    existing_buckets = s3_client.list_buckets()["Buckets"]

    # Reuse the bucket if it already exists to keep the workflow idempotent.
    for bucket in existing_buckets:
        if bucket["Name"] == bucket_name:
            print(f"Using existing bucket: {bucket_name}")
            return bucket_name

    # us-east-1 uses a slightly different create_bucket request format.
    if region == "us-east-1":
        s3_client.create_bucket(Bucket=bucket_name)
    else:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region}
        )

    print(f"Created bucket: {bucket_name}")
    return bucket_name


def upload_file(s3_client, bucket_name, file_name):
    """Upload a local file to the S3 bucket if it is not already present."""
    try:
        s3_client.head_object(Bucket=bucket_name, Key=file_name)
        print(f"File already exists in bucket: {file_name}")
        return
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code not in ["404", "NoSuchKey", "NotFound"]:
            raise

    s3_client.upload_file(file_name, bucket_name, file_name)
    print(f"Uploaded {file_name} to {bucket_name}")


def list_files(s3_client, bucket_name):
    """List all files currently stored in the S3 bucket."""
    response = s3_client.list_objects_v2(Bucket=bucket_name)

    if "Contents" not in response:
        print("No files in bucket.")
        return

    print("Files in bucket:")
    for obj in response["Contents"]:
        print(f" - {obj['Key']}")


def create_iam_user(iam_client, user_name):
    """Create an IAM user if it does not already exist."""
    try:
        iam_client.get_user(UserName=user_name)
        print(f"Using existing IAM user: {user_name}")
        return user_name
    except ClientError as e:
        if e.response["Error"]["Code"] != "NoSuchEntity":
            raise

    iam_client.create_user(UserName=user_name)
    print(f"Created IAM user: {user_name}")
    return user_name


def create_s3_policy(iam_client, policy_name, bucket_name):
    """Create a scoped IAM policy for access to the project bucket."""
    account_id = boto3.client("sts").get_caller_identity()["Account"]
    policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"

    try:
        iam_client.get_policy(PolicyArn=policy_arn)
        print(f"Using existing policy: {policy_name}")
        return policy_arn
    except ClientError as e:
        if e.response["Error"]["Code"] != "NoSuchEntity":
            raise

    # Limit permissions to this bucket only instead of granting broad S3 access.
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket"
                ],
                "Resource": f"arn:aws:s3:::{bucket_name}"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }

    response = iam_client.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document)
    )

    policy_arn = response["Policy"]["Arn"]
    print(f"Created policy: {policy_name}")
    return policy_arn


def attach_policy_to_user(iam_client, user_name, policy_arn):
    """Attach the S3 access policy to the IAM user if not already attached."""
    attached_policies = iam_client.list_attached_user_policies(
        UserName=user_name
    )["AttachedPolicies"]

    # Avoid attaching the same policy multiple times on reruns.
    for policy in attached_policies:
        if policy["PolicyArn"] == policy_arn:
            print(f"Policy already attached to user: {user_name}")
            return

    iam_client.attach_user_policy(
        UserName=user_name,
        PolicyArn=policy_arn
    )
    print(f"Attached policy to user: {user_name}")