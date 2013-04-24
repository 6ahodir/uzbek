from django.http import Http404, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

from proverbs.models import Proverb
from proverbs import utils


@csrf_exempt
def index(request, template_name):
    """Index Page"""
    data = {}

    # todo change REQUEST to POST
    signed_request = request.REQUEST.get('signed_request')
    if not signed_request:
        return HttpResponse('No signed request')
        raise Http404

    fb_profile = utils.get_facebook_profile(signed_request)

    if not fb_profile:
        return HttpResponse('No profile')
        raise Http404

    data['fb_profile'] = fb_profile

    proverbs = Proverb.objects.all()
    data['proverbs'] = proverbs

    return render_to_response(template_name, data,
                              context_instance=RequestContext(request))
