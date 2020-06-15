from django.urls import reverse
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import FormView, ListView, TemplateView

from .forms import QueryForm
from .models import Article, Query
from .utils import get_query_hash, load, get_pagination_meta


class QueryCreateView(FormView):
    template_name = "main/query_create.html"
    form_class = QueryForm

    def get_success_url(self):
        if not hasattr(self, "query_instance"):
            return reverse("main:article-void")  # or notify the user that there are none

        articles_found = self.query_instance.article_set.all().count()  # find out the number of articles the query has
        if articles_found > 0:  # if there are any
            kwargs = {
                "query_id": self.query_instance.id,
                "page_id": 1
            }

            return reverse("main:article-list", kwargs=kwargs)  # render the first page of articles

        return reverse("main:article-void")  # or notify the user that there are none

    def form_valid(self, form):
        query_hash = get_query_hash(**form.cleaned_data)  # calculate query hash
        try:
            query = Query.objects.get(hash=query_hash)  # get the query from the database if it exists
        except ObjectDoesNotExist:
            try:
                query = form.save()  # otherwise make a new one
                load(query_id=query.id, page_id=1)  # and load the first page of articles from the API server
            except Exception as error:
                query.delete()  # in case of failure, delete the freshly created query
                raise RuntimeError(error)

        self.query_instance = query  # save the instance of query for future

        return super().form_valid(form)


class ArticleListView(ListView):
    template_name = "main/article_list.html"

    def get_queryset(self):
        query_id = self.kwargs["query_id"]
        page_id = self.kwargs["page_id"]

        queryset = Article.objects.filter(query=query_id, page=page_id)  # from the database get page page_id of articles, associated with the query query_id
        if queryset.count() == 0:  # if there are none
            load(query_id, page_id)  # load the page from the API server
            queryset = Article.objects.filter(query=query_id, page=page_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        path = self.request.path.split("/")  # see urls.py
        query_id = path[2]
        page_id = path[5]

        meta = get_pagination_meta(query_id, page_id)  # get pagination info to facilitate rendering

        context["meta"] = meta

        return context


class ArticleVoidView(TemplateView):
    template_name = "main/article_void.html"


