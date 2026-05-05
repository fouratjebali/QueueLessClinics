from django.contrib import admin

from .models import Clinic, ClinicSettings, User, Service, Queue, Ticket, QueueEvent, Notification


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'is_active')
    search_fields = ('name', 'city', 'slug')


@admin.register(ClinicSettings)
class ClinicSettingsAdmin(admin.ModelAdmin):
    list_display = ('clinic', 'max_capacity', 'estimated_service_time', 'enable_sms', 'enable_email')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'clinic')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('role', 'clinic')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'clinic', 'code', 'estimated_duration', 'is_active')
    list_filter = ('clinic', 'is_active')
    search_fields = ('name', 'code')


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ('clinic', 'date', 'is_active', 'total_tickets', 'waiting', 'called', 'serving', 'completed')
    list_filter = ('clinic', 'date', 'is_active')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'clinic', 'queue', 'status', 'priority', 'position', 'patient_name')
    list_filter = ('clinic', 'status', 'priority')
    search_fields = ('ticket_number', 'patient_name', 'patient_phone')


@admin.register(QueueEvent)
class QueueEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'queue', 'ticket', 'timestamp', 'user_name')
    list_filter = ('event_type', 'queue')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('type', 'recipient', 'status', 'ticket', 'created_at')
    list_filter = ('type', 'status')
    search_fields = ('recipient',)