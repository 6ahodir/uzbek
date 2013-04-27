import json
import logging
from uuid import uuid4

from datetime import datetime

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

from proverbs.models import Proverb, DEFAULT_GAME_TIME, DEFAULT_HINT_COUNT
from proverbs.models import get_or_create_fb_user
from proverbs import utils

logger = logging.getLogger(__name__)


@csrf_exempt
def index(request, template_name):
    """Index Page"""
    data = {}

    # todo change REQUEST to POST
    signed_request = request.REQUEST.get('signed_request')

    if not signed_request:
        return HttpResponseRedirect(
            reverse("proverbs:get_facebook_permissions")
        )

    try:
        fb_profile = utils.get_facebook_profile(signed_request)
    except Exception as e:
        logger.error(e)
        fb_profile = None

    if not fb_profile:
        return HttpResponseRedirect(
            reverse("proverbs:get_facebook_permissions")
        )

    data['fb_profile'] = fb_profile

    user = get_or_create_fb_user(fb_profile)
    if not user.is_active:
        # todo: show the user is inactive template
        raise Http404
    # hack to avoid authenticate
    # todo: change this
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    data['profile'] = user.userprofile

    proverbs = Proverb.objects.all()
    data['proverbs'] = proverbs

    # todo: generate a global top score list and show on the page
    # todo: generate a top score list among user's friends

    return render_to_response(template_name, data,
                              context_instance=RequestContext(request))


def _generate_question(request):
    data = {}

    proverb, suggestions = Proverb.get_next_for_user(request.user)

    uuid = str(uuid4())
    # todo: set expiration
    request.session['quiz-%s' % uuid] = (proverb, datetime.now())

    data['uuid'] = uuid
    data['description'] = proverb.description
    data['question'] = utils.construct_question(proverb.text)
    data['suggestions'] = suggestions

    return data


#@login_required
def quiz(request, template_name):
    """Start the quiz and show the first question"""
    data = {}

    data.update(_generate_question(request))

    data['next_url'] = reverse('proverbs:check_answer')
    data['hints'] = DEFAULT_HINT_COUNT
    data['time'] = DEFAULT_GAME_TIME
    return render_to_response(
        template_name,
        data,
        context_instance=RequestContext(request)
    )


def check_answer(request):
    data = {}

    if not request.is_ajax():
        raise Http404

    uuid = request.POST.get('uuid')
    answers = request.POST.getlist('answers[]', [])

    if not uuid:
        return HttpResponse('error: uuid')

    saved = request.session.get('quiz-%s' % uuid)
    if not saved:
        return HttpResponse('error: session')

    proverb, start = saved

    end = datetime.now()

    result = utils.check_answers(proverb.text, answers)

    if not result:
        return HttpResponse('wrong')

    # delete session
    del request.session['quiz-%s' % uuid]

    # calculate score

    data.update(_generate_question(request))
    data['answer'] = 'correct'

    # return a new question
    return HttpResponse(json.dumps(data),
                        mimetype='application/json')


def get_facebook_permissions(request, template_name):
    data = {}
    data['facebook'] = settings.FACEBOOK
    data['facebook_channel_url'] = request.build_absolute_uri(
        reverse('proverbs:facebook_channel')
    )
    return render_to_response(template_name, data)


def facebook_channel(request, template_name):
    return render_to_response(template_name)
