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

from proverbs.models import Proverb, ProverbScore, ScoreList
from proverbs.models import DEFAULT_HINT_COUNT
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


#@login_required
def quiz(request, template_name):
    """Start the quiz and show the first question"""
    data = {}

    exclude = []
    question, proverb = utils.generate_question(request, exclude)
    data.update(question)

    uuid = str(uuid4())

    data['uuid'] = uuid
    data['check_url'] = reverse('proverbs:check_answer')
    data['next_url'] = reverse('proverbs:next_question')
    data['hints'] = DEFAULT_HINT_COUNT
    data['time'] = request.user.userprofile.game_time
    data['number'] = 1  # the number of the question

    # todo: set expiration
    # proverb, start time, result (initally wrong)
    request.session['quiz-%s' % uuid] = {
        'proverb': proverb,
        'start': datetime.now(),
        'hints': DEFAULT_HINT_COUNT,
        'time': data['time'],
        'number': data['number'],
        'score': 0,  # in the beginning the user's score is 0
        'exclude': exclude  # showed proverb ids
    }

    return render_to_response(
        template_name,
        data,
        context_instance=RequestContext(request)
    )


def check_answer(request):
    if not request.is_ajax():
        raise Http404

    uuid = request.POST.get('uuid')
    answers = request.POST.getlist('answers[]', [])

    if not uuid:
        return HttpResponse('error: uuid')

    session_quiz = request.session.get('quiz-%s' % uuid)
    if not session_quiz:
        return HttpResponse('error: session')

    #return HttpResponse(str(session_quiz['exclude']))
    answer = utils.check_answers(session_quiz['proverb'].text, answers)

    # increase the view count if not already done so
    proverb_score = session_quiz.get('proverb_score')
    if not proverb_score:
        proverb_score, created = ProverbScore.objects.get_or_create(
            proverb=session_quiz['proverb'], user=request.user)
        proverb_score.view_count += 1
        proverb_score.save()
        session_quiz['proverb_score'] = proverb_score
        request.session.modified = True

    if not answer:
        return HttpResponse('wrong')

    # save proverb result
    if proverb_score:
        del session_quiz['proverb_score']
        proverb_score.correct_count += 1
        proverb_score.save()

    # calculate score
    score = ScoreList.calculate_score(
        (datetime.now() - session_quiz['start']).seconds
    )
    session_quiz['score'] += score

    request.session.modified = True

    data = {
        'answer': 'correct',
        'score': score
    }
    return HttpResponse(json.dumps(data),
                        mimetype='application/json')


def next_question(request):
    if not request.is_ajax():
        raise Http404

    uuid = request.GET.get('uuid')
    if not uuid:
        return HttpResponse('error: uuid')

    session_quiz = request.session.get('quiz-%s' % uuid)
    if not session_quiz:
        return HttpResponse('error: session')

    data = {}

    session_quiz['exclude'].append(session_quiz['proverb'].id)
    session_quiz['number'] += 1
    request.session.modified = True

    question_data = utils.generate_question(
        request, session_quiz['exclude'])

    if not question_data:
        return HttpResponse('no more')

    question, proverb = question_data
    data.update(question)

    session_quiz['proverb'] = proverb
    session_quiz['start'] = datetime.now()
    request.session.modified = True

    data['number'] = session_quiz['number']
    data['success'] = True

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
