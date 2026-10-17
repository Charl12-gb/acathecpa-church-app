from config.routers import OptionalSlashRouter

from .views import TeamMemberViewSet

router = OptionalSlashRouter()
router.register("", TeamMemberViewSet, basename="team-member")

urlpatterns = router.urls
