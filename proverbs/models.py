from django.db import models


class Proverb(models.Model):
    text = models.CharField(max_length=255)
    description = models.TextField()

    def __unicode__(self):
        return self.text
