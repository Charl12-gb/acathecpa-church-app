from rest_framework.routers import SimpleRouter

from .views import TeamMemberViewSet

router = SimpleRouter(trailing_slash="/?")
router.register("", TeamMemberViewSet, basename="team-member")

urlpatterns = router.urls
