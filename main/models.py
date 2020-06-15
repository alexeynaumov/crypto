from django.db import models
from django.forms import model_to_dict

from main.utils import get_query_hash


class Query(models.Model):
    hash = models.CharField(max_length=64, blank=True, null=True)  # query hash, same queries have same hash
    query = models.CharField(max_length=128)  # query string
    sources = models.CharField(max_length=128, blank=True, null=True)
    domains = models.CharField(max_length=128, blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    language = models.CharField(max_length=32, blank=True, null=True)
    sorting = models.CharField(max_length=32, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    total_pages = models.IntegerField(blank=True, null=True)  # total number of response pages in query

    class Meta:
        verbose_name_plural = "Queries"

    def __str__(self):
        return f"{str(self.timestamp.strftime('%Y-%m-%d %H:%M:%S'))}: {self.query}"

    def save(self, *args, **kwargs):
        self.hash = get_query_hash(**model_to_dict(self))

        super().save(*args, **kwargs)


class Article(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE, blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)  # response page of article
    source = models.CharField(max_length=256, blank=True, null=True)
    author = models.CharField(max_length=256, blank=True, null=True)
    title = models.CharField(max_length=1024, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    published_at = models.DateField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{str(self.author).upper()}: {str(self.title)[:32]}"


class APIKey(models.Model):
    key = models.CharField(max_length=128)

    def __str__(self):
        return self.key
