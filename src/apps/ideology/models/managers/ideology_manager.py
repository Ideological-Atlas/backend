from core.models.managers import VisibleManagerMixin
from django.db import models


class IdeologyManager(VisibleManagerMixin, models.Manager):
    pass
