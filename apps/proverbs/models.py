from random import randrange
from string import punctuation

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

    def __str__(self):
        return '%s' % self.text

    @classmethod
    def get_next_for_user(self, user):
        """Get the next proverb for the user"""
        proverbs = Proverb.objects.filter(ProverbScore=None)
        count = proverbs.count()
        if count:
            # get random, order_by('?') is slow
            random_index = randrange(count - 1)
            return proverbs[random_index]
        else:
            return ProverbScore.get_lowest_score_for_user(user)


class SuggestionWord(models.Model):
    """Words used as suggestion to a given question.
    These words are unique and taken from Proverb.text and Proverb.description
    and converted to lowercase
    """
    word = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.word


@receiver(models.signals.post_save, sender=Proverb)
def add_new_suggestion_words(sender, instance, created, **kwargs):
    """Add new words when a new proverb is created
    """
    if created:
        words = set()
        words.update(
            [x.lower().strip(punctuation) for x in instance.text.split()]
        )
        words.update(
            [x.lower().strip(punctuation)
             for x in instance.description.split()]
        )
        # there is no bulk get_or_create method yet
        for word in words:
            word, created = SuggestionWord.objects.get_or_create(word=word)


class ProverbScore(models.Model):
    proverb = models.ForeignKey(Proverb)
    user = models.ForeignKey(User)
    # how many times has the user seen this proverb
    view_count = models.PositiveIntegerField()
    # how many times has the user answered correctly to this proverb
    correct_count = models.PositiveIntegerField()

    def __str__(self):
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

    def __str__(self):
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
    game_time = models.PositiveSmallIntegerField(choices=GAME_TIME_CHOICES,
                                                 default=DEFAULT_GAME_TIME)


@receiver(models.signals.post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created
    """
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)
