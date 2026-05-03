from rest_framework.routers import SimpleRouter

from .views import (
    PermissionViewSet,
    RolePermissionViewSet,
    RoleViewSet,
    UserPermissionViewSet,
)

router = SimpleRouter(trailing_slash="/?")
router.register("roles", RoleViewSet, basename="role")
router.register("permissions", PermissionViewSet, basename="permission")
router.register("role-permissions", RolePermissionViewSet, basename="role-permission")
router.register("user-permissions", UserPermissionViewSet, basename="user-permission")

urlpatterns = router.urls
