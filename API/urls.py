from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', views.APIRootView.as_view(), name='api-root'),  # The root API view
    # path('users', views.CreateNewUser.as_view(), name='users-create'),
    # path('users/me', views.DisplayCurrentUser.as_view(), name='users-display-current'),
    path('menu-categories', views.ListCreateMenuCategories.as_view(), name='menu-categories-list-create'),
    path('menu-categories/<int:pk>', views.ManageMenuCategory.as_view(), name='menu-categories-detail'),
    path('menu-items', views.ListCreateMenuItems.as_view(), name='menu-items-list-create'),
    path('menu-items/<int:pk>', views.RetrieveUpdateDestroyMenuItems.as_view(), name='menu-items-detail'),
    path('groups', views.ListCreateGroups.as_view(), name='groups-list-create'),
    path('groups/<int:pk>', views.RetrieveUpdateDestroyGroups.as_view(), name='groups-detail'),
    path('groups/managers/users', views.ListManagers.as_view(), name='managers-list'),
    path('groups/managers/users/<int:pk>', views.ManageSingleManager.as_view(), name='managers-detail'),
    path('groups/delivery-crew/users', views.ListDeliveryCrew.as_view(), name='delivery-crew-list'),
    path('groups/delivery-crew/users/<int:pk>', views.ManageSingleDeliveryCrew.as_view(), name='delivery-crew-detail'),
    path('cart/menu-items', views.ManageCart.as_view(), name='cart-menu-items'),
    path('orders', views.ManageOrders.as_view(), name='manage-orders'),
    path('orders/<int:pk>', views.ManageSingleOrder.as_view(), name='manage-single-order'),
]