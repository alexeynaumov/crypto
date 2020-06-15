import hashlib
import datetime
import requests
from base64 import b64encode
from bs4 import BeautifulSoup
from django.forms import model_to_dict

import main.models as models


ARTICLES_PER_PAGE = 5  # number of articles per page


def clean(raw_text):
    """
    Strip html tags from input raw_string.
    :param raw_text: Raw text
    :return: str, html tags free string
    """

    if not raw_text:
        return ""

    clean_text = BeautifulSoup(raw_text, "lxml").text

    return clean_text


def get_pagination_meta(query_id, page_id):
    """
    Based on the <query_id> and <page_id> make meta info containing of the number of previous, current and next pages to
    facilitate pagination. The data is used as 'context_data' to facilitate template rendering.
    :param query_id: query id
    :param page_id: page number
    :return: dict, pagination info
    """

    current_page = int(page_id)
    total_pages = models.Query.objects.get(id=query_id).total_pages
    pages = list(range(1, total_pages + 1))  # list of pages

    try:
        previous_page = pages[:current_page - 1][-3]
    except IndexError:
        previous_page = 0

    previous_pages = pages[:current_page - 1][-2:]
    next_pages = pages[current_page:][:2]

    try:
        next_page = pages[current_page:][3]
    except IndexError:
        next_page = 0

    # PAGINATOR:
    # PREVIOUS, 2 previous pages, current page, 2 next pages, NEXT
    meta = {
        "query_id": query_id,
        "page_id": page_id,
        "previous_page": previous_page,  # the very previous page, 0 if doesnt exist
        "previous_pages": previous_pages,  # 2 previous pages, [] if do not exist
        "current_page": current_page,
        "next_pages": next_pages,  # 2 next pages, [] if do not exist
        "next_page": next_page  # the very next page, 0 if does nto exist
    }

    return meta


def fetch_page(page, **kwargs):
    """
    Fetch one page of articles with number <page> from the API server.
    :param page: page number to fetch
    :param kwargs:
    :return: dict, API server response
    """

    # API_KEY = "e54b269c40db43e18d210f2a81ebb272"
    # API_KEY = "0d28ed0074924b35a94aefe3616c4a64"

    API_KEY = models.APIKey.objects.all().first()
    URL = "http://newsapi.org/v2/everything"

    query = f"{URL}"
    query += f"?q={kwargs.get('query')}"

    sources = kwargs.get("sources")
    if sources:
        query += f"&sources={sources}"

    domains = kwargs.get("domains")
    if domains:
        query += f"&domains={domains}"

    from_date = kwargs.get("from_date")
    if from_date:
        query += f"&from={str(from_date)}"

    to_date = kwargs.get("to_date")
    if to_date:
        query += f"&to={str(to_date)}"

    language = kwargs.get("language")
    if language:
        query += f"&language={language}"

    sort_by = kwargs.get("sort_by")
    if sort_by:
        query += f"&sortBy={sort_by}"

    query += f"&page={page}"
    query += f"&pageSize={ARTICLES_PER_PAGE}"
    query += f"&apiKey={API_KEY}"

    response = requests.get(query).json()

    return response


def load(query_id, page_id):
    """
    Fetch page of data <page_id>, associate it with the query <query_id>, clean the page and save it in the database.
    :param query_id: query id
    :param page_id: page number
    :return: None
    """

    query = models.Query.objects.get(id=query_id)

    page = fetch_page(page=page_id, **model_to_dict(query))

    articles = page.get("articles", [])
    for article in articles:
        source = article.get("source", None)
        if source:
            name = source.get("name", None)

        published_at = article.get("publishedAt", None)
        if published_at:
            published_at = datetime.datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")

        author = article.get("author", None)
        if author:
            all_authors = author.split(",")
            if len(all_authors) > 3:
                author = ", ".join(all_authors[:3])
                author += " et al"
        else:
            author = "Anonymous"

        query = models.Query.objects.get(id=query_id)
        models.Article.objects.create(
            query=query,
            page=page_id,
            source=name,
            author=author,
            title=clean(article.get("title", "")),
            description=clean(article.get("description", "")),
            url=article.get("url", ""),
            published_at=published_at,
            content=clean(article.get("content", ""))
        )

    total_results = page.get("totalResults", 0)
    total_pages = total_results // ARTICLES_PER_PAGE  # total number of pages
    if total_results % ARTICLES_PER_PAGE:
        total_pages += 1

    query.total_pages = total_pages
    query.save()


def get_query_hash(**kwargs):
    """
    Return query hash. Same queries must have same hash.
    :param kwargs: keyword args, similar to those in fetch_page function
    :return: str, hash
    """

    URL = "http://newsapi.org/v2/everything"

    query = f"{URL}"
    query += f"?q={kwargs.get('query')}"

    sources = kwargs.get("sources")
    if sources:
        query += f"&sources={sources}"

    domains = kwargs.get("domains")
    if domains:
        query += f"&domains={domains}"

    from_date = kwargs.get("from_date")
    if from_date:
        query += f"&from={str(from_date)}"

    to_date = kwargs.get("to_date")
    if to_date:
        query += f"&to={str(to_date)}"

    language = kwargs.get("language")
    if language:
        query += f"&language={language}"

    sort_by = kwargs.get("sort_by")
    if sort_by:
        query += f"&sortBy={sort_by}"

    query = str(query).encode()
    query = b64encode(query)
    query_hash = hashlib.md5(query)
    query_hash = query_hash.hexdigest()

    return query_hash
