from config.routers import OptionalSlashRouter

from .views import ContentViewSet

router = OptionalSlashRouter()
router.register("", ContentViewSet, basename="content")

urlpatterns = router.urls
