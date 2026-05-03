from rest_framework.routers import SimpleRouter

from .views import ContentViewSet

router = SimpleRouter(trailing_slash="/?")
router.register("", ContentViewSet, basename="content")

urlpatterns = router.urls
