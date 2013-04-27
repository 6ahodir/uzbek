import logging
from string import punctuation
from sys import exc_info

from django.conf import settings

from facebook_sdk import facebook as fb

logger = logging.getLogger(__name__)


def construct_question(text):
    """Transform text into a question, where each word's case is output.
    If the text reads "I went home, but no one was there.",
    the transformed text will look like so:
    ['u', 'l', 'l', ',', 'l', 'l', 'l', 'l', 'l', '.'],
    where 'u' stands for 'upper case', and 'l' stands for lowercase.
    Note that the punctuation mars are also in the list.
    """

    # add space before and after punctuataion marks so that we can split them
    spaced_punctuation = [' ' + x + ' ' for x in punctuation]
    text = text.translate(
        dict((ord(x), y) for (x, y) in zip(punctuation, spaced_punctuation))
    )

    result = []
    for word in text.split():
        if word in punctuation:
            result.append(word)
        elif word[0].isupper():
            result.append('u')
        else:
            result.append('l')

    return result


def check_answers(text, answers):
    """Splits the text and compares words to the words in the answer list"""

    # add space before and after punctuataion marks so that we can split them
    spaced_punctuation = [' ' + x + ' ' for x in punctuation]
    text = text.translate(
        dict((ord(x), y) for (x, y) in zip(punctuation, spaced_punctuation))
    )

    words = [x.lower() for x in text.split() if x not in punctuation]

    if not len(words) == len(answers):
        return False

    result = True
    for word, answer in zip(words, answers):
        if not word == answer:
            result = False
            break

    return result


def get_facebook_graph(signed_request):
    """Get facebook graph object from the signed_request"""
    try:
        facebook = fb.Facebook(
            {'signed_request': signed_request},
            settings.FACEBOOK['APP_ID'],
            settings.FACEBOOK['APP_SECRET']
        )
        #session = facebook.getSession()
        graph = facebook.getGraph()
    except Exception as e:
        logger.error(e, exc_info=exc_info())
        print(e)
        graph = None

    return graph


def get_facebook_profile(signed_request):
    """Get the user's profile from the signed_request"""
    graph = get_facebook_graph(signed_request)

    if not graph:
        return None

    try:
        profile = graph.get_object("me")
    except fb.GraphAPIError:
        profile = None

    return profile
