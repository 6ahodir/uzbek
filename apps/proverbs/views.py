from django.shortcuts import render_to_response

from proverbs.models import Proverb


def index(request, template_name):
    data = {}

    return render_to_response(template_name, data)
