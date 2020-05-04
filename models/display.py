from django.db import models

class ModelDisplay(models.Model):
    display = models.CharField(blank=True, max_length=255, null=True)
    FORCE_UPDATE_DISPLAY = False
    SHOW_DISPLAY_IN_URL = True

    class Meta:
        abstract = True

    def set_display(self):
        if self.FORCE_UPDATE_DISPLAY or self.display is None):
            self.display = str(self)

    def clean(self):
        self.set_display()
        super().clean()