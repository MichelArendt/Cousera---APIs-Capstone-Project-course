from django.shortcuts import render
from django.contrib.auth.models import Group, User
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import filters
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status

from .models import MenuItem, Category, Cart, Order, OrderItem
from . import serializers
from .permissions import IsDeliveryCrew, IsManager, DenyAllPermission

class APIRootView(APIView):
    def get(self, request, format=None):
        return Response({
            # 'users': reverse('users-create', request=request, format=format),
            # 'users-display-current': reverse('users-display-current', request=request, format=format),
            'menu-categories': reverse('menu-categories-list-create', request=request, format=format),
            'menu-category-detail': reverse('menu-categories-detail', kwargs={'pk': 1}, request=request, format=format),
            'menu-items': reverse('menu-items-list-create', request=request, format=format),
            'menu-items-detail': reverse('menu-items-detail', kwargs={'pk': 1}, request=request, format=format),
            'groups': reverse('groups-list-create', request=request, format=format),
            'groups-detail': reverse('groups-detail', kwargs={'pk': 1}, request=request, format=format),
            'managers': reverse('managers-list', request=request, format=format),
            'managers-detail': reverse('managers-detail', kwargs={'pk': 2}, request=request, format=format),
            'delivery-crew': reverse('delivery-crew-list', request=request, format=format),
            'delivery-crew-detail': reverse('delivery-crew-detail', kwargs={'pk': 3}, request=request, format=format),
            'cart-menu-items': reverse('cart-menu-items', request=request, format=format),
            'orders': reverse('manage-orders', request=request, format=format),
            'manage-single-order': reverse('manage-single-order', kwargs={'pk': 3}, request=request, format=format),
        })

class BaseMenuCategoriesView():
    """
    Base view class for menu categories that handles common queryset and serializer.
    """
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

class ListCreateMenuCategories(BaseMenuCategoriesView, generics.ListCreateAPIView):
    """
    Handles listing and creating menu categories.
    """
    def get_permissions(self):
        if self.request.method in ['POST']:
            return [IsManager()]
        return [AllowAny()]

