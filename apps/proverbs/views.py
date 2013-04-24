from datetime import datetime

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

from proverbs.models import Proverb
from proverbs.models import get_or_create_fb_user
from proverbs import utils


@csrf_exempt
def index(request, template_name):
    """Index Page"""
    data = {}

    # todo change REQUEST to POST
    signed_request = request.REQUEST.get('signed_request')
    if not signed_request:
        raise Http404

    fb_profile = utils.get_facebook_profile(signed_request)

    if not fb_profile:
        raise Http404

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

    proverb, suggestions = Proverb.get_next_for_user(request.user)

    request.session['proverb'] = proverb

    data['question'] = utils.construct_question(proverb.text)
    data['suggestions'] = suggestions
    data['start'] = datetime.now()
    return render_to_response(template_name, data,
                              context_instance=RequestContext(request))
