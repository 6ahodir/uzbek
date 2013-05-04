from django.conf.urls import patterns, url

from proverbs import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, {'template_name': 'index.html'}, name='index'),
    url(r'^quiz/$', views.quiz, {'template_name': 'quiz.html'}, name='quiz'),
    url(r'^check-answer/$', views.check_answer, {}, name='check_answer'),
    url(r'^next-question/$', views.next_question, {}, name='next_question'),
    url(r'^save-quiz-score/$', views.save_quiz_score, {},
        name='save_quiz_score'),

    url(r'^account-disabled/$', views.account_disabled,
        {'template_name': 'account_disabled.html'}, name='save_quiz_score'),

    url(r'^facebook-channel/$', views.facebook_channel,
        {'template_name': 'facebook_channel.html'},
        name='facebook_channel'),
)
