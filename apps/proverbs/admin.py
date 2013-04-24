from django.contrib import admin
from proverbs.models import Proverb, SuggestionWord, UserProfile

admin.site.register(Proverb)
admin.site.register(SuggestionWord)
admin.site.register(UserProfile)
