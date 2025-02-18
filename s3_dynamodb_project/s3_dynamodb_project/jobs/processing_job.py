from dagster import define_asset_job, AssetSelection
from s3_dynamodb_project.assets import s3_assets


processing_job = define_asset_job(
    name="processing_job",
    selection=AssetSelection.keys(
        "check_sqs_for_new_records",
        "download_and_preprocess_file",
        "upload_preprocessed_file",
        "update_dynamo_db_record"
    )
)
