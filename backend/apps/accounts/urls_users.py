from rest_framework.routers import SimpleRouter

from .views_users import UserViewSet

router = SimpleRouter(trailing_slash="/?")
router.register("", UserViewSet, basename="user")

urlpatterns = router.urls
