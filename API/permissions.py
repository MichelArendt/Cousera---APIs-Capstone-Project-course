from rest_framework.permissions import AllowAny, BasePermission

# def is_user_on_group(user, group):
#         return user and user.groups.filter(name=group).exists()

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Manager').exists()

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Delivery Crew').exists()

class DenyAllPermission(BasePermission):
    def has_permission(self, request, view):
        return False

# # class BasePermissionMixin:
# #     """
# #     Mixin to apply custom permissions based on the request method.
# #     Only allows POST, PUT, PATCH and DELETE for specified user groups, and allows all users to make GET requests.
# #     """
# #     def __init__(self, permission_class=None):
# #         self.permission_class = permission_class or AllowAny # Default to AllowAny if not provided

# #     def get_permissions(self):
# #         if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
# #             return [self.permission_class()]  # Use the provided permission class
# #         return [AllowAny()]  # Allows any user, authenticated or not, to make GET requests

# # class ManagerPermissionMixin(BasePermissionMixin):
# #     """
# #     Only allows POST, PUT, PATCH and DELETE for Manager users, and allows all users to make GET requests.
# #     """
# #     def __init__(self):
# #         super().__init__(permission_class=IsManager) # Pass the IsManager permission class to the base mixin

# #     def get_permissions(self):
# #         return super().get_permissions()

# # class DeliveryCrewPermissionMixin:
# #     """
# #     Only allows POST, PUT, PATCH and DELETE for Delivery Crew users, and allows all users to make GET requests.
# #     """
# #     def __init__(self):
# #         super().__init__(permission_class=IsDeliveryCrew)

# #     def get_permissions(self):
# #         return super().get_permissions()


# class Permission:
#     """
#     Mixin to apply custom permissions based on the request method.
#     Only allows POST, PUT, PATCH and DELETE for specified user groups, and allows all users to make GET requests.
#     """
#     def __init__(self, permission_class=None, methods=[]):
#         self.permission_class = permission_class or AllowAny # Default to AllowAny if not provided
#         self.methods = methods or ['GET']

#     def get_permissions(self):
#         if self.request.method in self.methods:
#             return [self.permission_class()]  # Use the provided permission class
#         return [AllowAny()]  # Allows any user, authenticated or not, to make GET requests