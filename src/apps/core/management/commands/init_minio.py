import json

import boto3
from botocore.client import Config
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Initialize MinIO bucket and policies"

    def handle(self, *args, **options):
        s3_url = getattr(settings, "AWS_S3_ENDPOINT_URL", None)
        access_key = getattr(settings, "AWS_ACCESS_KEY_ID", None)
        secret_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", None)
        bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "media")

        if not s3_url:
            self.stdout.write(self.style.WARNING("S3 Endpoint not configured."))
            return

        try:
            s3 = boto3.resource(
                "s3",
                endpoint_url=s3_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                config=Config(signature_version="s3v4"),
                region_name=getattr(settings, "AWS_S3_REGION_NAME", "us-east-1"),
            )

            bucket = s3.Bucket(bucket_name)

            if not bucket.creation_date:
                bucket.create()
                self.stdout.write(self.style.SUCCESS(f"Bucket {bucket_name} created."))

            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicRead",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
                    }
                ],
            }
            s3.BucketPolicy(bucket_name).put(Policy=json.dumps(policy))
            self.stdout.write(
                self.style.SUCCESS(f"Public policy applied to {bucket_name}.")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"MinIO Error: {e}"))
