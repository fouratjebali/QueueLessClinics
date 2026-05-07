"""
Serialisers for the QueueLess API.

These classes translate between Django model instances and JSON data
exchanged over the API. They encapsulate validation logic and can
perform complex creation/updating of models. Where appropriate
serializer methods call model helper functions to encapsulate
business rules (e.g. creating tickets and updating queue statistics).
"""

from __future__ import annotations

import string
import uuid
from typing import Any, Dict, Optional

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import (
    Clinic,
    ClinicSettings,
    Service,
    Queue,
    Ticket,
    QueueEvent,
    Notification,
    AdminAuditLog,
    SystemSettings,
    User,
)


class ClinicSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicSettings
        exclude = ['id', 'clinic', 'created_at', 'updated_at']


class ClinicSerializer(serializers.ModelSerializer):
    settings = ClinicSettingsSerializer(read_only=True)

    class Meta:
        model = Clinic
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class QueueSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)

    class Meta:
        model = Queue
        fields = '__all__'
        read_only_fields = ['id', 'opened_at', 'closed_at', 'created_at', 'updated_at',
                            'total_tickets', 'waiting', 'called', 'serving', 'completed',
                            'cancelled', 'no_show', 'avg_wait_time', 'avg_service_time',
                            'current_wait_time']


class TicketSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True, default=None)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['id', 'status', 'priority', 'position', 'ticket_number',
                            'joined_at', 'called_at', 'serving_started_at',
                            'completed_at', 'cancelled_at', 'created_at', 'updated_at',
                            'called_by', 'served_by']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        clinic: Clinic = attrs['clinic']
        queue: Optional[Queue] = attrs.get('queue')
        # For public join flows, allow queue omission and infer today's active queue.
        if queue is None:
            today = timezone.localdate()
            queue = (
                Queue.objects.filter(clinic=clinic, date=today, is_active=True)
                .order_by('-created_at')
                .first()
            )
            if queue is None:
                queue = Queue.objects.create(clinic=clinic, date=today, is_active=True)
            attrs['queue'] = queue
        # Ensure the queue belongs to the same clinic as the ticket
        if queue.clinic_id != clinic.id:
            raise serializers.ValidationError('Queue does not belong to the specified clinic.')
        if not queue.is_active:
            raise serializers.ValidationError('Queue is closed; cannot join.')
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Ticket:
        """Create a ticket and update related queue statistics.

        Ticket numbers are generated sequentially per clinic and day. The
        prefix derives from the clinic's position in the database (A
        for the first clinic, B for the second, etc.) but falls back to
        ``T`` when the clinic count exceeds 26. Positions and
        estimated wait times are computed based on the current queue.
        """
        queue: Queue = validated_data['queue']
        clinic: Clinic = validated_data['clinic']
        service: Optional[Service] = validated_data.get('service')
        # Determine prefix for ticket number based on clinic index
        clinic_index = Clinic.objects.filter(id__lte=clinic.id).count() - 1
        prefix = string.ascii_uppercase[clinic_index] if clinic_index < len(string.ascii_uppercase) else 'T'
        # Determine next sequential number for today's queue
        today_tickets = Ticket.objects.filter(queue=queue).order_by('-position')
        next_position = 1
        if today_tickets.exists():
            next_position = today_tickets.first().position + 1
        ticket_number = f"{prefix}{next_position:03d}"
        estimated_wait = 0
        # Use the clinic's estimated service time if provided; multiply by number ahead
        settings = getattr(clinic, 'settings', None)
        est_service_time = settings.estimated_service_time if settings else 15
        estimated_wait = est_service_time * (next_position - 1)
        validated_data['ticket_number'] = ticket_number
        validated_data['position'] = next_position
        validated_data['estimated_wait_time'] = estimated_wait
        validated_data['priority'] = Ticket.TicketPriority.NORMAL  # default priority
        # Use atomic transaction to avoid race conditions on position assignment
        with transaction.atomic():
            ticket = super().create(validated_data)
            # update queue statistics and create event
            queue.update_statistics()
            queue.save(update_fields=[
                'total_tickets', 'waiting', 'called', 'serving', 'completed',
                'cancelled', 'no_show', 'avg_wait_time', 'avg_service_time', 'current_wait_time'
            ])
            QueueEvent.objects.create(
                queue=queue,
                ticket=ticket,
                event_type=QueueEvent.QueueEventType.TICKET_CREATED,
                user=None,
                user_name='System',
                metadata={'ticket_number': ticket_number, 'patient_name': ticket.patient_name},
            )
        return ticket


class QueueEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueueEvent
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'status', 'sent_at', 'delivered_at', 'error_message', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True, default=None)
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'clinic',
            'clinic_name',
            'is_active',
            'is_staff',
            'force_password_change',
            'full_name',
            'password',
        ]
        read_only_fields = ['id', 'is_staff']

    def create(self, validated_data: Dict[str, Any]) -> User:
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        password = validated_data.pop('password', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class AdminClinicSerializer(serializers.ModelSerializer):
    settings = ClinicSettingsSerializer(read_only=True)

    class Meta:
        model = Clinic
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminClinicSettingsPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicSettings
        fields = ['max_capacity', 'estimated_service_time', 'emergency_priority_rules']


class AdminHoursPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicSettings
        fields = ['operating_hours']


class AdminServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True, default=None)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'clinic',
            'clinic_name',
            'is_active',
            'force_password_change',
            'full_name',
            'date_joined',
            'updated_at',
            'last_login_at',
        ]
        read_only_fields = ['id', 'date_joined', 'updated_at', 'last_login_at', 'full_name', 'clinic_name']


class AdminAuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)

    class Meta:
        model = AdminAuditLog
        fields = '__all__'


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = '__all__'
        read_only_fields = ['id', 'updated_by', 'updated_at', 'created_at']
