from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


class IsSelfOrStaff(permissions.BasePermission):
    """
    Custom permission to allow users to act only on themselves,
    unless they are staff.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.id == request.user.id


class AccountViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing user accounts.

    Available endpoints:
    - GET    /accounts/           → List all user accounts (staff only)
    - GET    /accounts/{id}/      → Retrieve a specific user by ID
    - POST   /accounts/           → Create a user (email must match JWT)
    - PUT    /accounts/{id}/      → Update all fields of the current user
    - PATCH  /accounts/{id}/      → Partially update the current user
    - DELETE /accounts/{id}/      → Delete the current user
    - GET    /accounts/me/        → Get the current authenticated user's profile
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelfOrStaff]

    def get_queryset(self):
        """Staff users can see all; regular users only see themselves."""
        user = self.request.user
        return User.objects.all() if user.is_staff else User.objects.filter(id=user.id)

    def perform_create(self, serializer):
        """Allow users to create only their own account (email match)."""
        user = self.request.user
        email = serializer.validated_data.get("email")

        if not user.is_staff and email != user.email:
            raise PermissionDenied(
                "You can only create an account with your own email."
            )

        serializer.save()

    def perform_update(self, serializer):
        """Allow users to edit only their own account."""
        if not self.request.user.is_staff and serializer.instance != self.request.user:
            raise PermissionDenied("You can only edit your own account.")
        serializer.save()

    def perform_destroy(self, instance):
        """Allow users to delete only their own account."""
        if not self.request.user.is_staff and instance != self.request.user:
            raise PermissionDenied("You can only delete your own account.")
        instance.delete()

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """Return the current authenticated user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
