from django.db import models


class IdeologyAbstractionComplexityManager(models.Manager):
    @property
    def visible(self):
        return self.filter(visible=True)

    @property
    def not_visible(self):
        return self.filter(visible=False)
