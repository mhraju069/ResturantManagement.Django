from rest_framework import permissions


class IsBusinessOwner(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'business_owner')
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if hasattr(obj, 'user'):
            return obj.user.role == 'business_owner' and obj.user == request.user
        
            
        return False