import logging
import uuid

from django.db import models
from model_utils import models as model_utils_models

logger = logging.getLogger(__name__)


class UUIDModel(models.Model):
    uuid = models.UUIDField(
        db_index=True, default=uuid.uuid4, editable=False, unique=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        if hasattr(self, "id"):
            if hasattr(self, "name"):
                return f"{self.id}-{self.name}"
            return f"{self.id}-{self.uuid.hex}"
        return str(self.uuid)


class TimeStampedUUIDModel(UUIDModel, model_utils_models.TimeStampedModel):

    class Meta:
        abstract = True
