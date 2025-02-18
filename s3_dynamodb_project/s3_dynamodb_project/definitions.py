from dagster import Definitions, load_asset_checks_from_modules
from .assets.s3_assets import (
    check_sqs_for_new_records,
    update_dynamo_db_record,
    upload_preprocessed_file,
    download_and_preprocess_file
)
from .resources.aws_resources import (
    s3_client_resource,
    dynamodb_client_resource,
    sqs_client_resource
)
from .jobs.processing_job import processing_job
from .schedules.processing_schedule import processing_schedule


# all_assets = load_asset_checks_from_modules([s3_assets])

defs = Definitions(
    # assets=all_assets,
    assets=[
        check_sqs_for_new_records,
        upload_preprocessed_file,
        download_and_preprocess_file,
        update_dynamo_db_record,

    ],
    resources={
        "s3": s3_client_resource,
        "dynamodb": dynamodb_client_resource,
        "sqs": sqs_client_resource
    },
    jobs=[processing_job],
    schedules=[processing_schedule]
)
