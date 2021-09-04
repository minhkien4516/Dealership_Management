from django.urls import path

from . import views

urlpatterns = [
    path('logout', views.user_logout_view, name='user-logout'),

    path('dealership-registration/', views.dealership_registration_view, name='dealership-registration'),
    path('dropdown/', views.load_districts, name='ajax-load-districts'),

    path('dealerships/', views.dealerships_of_current_user, name='dealerships-of-current-user'),
    path('dealerships-in-queue/', views.dealerships_in_queue_of_current_user,
         name='dealerships-in-queue-of-current-user'),
    path('dealerships/<str:dealership_id>/', views.update_delete_dealership_information_view,
         name='update-dealership-information'),
]
