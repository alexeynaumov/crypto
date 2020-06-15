from django.contrib import admin

from main.models import Query, Article, APIKey

admin.site.register(Query)
admin.site.register(Article)
admin.site.register(APIKey)
