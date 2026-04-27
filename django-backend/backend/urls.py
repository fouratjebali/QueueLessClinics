"""
URL configuration for the QueueLess backend.

This module defines the URL routing for the project. It wires up the
Django admin, the REST API router and authentication endpoints. API
routes are namespaced under ``/api/`` to avoid colliding with any
future server‑side rendered pages.
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from core import views as core_views


# Create a default router and register our viewsets. Each viewset
# provides list and detail actions by default and can be extended
# with custom actions (e.g. call‑next, serve) in the viewset class.
router = routers.DefaultRouter()
router.register(r'clinics', core_views.ClinicViewSet, basename='clinic')
router.register(r'clinic-settings', core_views.ClinicSettingsViewSet, basename='clinic-settings')
router.register(r'services', core_views.ServiceViewSet, basename='service')
router.register(r'queues', core_views.QueueViewSet, basename='queue')
router.register(r'tickets', core_views.TicketViewSet, basename='ticket')
router.register(r'users', core_views.UserViewSet, basename='user')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/public/stats/', core_views.PublicStatsView.as_view(), name='api-public-stats'),
    # Simple email/password login backed by the existing users table
    path('api/auth/login/', core_views.LoginView.as_view(), name='api-login'),
    path('api/auth/logout/', core_views.AuthLogoutView.as_view(), name='api-logout'),
    path('api/auth/me/', core_views.AuthMeView.as_view(), name='api-auth-me'),
    path('api/auth/change-password/', core_views.AuthChangePasswordView.as_view(), name='api-auth-change-password'),
    # Staff module APIs
    path('api/staff/clinic/', core_views.StaffClinicView.as_view(), name='api-staff-clinic'),
    path('api/staff/clinic/settings/', core_views.StaffClinicSettingsView.as_view(), name='api-staff-clinic-settings'),
    path('api/staff/clinic/kpis/', core_views.StaffClinicKpiView.as_view(), name='api-staff-clinic-kpis'),
    path('api/staff/queues/', core_views.StaffQueuesView.as_view(), name='api-staff-queues'),
    path('api/staff/queues/open/', core_views.StaffQueueOpenView.as_view(), name='api-staff-queues-open'),
    path('api/staff/queues/<uuid:queue_id>/close/', core_views.StaffQueueCloseView.as_view(), name='api-staff-queues-close'),
    path('api/staff/tickets/', core_views.StaffTicketsView.as_view(), name='api-staff-tickets'),
    path('api/staff/tickets/walkin/', core_views.StaffWalkinCreateView.as_view(), name='api-staff-tickets-walkin'),
    path('api/staff/tickets/<uuid:ticket_id>/call/', core_views.StaffTicketCallView.as_view(), name='api-staff-ticket-call'),
    path('api/staff/tickets/<uuid:ticket_id>/start/', core_views.StaffTicketStartView.as_view(), name='api-staff-ticket-start'),
    path('api/staff/tickets/<uuid:ticket_id>/complete/', core_views.StaffTicketCompleteView.as_view(), name='api-staff-ticket-complete'),
    path('api/staff/tickets/<uuid:ticket_id>/cancel/', core_views.StaffTicketCancelView.as_view(), name='api-staff-ticket-cancel'),
    path('api/staff/tickets/<uuid:ticket_id>/no-show/', core_views.StaffTicketNoShowView.as_view(), name='api-staff-ticket-no-show'),
    path('api/staff/tickets/<uuid:ticket_id>/reorder/', core_views.StaffTicketReorderView.as_view(), name='api-staff-ticket-reorder'),
    path('api/staff/tickets/<uuid:ticket_id>/', core_views.StaffTicketPatchView.as_view(), name='api-staff-ticket-patch'),
    path('api/staff/services/', core_views.StaffServicesView.as_view(), name='api-staff-services'),
    path('api/staff/services/<uuid:service_id>/', core_views.StaffServiceDetailView.as_view(), name='api-staff-service-detail'),
    # Admin module APIs
    path('api/admin/clinics/', core_views.AdminClinicListCreateView.as_view(), name='api-admin-clinics'),
    path('api/admin/clinics/<uuid:pk>/', core_views.AdminClinicDetailView.as_view(), name='api-admin-clinic-detail'),
    path('api/admin/clinics/<uuid:pk>/toggle-active/', core_views.AdminClinicToggleActiveView.as_view(), name='api-admin-clinic-toggle-active'),
    path('api/admin/clinics/<uuid:pk>/logo/', core_views.AdminClinicLogoView.as_view(), name='api-admin-clinic-logo'),
    path('api/admin/clinics/<uuid:pk>/branding/', core_views.AdminClinicBrandingView.as_view(), name='api-admin-clinic-branding'),
    path('api/admin/clinics/<uuid:pk>/rules/', core_views.AdminClinicRulesView.as_view(), name='api-admin-clinic-rules'),
    path('api/admin/clinics/<uuid:pk>/hours/', core_views.AdminClinicHoursView.as_view(), name='api-admin-clinic-hours'),
    path('api/admin/clinics/<uuid:pk>/services/', core_views.AdminClinicServicesView.as_view(), name='api-admin-clinic-services'),
    path('api/admin/services/<uuid:service_id>/', core_views.AdminServiceDetailView.as_view(), name='api-admin-service-detail'),
    path('api/admin/services/reorder/', core_views.AdminServiceReorderView.as_view(), name='api-admin-service-reorder'),
    path('api/admin/users/', core_views.AdminUsersListCreateView.as_view(), name='api-admin-users'),
    path('api/admin/users/<uuid:pk>/', core_views.AdminUserDetailView.as_view(), name='api-admin-user-detail'),
    path('api/admin/users/<uuid:pk>/toggle-active/', core_views.AdminUserToggleActiveView.as_view(), name='api-admin-user-toggle-active'),
    path('api/admin/users/<uuid:pk>/reset-password/', core_views.AdminUserResetPasswordView.as_view(), name='api-admin-user-reset-password'),
    path('api/admin/users/<uuid:pk>/set-role/', core_views.AdminUserSetRoleView.as_view(), name='api-admin-user-set-role'),
    path('api/admin/users/<uuid:pk>/assign-clinic/', core_views.AdminUserAssignClinicView.as_view(), name='api-admin-user-assign-clinic'),
    path('api/admin/analytics/overview/', core_views.AdminAnalyticsOverviewView.as_view(), name='api-admin-analytics-overview'),
    path('api/admin/analytics/clinic-ranking/', core_views.AdminAnalyticsClinicRankingView.as_view(), name='api-admin-analytics-clinic-ranking'),
    path('api/admin/analytics/tickets-timeseries/', core_views.AdminAnalyticsTicketsTimeseriesView.as_view(), name='api-admin-analytics-timeseries'),
    path('api/admin/analytics/status-distribution/', core_views.AdminAnalyticsStatusDistributionView.as_view(), name='api-admin-analytics-status-distribution'),
    path('api/admin/analytics/peak-hours/', core_views.AdminAnalyticsPeakHoursView.as_view(), name='api-admin-analytics-peak-hours'),
    path('api/admin/analytics/export-csv/', core_views.AdminAnalyticsExportCsvView.as_view(), name='api-admin-analytics-export-csv'),
    path('api/admin/analytics/export-pdf/', core_views.AdminAnalyticsExportPdfView.as_view(), name='api-admin-analytics-export-pdf'),
    path('api/admin/audit-logs/', core_views.AdminAuditLogsListView.as_view(), name='api-admin-audit-logs'),
    path('api/admin/audit-logs/<uuid:pk>/', core_views.AdminAuditLogDetailView.as_view(), name='api-admin-audit-log-detail'),
    path('api/admin/settings/', core_views.AdminSystemSettingsView.as_view(), name='api-admin-system-settings'),
    path('api/admin/settings/test-notification/', core_views.AdminSystemSettingsTestNotificationView.as_view(), name='api-admin-system-settings-test-notification'),
    # Browsable API login/logout (session-based, mainly for debugging)
    path('api/auth/', include('rest_framework.urls')),
]
