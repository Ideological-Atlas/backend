from django.db import models


class VisibleManagerMixin(models.Manager):
    @property
    def visible(self):
        return self.get_queryset().filter(visible=True)

    @property
    def not_visible(self):
        return self.get_queryset().filter(visible=False)
