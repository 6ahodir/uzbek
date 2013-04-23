from django.shortcuts import render_to_response
from django.http import Http404

from proverbs.models import Proverb
from proverbs import utils


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

    proverbs = Proverb.objects.all()
    data['proverbs'] = proverbs

    return render_to_response(template_name, data)
