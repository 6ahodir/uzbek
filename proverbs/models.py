from django.contrib.auth.models import User
from django.db import models


class Proverb(models.Model):
    text = models.CharField(max_length=255)
    description = models.TextField()

    def __unicode__(self):
        return self.text


class ProverbScore(models.Model):
    proverb = models.ForeignKey(Proverb)
    user = models.ForeignKey(User)
    # how many times has the user seen this proverb
    view_count = models.PositiveIntegerField()
    # how many times has the user answered correctly to this proverb
    correct_count = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s - %s - %d - %d" % (self.user.username, self.proverb[:20],
                                      self.view_count, self.correct_count)
