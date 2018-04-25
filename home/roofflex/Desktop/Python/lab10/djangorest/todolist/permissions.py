from rest_framework.permissions import BasePermission
from .models import Tasklist, Task

class IsOwner(BasePermission):
    """Custom permission class to allow only bucketlist owners to edit them."""

    def has_object_permission(self, request, view, obj):
        """Return True if permission is granted to the bucketlist owner."""
        if isinstance(obj, Tasklist) or isinstance(obj, Task):
            return obj.owner == request.user
        return obj.owner == request.user

