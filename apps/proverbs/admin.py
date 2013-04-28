from django.contrib import admin
from proverbs.models import Proverb, ProverbScore, ScoreList,\
    SuggestionWord, UserProfile

admin.site.register(Proverb)
admin.site.register(ProverbScore)
admin.site.register(ScoreList)
admin.site.register(SuggestionWord)
admin.site.register(UserProfile)
