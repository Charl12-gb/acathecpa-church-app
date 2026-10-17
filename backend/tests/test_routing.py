"""Every API route must compile and the list endpoints must answer, with or without a trailing slash."""
import pytest
from django.urls import URLPattern, URLResolver, get_resolver
from rest_framework.test import APIClient


def _walk(patterns):
    for p in patterns:
        if isinstance(p, URLResolver):
            yield p
            yield from _walk(p.url_patterns)
        elif isinstance(p, URLPattern):
            yield p


def test_all_url_patterns_compile():
    for p in _walk(get_resolver().url_patterns):
        p.pattern.regex  # raises re.error on an invalid pattern


@pytest.mark.parametrize("url", [
    # contents/ and team/ are mounted with an include, so they need the slash.
    "/api/v1/contents/", "/api/v1/team/",
    "/api/v1/courses/", "/api/v1/courses",
    "/api/v1/categories/", "/api/v1/categories",
])
def test_public_list_endpoints_answer(db, url):
    assert APIClient().get(url).status_code == 200


def test_users_list_requires_login(db):
    # Used to crash with a regex error instead of answering 401.
    assert APIClient().get("/api/v1/users/").status_code == 401
