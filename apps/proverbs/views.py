import json
import logging
from uuid import uuid4

from datetime import datetime, timedelta

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
    """Index Page
    When the access_token, expires, and uid are set, then the user is coming
    to the page second time, so we'll just redirect the user to the quiz page
    if we can get the graph"""
    data = {}

    # todo change REQUEST to POST
    signed_request = request.REQUEST.get('signed_request')
    access_token = request.REQUEST.get('access_token')
    expires = request.REQUEST.get('expires')
    uid = request.REQUEST.get('uid')
    if not signed_request and not (access_token and expires and uid):
        raise Http404

    if access_token:
        user_data = {
            'access_token': access_token,
            'expires': expires,
            'uid': uid
        }
        fb_graph = utils.get_facebook_graph(user_data=user_data)
    else:
        fb_graph = utils.get_facebook_graph(signed_request)

    if not fb_graph:
        raise Http404

    fb_profile = utils.get_facebook_profile(graph=fb_graph)
    if fb_profile:
        data['fb_profile'] = fb_profile

        user = get_or_create_fb_user(fb_profile)
        if not user.is_active:
            return HttpResponseRedirect(reverse('proverbs:account_disabled'))

        # hack to avoid authenticate
        # todo: change this
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        data['profile'] = user.userprofile

    data['top_scorers'] = _get_top_scorers(count=10)
    data['facebook'] = settings.FACEBOOK

    # todo: generate a top score list among user's friends

    if access_token:
        return HttpResponseRedirect(reverse('proverbs:quiz'))

    return render_to_response(template_name, data,
                              context_instance=RequestContext(request))


@login_required
def quiz(request, template_name):
    """Start the quiz and show the first question"""
    data = {}

    exclude = []
    question, proverb = utils.generate_question(request, exclude)
    data.update(question)

    exclude.append(proverb.id)

    uuid = str(uuid4())

    data['uuid'] = uuid
    data['check_url'] = reverse('proverbs:check_answer')
    data['next_url'] = reverse('proverbs:next_question')
    data['save_score_url'] = reverse('proverbs:save_quiz_score')
    data['hints'] = DEFAULT_HINT_COUNT
    data['time'] = request.user.userprofile.game_time
    data['number'] = 1  # the number of the question

    start = datetime.now()
    time_left = timedelta(0, data['time'] * 60)
    # todo: set expiration
    # proverb, start time, result (initally wrong)
    request.session['quiz-%s' % uuid] = {
        'proverb': proverb,
        'start': start,  # start will change with each next question
        'time_left': time_left,
        'hints': DEFAULT_HINT_COUNT,
        'time': data['time'],
        'number': data['number'],
        'score': 0,  # in the beginning the user's score is 0
        'exclude': exclude,  # showed proverb ids
        # save the score only if there are no more questions to show
        'is_score_saved': False
    }

    return render_to_response(
        template_name,
        data,
        context_instance=RequestContext(request)
    )


@login_required
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

    time_passed = datetime.now() - session_quiz['start']
    session_quiz['time_left'] -= time_passed

    # calculate score
    score = ScoreList.calculate_score(time_passed.seconds)
    session_quiz['score'] += score

    request.session.modified = True

    data = {
        'answer': 'correct',
        'score': score
    }
    return HttpResponse(json.dumps(data),
                        mimetype='application/json')


@login_required
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

    # has the quiz end time reached?
    if session_quiz['time_left'].seconds <= 0:
        return HttpResponse('expired')

    question_data = utils.generate_question(
        request, session_quiz['exclude'])

    if not question_data:
        return HttpResponse('no more')

    question, proverb = question_data
    data.update(question)

    session_quiz['proverb'] = proverb
    session_quiz['exclude'].append(proverb.id)
    session_quiz['start'] = datetime.now()
    session_quiz['number'] += 1
    request.session.modified = True

    data['number'] = session_quiz['number']
    data['success'] = True

    # return a new question
    return HttpResponse(json.dumps(data),
                        mimetype='application/json')


@login_required
def save_quiz_score(request):
    """Calculates the user's final score and saves as top score.
    Returns a list of top scorers and the user's score if not in that list
    This is the last step of a quiz. This function must get called when
    the time expires or there is no more questions to show.
    """
    if not request.is_ajax():
        raise Http404

    uuid = request.GET.get('uuid')
    if not uuid:
        return HttpResponse('error: uuid')

    session_quiz = request.session.get('quiz-%s' % uuid)
    if not session_quiz:
        return HttpResponse('error: session')

    # only save if there are no more questions to show
    if session_quiz['is_score_saved']:
        return HttpResponse('error: already saved')
    else:
        session_quiz['is_score_saved'] = True
        request.session.modified = True

    user_score, created = ScoreList.objects.get_or_create(
        user=request.user)
    if session_quiz['score'] > user_score.score:
        user_score.score = session_quiz['score']
        user_score.save()

    top_scorers = _get_top_scorers(user_score)
    return HttpResponse(json.dumps({
        'top_scorers': top_scorers,
        'success': True
    }), mimetype='application/json')


def _get_top_scorers(user_score=None, count=10):
    """returns a list of top scorers (10) along with their rankings +
    user_score and its ranking if not in those 10
    """

    top_score_list = ScoreList.objects.filter(
        score__gt=0, user__userprofile__publish_score=True
    ).order_by('-score')[:count]

    top_scorers = []
    for rank, top_score in enumerate(top_score_list):
        top_scorers.append({
            'name': top_score.user.userprofile.get_name(),
            'photo_url': top_score.user.userprofile.get_photo(),
            'score': top_score.score,
            'rank': rank + 1,
            'current_user': True if user_score and
            user_score.user == top_score.user else False
        })

    if user_score and user_score not in top_score_list:
        top_scorers.append({
            'id': user_score.user.id,
            'name': user_score.user.userprofile.get_name(),
            'photo_url': user_score.user.userprofile.get_photo(),
            'score': user_score.score,
            'rank': ScoreList.objects.filter(
                score__gt=user_score.score).count() + 1,
            'current_user': True
        })
    return top_scorers


def facebook_channel(request, template_name):
    return render_to_response(template_name)


def account_disabled(request, template_name):
    """Show a template with the admin's email"""
    data = {}
    try:
        admin = settings.ADMINS[0]
    except:
        admin = None
    data['admin'] = admin
    return render_to_response(template_name, data)
