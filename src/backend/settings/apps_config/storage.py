from ..base import env

AWS_ACCESS_KEY_ID = env.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = env.get("AWS_S3_ENDPOINT_URL")
AWS_S3_REGION_NAME = env.get("AWS_S3_REGION_NAME", "us-east-1")
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
