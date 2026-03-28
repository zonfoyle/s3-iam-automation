from utils import (
    load_config,
    get_s3_client,
    get_iam_client,
    create_bucket,
    upload_file,
    list_files,
    create_iam_user,
    create_s3_policy,
    attach_policy_to_user,
)


def main():
    # Load project settings from config.yaml
    config = load_config()

    region = config["aws_region"]
    s3_client = get_s3_client(region)
    iam_client = get_iam_client()

    bucket_name = config["s3"]["bucket_name"]
    file_name = config["s3"]["file_to_upload"]

    user_name = config["iam"]["user_name"]
    policy_name = config["iam"]["policy_name"]

    # Provision storage resources
    create_bucket(s3_client, bucket_name, region)
    upload_file(s3_client, bucket_name, file_name)
    list_files(s3_client, bucket_name)

    # Provision IAM resources for controlled bucket access
    create_iam_user(iam_client, user_name)
    policy_arn = create_s3_policy(iam_client, policy_name, bucket_name)
    attach_policy_to_user(iam_client, user_name, policy_arn)


if __name__ == "__main__":
    main()