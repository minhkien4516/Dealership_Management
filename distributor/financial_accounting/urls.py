from django.urls import path

from . import views

urlpatterns = [
    path('exportation-report/', views.exportation_report_view, name='exportation-report'),
    path('exportation-detail-form/<str:dealership_id>/<int:month>', views.load_exportation_detail_reports_by_month_view,
         name='exportation-detail-form'),

    path('importation-report/', views.importation_report_view, name='importation-report'),
    path('importation-detail-form/<int:importation_id>', views.load_importation_detail_reports_by_month,
         name='importation-detail-form'),

    path('importation-request/', views.importation_request_view, name='importation-request'),
    path('importation-detail-request/<int:importation_request_id>', views.load_importation_detail_request,
         name='importation-detail-request'),
    path('approve-importation-request/<int:importation_request_id>', views.approve_importation_detail_request,
         name='approve-importation-request'),
    path('reject-importation-request/<int:importation_request_id>', views.reject_importation_detail_request,
         name='reject-importation-request'),
]
