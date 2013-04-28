from django.conf.urls import patterns, url

from proverbs import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, {'template_name': 'index.html'}, name='index'),
    url(r'^quiz/$', views.quiz, {'template_name': 'quiz.html'}, name='quiz'),
    url(r'^check-answer/$', views.check_answer, {}, name='check_answer'),
    url(r'^next-question/$', views.next_question, {}, name='next_question'),

    url(r'^get-facebook-permissions/$', views.get_facebook_permissions,
        {'template_name': 'get_facebook_permissions.html'},
        name='get_facebook_permissions'),
    url(r'^facebook-channel/$', views.facebook_channel,
        {'template_name': 'facebook_channel.html'},
        name='facebook_channel'),
)
