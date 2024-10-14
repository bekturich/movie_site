from rest_framework import permissions
from rest_framework.permissions import BasePermission


class ProUserOrSimple(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if obj.status_movie == 'simple':
            return True
        if obj.status_movie == 'pro' and request.user.status == 'pro':
            return True
        return False