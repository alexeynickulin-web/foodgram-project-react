from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin to access.
    """

    def has_permission(self, request, view):
        return request.user.is_admin


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow admin or owner to access.
    """

    def has_object_permission(self, request, view, obj):
        return obj.username == request.user.username


class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and (
                request.user.is_admin
            )
        )
