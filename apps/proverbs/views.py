from django.shortcuts import render_to_response

from proverbs.models import Proverb


def index(request, template_name):
    """Index Page"""
    data = {}

    proverbs = Proverb.objects.all()
    data['proverbs'] = proverbs

    return render_to_response(template_name, data)
