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


def get_facebook_graph(signed_request):
    """Get facebook graph object from the signed_request"""
    try:
        facebook = fb.Facebook(
            {'signed_request': signed_request},
            settings.FACEBOOK['APP_ID'],
            settings.FACEBOOK['APP_SECRET']
        )
        session = facebook.getSession()
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
