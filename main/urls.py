from django.urls import path
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from crypto import settings
from . import views

app_name = "main"

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

urlpatterns = [
    path("", views.QueryCreateView.as_view(), name="query-create"),
    path("queries/<int:query_id>/articles/pages/<int:page_id>/", cache_page(CACHE_TTL)(views.ArticleListView.as_view()), name="article-list"),
    path("articles/void/", views.ArticleVoidView.as_view(), name="article-void")
]