class ManageMenuCategory(BaseMenuCategoriesView, generics.RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating, and deleting a single menu category.
    """
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsManager()]
        return [AllowAny()]

class BaseMenuItemsView():
    """
    Base view class for menu categories that handles common queryset and serializer.
    """
    queryset = MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'price', 'featured', 'category__title']
    ordering_fields  = ['title', 'price', 'featured', 'category__title']

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset

# /api/menu-items - get and post
class ListCreateMenuItems(BaseMenuItemsView, generics.ListCreateAPIView):
    """
    Handles listing and creating menu items.
    """

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [IsManager()]
        return [AllowAny()]

# /api/menu-items/<int:pk> - get, put, patch and delete
class RetrieveUpdateDestroyMenuItems(BaseMenuItemsView, generics.RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating, and deleting a single menu item.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Item deleted successfully'}, status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsManager()]
        return [AllowAny()]

class BaseGroupsView():
    """
    Base view class for menu categories that handles common queryset and serializer.
    """
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer

    def get_permissions(self):
        return [IsManager()]

class ListCreateGroups(BaseGroupsView, generics.ListCreateAPIView):
    """
    Handles listing and creating groups.
    """

class RetrieveUpdateDestroyGroups(BaseGroupsView, generics.RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating, and deleting a single group.
    """

class BaseUsersView():
    """
    Base view class for menu categories that handles common queryset and serializer.
    """
    serializer_class = serializers.UserSerializer

class ListManagers(BaseUsersView, generics.ListCreateAPIView):
    """
    List all manager users
    """
    def post(self, request, *args, **kwargs):
        user_id = request.data['id']

        if not user_id:
            return Response(f"No id was sent", status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)

            if user.groups.filter(name='Manager').exists():
                return Response(f"User is already a manager", status.HTTP_409_CONFLICT)

            # add user to manager group
            manager_group = Group.objects.get(name='Manager')
            user.groups.add(manager_group)

            return Response(f"User {user_id} added to Manager's group.", status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(f"User with id {user_id} was not found", status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response(f"Manager group does not exist", status.HTTP_404_NOT_FOUND)

    def get_permissions(self):
        return [IsManager()]

    def get_queryset(self):
        return User.objects.filter(groups=Group.objects.get(name='Manager'))

class ManageSingleManager(generics.ListCreateAPIView, generics.DestroyAPIView):
    """
    Manages single Manager user
    """

    def get_permissions(self):
        return [IsManager()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.UserSerializer
        return serializers.UserGroupSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('pk')  # Retrieve the user ID from the URL
        return User.objects.filter(pk=user_id, groups__name='Manager')

    def create(self, request, *args, **kwargs):
        # Only allow modifications to the groups field
        user_id = kwargs.get('pk')
        group_name = request.data.get('group_name', 'Manager') # Default to Manager

        try:
            user = User.objects.get(pk=user_id)
            group = Group.objects.get(name=group_name)
        except User.DoesNotExist:
            return Response('User not found', status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response('Group not found', status.HTTP_404_NOT_FOUND)

        # Add the user to the group
        user.groups.add(group)
        user.save()

        return Response(f'User {user.username} added to group {group.name}.', status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        # Only allow modifications to the groups field
        user_id = kwargs.get('pk')
        group_name = 'Manager'

        try:
            user = User.objects.get(pk=user_id)
            group = Group.objects.get(name=group_name)
        except User.DoesNotExist:
            return Response('User not found', status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response('Group not found', status.HTTP_404_NOT_FOUND)

        # Add the user to the group
        user.groups.remove(group)
        user.save()

        return Response(f'User {user.username} removed from group {group.name}.', status.HTTP_200_OK)

class ListDeliveryCrew(BaseUsersView, generics.ListCreateAPIView):
    """
    List all delivery crew users
    """
    def post(self, request, *args, **kwargs):
        user_id = request.data['id']

        if not user_id:
            return Response(f"No id was sent", status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)

            if user.groups.filter(name='Delivery Crew').exists():
                return Response(f"User is already a delivery crew", status.HTTP_409_CONFLICT)

            # add user to Delivery Crew group
            delivery_crew_group = Group.objects.get(name='Delivery Crew')
            user.groups.add(delivery_crew_group)

            return Response(f"User {user_id} added to Delivery Crew's group.", status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(f"User with id {user_id} was not found", status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response(f"Delivery Crew group does not exist", status.HTTP_404_NOT_FOUND)

    def get_permissions(self):
        return [IsManager()]

    def get_queryset(self):
        return User.objects.filter(groups=Group.objects.get(name='Delivery Crew'))

class ManageSingleDeliveryCrew(generics.ListCreateAPIView, generics.DestroyAPIView):
    """
    Manages single Delivery Crew user
    """

    def get_permissions(self):
        return [IsManager()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.UserSerializer
        return serializers.UserGroupSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('pk')  # Retrieve the user ID from the URL
        return User.objects.filter(pk=user_id, groups__name='Delivery Crew')

    def create(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        group_id = request.data.get('groups') # Default to Manager
        print(f"User ID: {user_id}, Group id: {group_id}")

        try:
            user = User.objects.get(pk=user_id)
            group = Group.objects.get(id=group_id)
        except User.DoesNotExist:
            return Response('User not found', status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response('Group not found', status.HTTP_404_NOT_FOUND)

        # Add the user to the group
        user.groups.add(group)
        user.save()

        return Response(f'User {user.username} added to group {group.name}.', status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        # Only allow modifications to the groups field
        user_id = kwargs.get('pk')
        group_name = 'Delivery Crew'

        try:
            user = User.objects.get(pk=user_id)
            group = Group.objects.get(name=group_name)
        except User.DoesNotExist:
            return Response('User not found', status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response('Group not found', status.HTTP_404_NOT_FOUND)

        # Add the user to the group
        user.groups.remove(group)
        user.save()

        return Response(f'User {user.username} removed from group {group.name}.', status.HTTP_200_OK)

def check_authorization_token(view_instance):
        auth_token = view_instance.request.headers.get('Authorization')

        if auth_token is None:
            return Response({'error': 'Missing authorization token'}, status=status.HTTP_400_BAD_REQUEST)

        if not auth_token.startswith('Token '):
            return Response({'error': 'Invalid authorization token format'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = Token.objects.get(key=auth_token.split(' ')[1])
        except Token.DoesNotExist:
            return Response({'error': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)

        user = token.user

        if not user:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        return user

class ManageCart(generics.ListCreateAPIView, generics.DestroyAPIView):

    serializer_class = serializers.CartSerializer

    def get(self, request, *args, **kwargs):
        user_or_response = check_authorization_token(self)

        if isinstance(user_or_response, Response):
            return user_or_response

        user = user_or_response

        cart = Cart.objects.filter(user_id=user.id)

        if not cart.exists():  # Check if the cart is empty
            return Response({'message': 'Cart empty'}, status=status.HTTP_200_OK)

        return Response(serializers.CartSerializer(cart, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user_or_response = check_authorization_token(self)

        if isinstance(user_or_response, Response):
            return user_or_response

        user = user_or_response

        errors = {}

        field = 'quantity'
        if field not in self.request.data:
            errors[field] = f'{field} is required'

        field = 'menuitem'
        if field not in self.request.data:
            errors[field] = f'{field} is required'

        if errors:
            return Response(errors, status.HTTP_400_BAD_REQUEST)

        quantity = self.request.data['quantity']

        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response({'error': "Quantity must be a positive number greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

            menu_item = MenuItem.objects.get(id=self.request.data['menuitem'])
        except ValueError:
            return Response({'error': "Quantity must be a valid integer"}, status=status.HTTP_400_BAD_REQUEST)
        except MenuItem.DoesNotExist:
            return Response({'error': 'Menu item does not exists'}, status.HTTP_400_BAD_REQUEST)

        # Save the cart instance to the database
        try:
            # Create an instance of the Cart model
            cart = Cart(
                user=user,  # Set the user instance
                menuitem=menu_item,  # Set the menu item instance
                quantity=quantity,
                unit_price=menu_item.price,
                price=quantity * menu_item.price
            )

            cart.save()
            return Response({'success': 'Item added successfully to cart'}, status.HTTP_200_OK)
        except IntegrityError:
            # If the item already exists in the cart, update the existing entry
            cart = Cart.objects.get(user=user, menuitem=menu_item)
            cart.quantity = quantity  # Update the quantity by adding the new quantity
            cart.price = cart.quantity * cart.unit_price  # Update the price
            cart.save()  # Save the updated cart item
            return Response({'success': 'Item quantity change updated successfully in cart'}, status.HTTP_200_OK)


    def delete(self, request, *args, **kwargs):
        user_or_response = check_authorization_token(self)

        if isinstance(user_or_response, Response):
            return user_or_response

        user = user_or_response

        deleted, _ = Cart.objects.filter(user=user).delete()

        if deleted == 0:
            return Response({'message': "User's cart is already empty"}, status.HTTP_200_OK)

        return Response({'success': 'Emptied the cart for the user'}, status.HTTP_200_OK)

    def get_queryset(self):
        return Cart.objects.all()

    def get_permissions(self):
        user = self.request.user

        # Allow access to authenticated users who are not in "Manager" or "Delivery Crew" groups
        if user.is_authenticated and not user.groups.filter(name__in=['Manager', 'Delivery Crew']).exists():
            return [AllowAny()]

        # Deny access if the user is in "Manager" or "Delivery Crew" groups or if user is not authenticated
        return [DenyAllPermission()]

    def has_permission(self, request, view):
        # Explicitly check the permissions
        permissions = self.get_permissions()
        for permission in permissions:
            if not permission.has_permission(request, view):
                return False
        return True

    def get_serializer(self, *args, **kwargs):
        # Ensure the serializer is not accessible if the user doesn't have permissions
        if not self.request.user.is_authenticated or self.request.user.groups.filter(name__in=['Manager', 'Delivery Crew']).exists():
            raise PermissionDenied("You do not have permission to perform this action.")
        return super().get_serializer(*args, **kwargs)

class ManageOrders(generics.CreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.Order

    def get(self, request, *args, **kwargs):
        user_or_response = check_authorization_token(self)

        if isinstance(user_or_response, Response):
            return user_or_response

        user = user_or_response

        if not user.groups.exists():
            # Customer
            user_orders = Order.objects.filter(user=user)

            if not user_orders:
                return Response({'empty': 'You have no orders'}, status.HTTP_404_NOT_FOUND)

            return Response(serializers.OrderSerializer(user_orders, many=True).data, status.HTTP_200_OK)
        elif user.groups.filter(name='Delivery Crew').exists():
            # Delivery Crew
            user_orders = Order.objects.filter(delivery_crew=user)

            if not user_orders:
                return Response({'empty': 'No orders were found for this Delivery Crew user'}, status.HTTP_404_NOT_FOUND)

            return Response(serializers.OrderSerializer(user_orders, many=True).data, status.HTTP_200_OK)
        else:
            # Manager
            user_orders = Order.objects.all()

            if not user_orders:
                return Response({'empty': 'No orders were yet placed'}, status.HTTP_404_NOT_FOUND)

            return Response(serializers.OrderSerializer(user_orders, many=True).data, status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user_or_response = check_authorization_token(self)

        if isinstance(user_or_response, Response):
            return user_or_response

        user = user_or_response

        # Deny access to users in a group (not a customer)
        if user.groups.exists():
            return Response({'error': 'Not a customer'}, status.HTTP_403_FORBIDDEN)

        try:
            user_cart = Cart.objects.filter(user=user)

            # Attempt to find a delivery crew user
            delivery_crew_group =  Group.objects.get(name='Delivery Crew')
            delivery_crew_user = User.objects.filter(groups=delivery_crew_group).first()

            if delivery_crew_user is None:
                return Response({'error': 'No Delivery Crew user was found. Add one'}, status.HTTP_404_NOT_FOUND)

            # Calculate the total price for the order
            order_total_price = sum(item.price for item in user_cart)

            with transaction.atomic():
                # Create an Order instance
                new_order = Order(
                    user = user,
                    total = order_total_price,
                    date = timezone.now().date()  # Convert datetime to date
                )

                # Save the order first to generate the primary key
                new_order.save()

                # Create OrderItems for each item in the cart
                new_order_items = []
                for cart_item in user_cart:
                    order_item = OrderItem(
                        order=new_order,
                        menuitem = cart_item.menuitem,
                        quantity = cart_item.quantity,
                        unit_price = cart_item.unit_price,
                        price = cart_item.price
                    )

                    order_total_price += cart_item.price
                    new_order_items.append(order_item)

                # Bulk create the order items
                OrderItem.objects.bulk_create(new_order_items)

                # Clear the user's cart
                user_cart.delete()

                # Return the order details
                return Response(serializers.OrderSerializer(new_order).data, status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({'empty': 'No cart items were found for the user'}, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# GET, PUT, PATCH, DELETE
class ManageSingleOrder(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.Order

    def get(self, request, *args, **kwargs):
        user_or_response = check_authorization_token(self)

        if isinstance(user_or_response, Response):
            return user_or_response

        user = user_or_response

        order_id = kwargs.get('pk')

        if not user.groups.exists():
            # Customer
            try:
                order = Order.objects.get(id=order_id, user=user)
                return Response(serializers.OrderSerializer(order).data, status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({'error': 'No orders were found for this customer'}, status.HTTP_404_NOT_FOUND)
        elif user.groups.filter(name='Delivery Crew').exists():
            # Delivery Crew
            try:
                order = Order.objects.get(id=order_id, delivery_crew=user)
                return Response(serializers.OrderSerializer(order).data, status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({'error': 'No order with this specific id was found for this Delivery Crew'}, status.HTTP_404_NOT_FOUND)
        else:
                return Response({'error': 'Unauthorized'}, status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        user_or_response = check_authorization_token(self)

        if isinstance(user_or_response, Response):
            return user_or_response

        user = user_or_response

        if not user.groups.filter(name__in=['Manager', 'Delivery Crew']).exists():
            return Response({'error': 'Only staff can update orders'}, status=status.HTTP_403_FORBIDDEN)

        order_id = kwargs.get('pk')

        try:
            order = Order.objects.get(id=order_id)

            status_value = request.data.get('status')

            if user.groups.filter(name='Delivery Crew').exists():
                delivery_crew_id = None
            else:
                # Manager can update this field
                delivery_crew_id = request.data.get('delivery_crew')

            if not delivery_crew_id and not status_value:
                return Response({'error': 'Nothing to update. Missing either status or delivery_crew'}, status.HTTP_400_BAD_REQUEST)

            if delivery_crew_id:
                try:
                    delivery_crew_user = User.objects.get(id=delivery_crew_id)

                    if not delivery_crew_user.groups.filter(name='Delivery Crew').exists():
                        return Response({'error': 'User is not in Delivery Crew group'}, status.HTTP_400_BAD_REQUEST)

                    order.delivery_crew = delivery_crew_user
                except User.DoesNotExist:
                    return Response({'error': 'User not found'}, status.HTTP_404_NOT_FOUND)

            if status_value:
                order.status = status_value

            order.save()
            return Response({'message': 'Order updated'}, status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'No orders were found'}, status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        user_or_response = check_authorization_token(self)

        if isinstance(user_or_response, Response):
            return user_or_response

        user = user_or_response

        if not user.groups.filter(name='Manager').exists():
            return Response({'error': 'Only managers can delete orders'}, status=status.HTTP_403_FORBIDDEN)

        order_id = kwargs.get('pk')

        try:
            order = Order.objects.get(id=order_id)

            order.delete()
            return Response({'message': 'Order deleted'}, status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'No orders were found'}, status.HTTP_404_NOT_FOUND)