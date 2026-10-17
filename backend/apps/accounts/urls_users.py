from config.routers import OptionalSlashRouter

from .views_users import UserViewSet

router = OptionalSlashRouter()
router.register("", UserViewSet, basename="user")

urlpatterns = router.urls
