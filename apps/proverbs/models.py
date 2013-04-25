from math import ceil
from random import randrange, shuffle
from string import punctuation

from django.contrib.auth.models import User
from django.db import models#, transaction
from django.dispatch import receiver

# How long should a game last?
GAME_TIME_CHOICES = ((1, '1 min'), (3, '3 mins'), (5, '5 mins'))

# Default game will last 3 minutes, make sure this number is in the
# GAME_TIME_CHOICES tuple
DEFAULT_GAME_TIME = 3

# How many suggested words should we show?
SUGGESTIONS_COUNT = 20

# How many points does a user earn per correct answer?
SCORES = {
    10: 5,   # within 10 seconds is 5 points
    20: 4,  # within 20 seconds but more than 10 seconds is 4 points
    30: 3,  # within 30 seconds but more than 20 seconds is 3 points
    0: 1    # more than 30 seconds is 1 point
}

# How many hints does a user get?
DEFAULT_HINT_COUNT = 5

class Proverb(models.Model):
    text = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return '%s' % self.text

    @classmethod
    def get_next_for_user(cls, user):
        """Get the next proverb and possible answers for the user"""
        proverbs = Proverb.objects.filter(proverbscore=None)
        count = proverbs.count()
        if count:
            # get random, order_by('?') is slow
            random_index = randrange(count - 1)
            proverb = proverbs[random_index]
        else:
            proverb = ProverbScore.get_lowest_score_for_user(user)

        if not proverb:
            return None

        words = [x.lower().strip(punctuation) for x in proverb.text.split()]
        # each word will have two suggestions
        suggestion_words = SuggestionWord.objects.order_by(
            '?')[:SUGGESTIONS_COUNT - len(words)]
        suggestions = [x.word for x in suggestion_words]
        # add the correct answers too
        suggestions.extend(words)
        shuffle(suggestions)
        return (proverb, suggestions)


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

    @classmethod
    def get_score(cls, results):
        """Calculate a game's score
        results is a list of times in seconds a user took to answer the
        question correctly
        """
        score = 0
        for result in results:
            secs = ceil(result / 10)
            if secs in SCORES:
                points = SCORES[secs]
            else:
                points = SCORES[0]
            score += points
        return score


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

    def __str__(self):
        return '%s - %s' % (self.user.username, self.facebook_id)

    def save(self, *args, **kwargs):
        # get the facebook_id from the username, which may change later
        if not self.facebook_id:
            self.facebook_id = self.user.username
        super(UserProfile, self).save(*args, **kwargs)


@receiver(models.signals.post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created
    """
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)


def get_or_create_fb_user(fb_profile):
    """Get or create facebook user by facebook id"""
    try:
        user = User.objects.get(userprofile__facebook_id=fb_profile.get('id'))
    except User.DoesNotExist:
        user = User(
            # user name must be the facebook ID initailly,
            # once a UserProfile is created the username may be changed
            username=fb_profile.get('id'),
            first_name=fb_profile.get('first_name'),
            last_name=fb_profile.get('last_name'),
            email=fb_profile.get('email')
        )
        password = User.objects.make_random_password()
        user.set_password(password)
        user.save()

    return user
