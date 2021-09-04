from django.urls import path

from . import views

urlpatterns = [
    path('dealership-list/', views.dealership_list_view, name='dealership-list'),

    path('dealership-registration-queue/', views.dealership_registration_queue_view,
         name='dealership-registration-queue'),
    path('approve-registration-form/<int:dealership_in_queue_id>', views.approve_registration_form,
         name='approve-registration-form'),
    path('reject-registration-form/<int:dealership_in_queue_id>', views.reject_registration_form,
         name='reject-registration-form'),

    path('dealership-cancel-queue/', views.dealership_cancellation_in_queue_view,
         name='dealerships-in-cancellation-queue'),
    path('approve-cancellation-form/<str:dealership_id>', views.approve_cancellation_form,
         name='approve-cancellation-form'),
    path('reject-cancellation-form/<str:dealership_id>', views.reject_cancellation_form,
         name='reject-cancellation-form'),
]
