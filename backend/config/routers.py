"""Router accepting URLs with or without a trailing slash."""
from django.urls import re_path
from rest_framework.routers import SimpleRouter


class OptionalSlashRouter(SimpleRouter):
    # Recent DRF versions coerce any truthy `trailing_slash` argument to "/",
    # so `SimpleRouter(trailing_slash="/?")` no longer matches `/courses/1`.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = "/?"

    def get_urls(self):
        # With an empty prefix (router included under "contents/", "users/"…)
        # DRF strips the leading "^/" of the list route, which turns "^/?$"
        # into the invalid regex "^?$". The include already consumed the slash.
        urls = []
        for url in super().get_urls():
            regex = str(url.pattern)  # raw string: compiling it would fail
            if regex.startswith("^?"):
                url = re_path("^" + regex[2:], url.callback, name=url.name)
            urls.append(url)
        return urls
