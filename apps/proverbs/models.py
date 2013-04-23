from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver

# How long should a game last?
GAME_TIME_CHOICES = ((1, '1 min'), (3, '3 mins'), (5, '5 mins'))

# Default game will last 3 minutes, make sure this number is in the
# GAME_TIME_CHOICES tuple
DEFAULT_GAME_TIME = 3


class Proverb(models.Model):
    text = models.CharField(max_length=255)
    description = models.TextField()

    def __unicode__(self):
        return '%s' % self.text

    def get_next_for_user(self, user):
        """Get the next proverb for the user"""
        proverb = Proverb.objects.filter(ProverbScore=None).order_by('?')
        if proverb.count():
            return proverb.latest()
        else:
            return ProverbScore.get_lowest_score_for_user(user)


class ProverbScore(models.Model):
    proverb = models.ForeignKey(Proverb)
    user = models.ForeignKey(User)
    # how many times has the user seen this proverb
    view_count = models.PositiveIntegerField()
    # how many times has the user answered correctly to this proverb
    correct_count = models.PositiveIntegerField()

    def __unicode__(self):
        return '%s - %s - %d - %d' % (self.user.username, self.proverb[:20],
                                      self.view_count, self.correct_count)

    @classmethod
    def get_lowest_score_for_user(cls, user):
        """Get the proverb that has the lowest correct_count / view_count
        ratio
        """
        try:
            return cls.objects.extra(
                select={'score': 'correct_count / view_count'}
            ).filter(user=user).latest('-score')
        except cls.DoesNotExist:
            return None


class ScoreList(models.Model):
    """User's top score
    Scores are updated if a user's score is more than their top score.
    """
    user = models.OneToOneField(User)
    score = models.PositiveIntegerField()

    def __unicode__(self):
        return '%s - %d' % (self.user.username, self.score)


class UserProfile(models.Model):
    """User's site settings
    """
    user = models.OneToOneField(User)
    facebook_id = models.CharField(max_length=64)
    # used to show the user's facebook photo on the score board
    show_photo = models.BooleanField(default=True)
    # used to show the user's facebook name on the score board
    show_name = models.BooleanField(default=True)
    # used to show the user's score on the score board
    publish_score = models.BooleanField(default=True)
    # used to decide the game length for the user
    game_time = models.SmallPositiveIntegerField(choices=GAME_TIME_CHOICES,
                                                 default=DEFAULT_GAME_TIME)


@receiver(models.signals.post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created
    """
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)
