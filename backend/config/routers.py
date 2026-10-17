"""Router accepting URLs with or without a trailing slash."""
from rest_framework.routers import SimpleRouter


class OptionalSlashRouter(SimpleRouter):
    # Recent DRF versions coerce any truthy `trailing_slash` argument to "/",
    # so `SimpleRouter(trailing_slash="/?")` no longer matches `/courses/1`.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = "/?"
