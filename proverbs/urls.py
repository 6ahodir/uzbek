from django.conf.urls import patterns, url

from proverbs import views

urlpatterns = patterns(
    '',
    url(r'', views.index, {'template_name': 'index.html'}, name='index')
)
