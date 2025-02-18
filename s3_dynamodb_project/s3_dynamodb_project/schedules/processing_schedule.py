from dagster import ScheduleDefinition
from s3_dynamodb_project.jobs.processing_job import processing_job


processing_schedule = ScheduleDefinition(
    job=processing_job,
    cron_schedule="*/5 * * * *"
)
