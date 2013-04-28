from django.contrib import admin
from proverbs.models import Proverb, ProverbScore, SuggestionWord, UserProfile

admin.site.register(Proverb)
admin.site.register(ProverbScore)
admin.site.register(SuggestionWord)
admin.site.register(UserProfile)
