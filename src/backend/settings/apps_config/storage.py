import sys
from typing import Any

from ..base import PRODUCTION, env

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="admin")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="change_me")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="media")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")

AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="http://minio:9000")

AWS_S3_PUBLIC_DOMAIN = env("AWS_S3_PUBLIC_DOMAIN", default=None)

if AWS_S3_PUBLIC_DOMAIN:
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_S3_PUBLIC_DOMAIN}/{AWS_STORAGE_BUCKET_NAME}"
else:
    AWS_S3_CUSTOM_DOMAIN = ""

AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False

if not PRODUCTION:
    AWS_S3_URL_PROTOCOL = "http:"

STORAGES: dict[str, Any] = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

if "test" in sys.argv:
    STORAGES["default"] = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {"location": "/tmp/test_media"},  # nosec
    }
