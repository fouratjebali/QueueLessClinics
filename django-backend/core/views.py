"""Viewsets for the QueueLess API."""

from __future__ import annotations

import csv
import secrets
import string
from datetime import timedelta
from typing import Optional

import bcrypt
from django.http import HttpResponse
from django.db import connection, transaction
from django.db.models import Avg, Count, F, Q, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AdminAuditLog, Clinic, ClinicSettings, Notification, Queue, QueueEvent, Service, SystemSettings, Ticket, User
from .serializers import (
    AdminAuditLogSerializer,
    AdminClinicSerializer,
    AdminClinicSettingsPatchSerializer,
    AdminHoursPatchSerializer,
    AdminServiceSerializer,
    AdminUserSerializer,
    ClinicSerializer,
    ClinicSettingsSerializer,
    QueueSerializer,
    ServiceSerializer,
    SystemSettingsSerializer,
    TicketSerializer,
    UserSerializer,
)


def _actor_from_request(request) -> Optional[User]:
    user = getattr(request, 'user', None)
    if user is not None and getattr(user, 'is_authenticated', False):
        return user
    return None


class ClinicViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing clinics."""

    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing services."""

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        clinic_id = self.request.query_params.get('clinic')
        is_active = self.request.query_params.get('active')
        if clinic_id:
            qs = qs.filter(clinic_id=clinic_id)
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        return qs


class QueueViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing queues."""

    queryset = Queue.objects.all()
    serializer_class = QueueSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        clinic_id = self.request.query_params.get('clinic')
        date = self.request.query_params.get('date')
        if clinic_id:
            qs = qs.filter(clinic_id=clinic_id)
        if date:
            qs = qs.filter(date=date)
        return qs

    @action(detail=True, methods=['post'])
    def open(self, request, pk: str | None = None) -> Response:
        """Open the queue for the day."""
        actor = _actor_from_request(request)
        queue = self.get_object()
        queue.open()
        queue.save()
        QueueEvent.objects.create(
            queue=queue,
            ticket=None,
            event_type=QueueEvent.QueueEventType.QUEUE_OPENED,
            user=actor,
            user_name=actor.get_full_name() if actor else 'System',
            metadata={'message': 'Queue opened'},
        )
        serializer = self.get_serializer(queue)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk: str | None = None) -> Response:
        """Close the queue."""
        actor = _actor_from_request(request)
        queue = self.get_object()
        queue.close()
        queue.save()
        QueueEvent.objects.create(
            queue=queue,
            ticket=None,
            event_type=QueueEvent.QueueEventType.QUEUE_CLOSED,
            user=actor,
            user_name=actor.get_full_name() if actor else 'System',
            metadata={'message': 'Queue closed'},
        )
        serializer = self.get_serializer(queue)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def call_next(self, request, pk: str | None = None) -> Response:
        """Call the next waiting ticket in the queue."""
        actor = _actor_from_request(request)
        queue = self.get_object()
        priority_order = {
            Ticket.TicketPriority.URGENT: 0,
            Ticket.TicketPriority.HIGH: 1,
            Ticket.TicketPriority.NORMAL: 2,
        }
        waiting_tickets = list(queue.tickets.filter(status=Ticket.TicketStatus.WAITING))
        if not waiting_tickets:
            return Response({'detail': 'No waiting tickets.'}, status=status.HTTP_400_BAD_REQUEST)
        waiting_tickets.sort(key=lambda t: (priority_order[t.priority], t.position))
        ticket = waiting_tickets[0]
        ticket.call(actor)
        ticket.save(update_fields=['status', 'called_at', 'called_by'])
        serializer = TicketSerializer(ticket, context={'request': request})
        return Response(serializer.data)


class ClinicSettingsViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing clinic settings."""

    queryset = Clinic.objects.select_related('settings').all()
    serializer_class = ClinicSettingsSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        clinic_id = self.request.query_params.get('clinic')
        if clinic_id:
            qs = qs.filter(id=clinic_id)
        return qs

    def list(self, request, *args, **kwargs):
        clinics = self.get_queryset()
        settings = [c.settings for c in clinics if hasattr(c, 'settings')]
        serializer = self.get_serializer(settings, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        clinic = get_object_or_404(Clinic.objects.select_related('settings'), id=kwargs.get('pk'))
        serializer = self.get_serializer(clinic.settings)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        clinic = get_object_or_404(Clinic.objects.select_related('settings'), id=kwargs.get('pk'))
        serializer = self.get_serializer(clinic.settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        clinic = get_object_or_404(Clinic.objects.select_related('settings'), id=kwargs.get('pk'))
        serializer = self.get_serializer(clinic.settings, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing users."""

    queryset = User.objects.select_related('clinic').all()
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        clinic_id = self.request.query_params.get('clinic')
        role = self.request.query_params.get('role')
        is_active = self.request.query_params.get('active')
        if clinic_id:
            qs = qs.filter(clinic_id=clinic_id)
        if role:
            qs = qs.filter(role=role)
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        return qs


class TicketViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing tickets."""

    queryset = Ticket.objects.select_related('clinic', 'queue', 'service').all()
    serializer_class = TicketSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        ticket_id = self.request.query_params.get('id')
        clinic_id = self.request.query_params.get('clinic')
        queue_id = self.request.query_params.get('queue')
        ticket_number = self.request.query_params.get('ticket_number')
        patient_phone = self.request.query_params.get('patient_phone')
        status_param = self.request.query_params.get('status')
        if ticket_id:
            qs = qs.filter(id=ticket_id)
        if clinic_id:
            qs = qs.filter(clinic_id=clinic_id)
        if queue_id:
            qs = qs.filter(queue_id=queue_id)
        if ticket_number:
            qs = qs.filter(ticket_number__iexact=ticket_number)
        if patient_phone:
            qs = qs.filter(patient_phone=patient_phone)
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    @action(detail=True, methods=['post'])
    def call(self, request, pk: str | None = None) -> Response:
        """Call a specific ticket (manual override)."""
        actor = _actor_from_request(request)
        ticket = self.get_object()
        ticket.call(actor)
        ticket.save(update_fields=['status', 'called_at', 'called_by'])
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def start_service(self, request, pk: str | None = None) -> Response:
        """Begin serving the ticket."""
        actor = _actor_from_request(request)
        ticket = self.get_object()
        ticket.start_serving(actor)
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk: str | None = None) -> Response:
        """Complete the service for the ticket."""
        actor = _actor_from_request(request)
        ticket = self.get_object()
        ticket.complete(actor)
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk: str | None = None) -> Response:
        """Cancel a ticket with an optional reason."""
        actor = _actor_from_request(request)
        ticket = self.get_object()
        reason: Optional[str] = request.data.get('reason')
        ticket.cancel(actor, reason=reason)
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def no_show(self, request, pk: str | None = None) -> Response:
        """Mark a ticket as no-show."""
        actor = _actor_from_request(request)
        ticket = self.get_object()
        ticket.mark_no_show(actor)
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)


class LoginView(APIView):
    """Simple email/password login endpoint."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs) -> Response:
        email: str | None = request.data.get('email')
        password: str | None = request.data.get('password')

        if not email or not password:
            return Response(
                {'detail': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, clinic_id, email, first_name, last_name, role, password_hash
                FROM users
                WHERE email = %s AND is_active = TRUE
                """,
                [email],
            )
            row = cursor.fetchone()

        if not row:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)

        user_id, clinic_id, email_db, first_name, last_name, role, password_hash = row

        try:
            password_ok = bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except ValueError:
            # Legacy/truncated hashes should fail auth gracefully, not crash login.
            password_ok = False

        if not password_ok:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)

        user_payload = {
            'id': str(user_id),
            'clinic_id': str(clinic_id) if clinic_id else None,
            'email': email_db,
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'full_name': f'{first_name} {last_name}'.strip(),
        }

        return Response({'token': 'dummy-token', 'user': user_payload})


class PublicStatsView(APIView):
    """Public aggregate statistics for homepage hero cards."""

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs) -> Response:
        today = timezone.localdate()
        active_clinics = Clinic.objects.filter(is_active=True).count()
        queues_today = Queue.objects.filter(date=today, is_active=True)
        active_queues = Queue.objects.filter(is_active=True)

        # Prefer today's active queues, but tolerate date/timezone drift by
        # falling back to all active queues when needed.
        queue_scope = queues_today if queues_today.exists() else active_queues

        waiting_tickets = Ticket.objects.filter(
            queue__in=queue_scope,
            status=Ticket.TicketStatus.WAITING
        )
        in_queue = waiting_tickets.count()

        serving_now = Ticket.objects.filter(
            queue__in=queue_scope,
            status=Ticket.TicketStatus.SERVING
        ).count()

        open_queues = queue_scope.count()

        avg_wait_minutes = waiting_tickets.aggregate(avg=Avg('estimated_wait_time')).get('avg') or 0

        avg_wait_minutes = max(0, int(round(float(avg_wait_minutes))))

        total_patients = Ticket.objects.filter(joined_at__date=today).count()

        next_available_at = timezone.localtime() + timedelta(minutes=avg_wait_minutes)
        next_available_time = next_available_at.strftime('%I:%M %p').lstrip('0')

        return Response({
            'total_patients': total_patients,
            'partner_clinics': active_clinics,
            'open_queues': open_queues,
            'in_queue': in_queue,
            'serving_now': serving_now,
            'next_available_time': next_available_time,
        })


STAFF_ROLES = {
    User.UserRole.STAFF,
    User.UserRole.DOCTOR,
    User.UserRole.NURSE,
    User.UserRole.RECEPTIONIST,
}

STAFF_ACTION_ROLES = {
    'queue_open': {User.UserRole.STAFF, User.UserRole.RECEPTIONIST},
    'queue_close': {User.UserRole.STAFF, User.UserRole.RECEPTIONIST},
    'ticket_call': {User.UserRole.STAFF, User.UserRole.RECEPTIONIST, User.UserRole.NURSE, User.UserRole.DOCTOR},
    'ticket_start': {User.UserRole.STAFF, User.UserRole.NURSE, User.UserRole.DOCTOR},
    'ticket_complete': {User.UserRole.STAFF, User.UserRole.NURSE, User.UserRole.DOCTOR},
    'ticket_cancel': {User.UserRole.STAFF, User.UserRole.RECEPTIONIST, User.UserRole.NURSE},
    'ticket_no_show': {User.UserRole.STAFF, User.UserRole.RECEPTIONIST, User.UserRole.NURSE},
    'ticket_walkin': {User.UserRole.STAFF, User.UserRole.RECEPTIONIST},
    'ticket_reorder': {User.UserRole.STAFF, User.UserRole.RECEPTIONIST},
    'ticket_update': {User.UserRole.STAFF, User.UserRole.RECEPTIONIST, User.UserRole.NURSE, User.UserRole.DOCTOR},
    'service_manage': {User.UserRole.STAFF, User.UserRole.RECEPTIONIST},
    'settings_manage': {User.UserRole.STAFF, User.UserRole.RECEPTIONIST},
}


def _parse_iso_date(value: Optional[str], fallback):
    if not value:
        return fallback
    try:
        return timezone.datetime.fromisoformat(value).date()
    except ValueError:
        return fallback


def _has_role_access(user: User, action: str) -> bool:
    if user.role == User.UserRole.ADMIN:
        return True
    allowed_roles = STAFF_ACTION_ROLES.get(action, STAFF_ROLES)
    return user.role in allowed_roles


class IsStaffRequest(BasePermission):
    """Allow access for authenticated staff roles, including admins."""

    def has_permission(self, request, view) -> bool:
        user = getattr(request, 'user', None)
        if user and getattr(user, 'is_authenticated', False):
            return user.role in STAFF_ROLES or user.role == User.UserRole.ADMIN
        role = request.headers.get('X-User-Role')
        return role in STAFF_ROLES or role == User.UserRole.ADMIN


class AuthMeView(APIView):
    permission_classes = [IsStaffRequest]

    def get(self, request) -> Response:
        actor = _request_actor(request)
        if not actor:
            return Response({'detail': 'Unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)
        payload = {
            'id': str(actor.id),
            'email': actor.email,
            'first_name': actor.first_name,
            'last_name': actor.last_name,
            'role': actor.role,
            'clinic': str(actor.clinic_id) if actor.clinic_id else None,
            'clinic_name': actor.clinic.name if actor.clinic else None,
            'full_name': actor.get_full_name(),
            'force_password_change': actor.force_password_change,
        }
        return Response(payload)


class AuthLogoutView(APIView):
    permission_classes = [IsStaffRequest]

    def post(self, request) -> Response:
        return Response({'detail': 'Logged out.'})


class AuthChangePasswordView(APIView):
    permission_classes = [IsStaffRequest]

    def post(self, request) -> Response:
        actor_id = request.headers.get('X-User-Id')
        if not actor_id:
            return Response({'detail': 'Unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)

        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if not current_password or not new_password:
            return Response(
                {'detail': 'current_password and new_password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT password_hash
                FROM users
                WHERE id = %s AND is_active = TRUE
                """,
                [actor_id],
            )
            row = cursor.fetchone()

        if not row:
            return Response({'detail': 'Unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)

        current_hash = row[0]
        try:
            password_ok = bcrypt.checkpw(current_password.encode('utf-8'), current_hash.encode('utf-8'))
        except ValueError:
            password_ok = False

        if not password_ok:
            return Response({'detail': 'Current password is invalid.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 8:
            return Response({'detail': 'New password must be at least 8 characters.'}, status=status.HTTP_400_BAD_REQUEST)

        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET password_hash = %s,
                    force_password_change = FALSE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                [new_hash, actor_id],
            )
        return Response({'detail': 'Password changed successfully.'})


def _staff_actor_or_error(request):
    actor = _request_actor(request)
    if not actor:
        return None, Response({'detail': 'Unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)
    return actor, None


def _staff_clinic_or_error(actor: User):
    if not actor.clinic:
        return None, Response({'detail': 'No clinic assigned to this staff user.'}, status=status.HTTP_400_BAD_REQUEST)
    return actor.clinic, None


def _staff_action_allowed_or_error(actor: User, action: str):
    if not _has_role_access(actor, action):
        return Response({'detail': 'You do not have permission for this action.'}, status=status.HTTP_403_FORBIDDEN)
    return None


def _staff_clinic_for_request(actor: User, clinic_id: Optional[str]):
    if actor.role == User.UserRole.ADMIN:
        if clinic_id:
            clinic = get_object_or_404(Clinic, id=clinic_id)
            return clinic, None
        return None, Response({'detail': 'clinic is required for admin staff requests.'}, status=status.HTTP_400_BAD_REQUEST)
    clinic, error = _staff_clinic_or_error(actor)
    if error:
        return None, error
    if clinic_id and str(clinic.id) != str(clinic_id):
        return None, Response({'detail': 'Clinic scope mismatch.'}, status=status.HTTP_403_FORBIDDEN)
    return clinic, None


class StaffClinicView(APIView):
    permission_classes = [IsStaffRequest]

    def get(self, request) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        clinic, error = _staff_clinic_or_error(actor)
        if error:
            return error
        settings_obj, _ = ClinicSettings.objects.get_or_create(clinic=clinic)
        can_edit = _has_role_access(actor, 'settings_manage')
        return Response({
            'clinic': ClinicSerializer(clinic).data,
            'settings': ClinicSettingsSerializer(settings_obj).data,
            'permissions': {
                'can_edit_settings': can_edit,
                'can_manage_services': _has_role_access(actor, 'service_manage'),
                'role': actor.role,
            },
        })

    def patch(self, request) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'settings_manage')
        if denied:
            return denied
        clinic, error = _staff_clinic_or_error(actor)
        if error:
            return error
        allowed = {'name', 'street', 'city', 'state', 'zip_code', 'country', 'phone', 'email', 'logo', 'primary_color', 'secondary_color'}
        payload = {k: v for k, v in request.data.items() if k in allowed}
        if not payload:
            return Response({'detail': 'No editable clinic fields provided.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ClinicSerializer(clinic, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class StaffClinicSettingsView(APIView):
    permission_classes = [IsStaffRequest]

    def get(self, request) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        clinic, error = _staff_clinic_or_error(actor)
        if error:
            return error
        settings_obj, _ = ClinicSettings.objects.get_or_create(clinic=clinic)
        return Response(ClinicSettingsSerializer(settings_obj).data)

    def patch(self, request) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'settings_manage')
        if denied:
            return denied
        clinic, error = _staff_clinic_or_error(actor)
        if error:
            return error
        settings_obj, _ = ClinicSettings.objects.get_or_create(clinic=clinic)
        serializer = ClinicSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class StaffClinicKpiView(APIView):
    permission_classes = [IsStaffRequest]

    def get(self, request) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        clinic, error = _staff_clinic_or_error(actor)
        if error:
            return error

        target_date = _parse_iso_date(request.query_params.get('date'), timezone.localdate())
        queue = Queue.objects.filter(clinic=clinic, date=target_date).order_by('-created_at').first()
        if not queue:
            return Response({
                'date': target_date.isoformat(),
                'waiting': 0,
                'avg_wait': 0,
                'completed': 0,
                'no_show': 0,
            })
        queue.update_statistics()
        queue.save(update_fields=[
            'total_tickets', 'waiting', 'called', 'serving', 'completed',
            'cancelled', 'no_show', 'avg_wait_time', 'avg_service_time', 'current_wait_time'
        ])
        return Response({
            'date': target_date.isoformat(),
            'waiting': queue.waiting,
            'avg_wait': round(float(queue.avg_wait_time or 0), 2),
            'completed': queue.completed,
            'no_show': queue.no_show,
        })


class StaffQueuesView(APIView):
    permission_classes = [IsStaffRequest]

    def get(self, request) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        clinic_id = request.query_params.get('clinic')
        clinic, error = _staff_clinic_for_request(actor, clinic_id)
        if error:
            return error

        qs = Queue.objects.select_related('clinic')
        if clinic:
            qs = qs.filter(clinic=clinic)
        date = request.query_params.get('date')
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        if date:
            qs = qs.filter(date=_parse_iso_date(date, timezone.localdate()))
        else:
            if date_from:
                qs = qs.filter(date__gte=_parse_iso_date(date_from, timezone.localdate() - timedelta(days=30)))
            if date_to:
                qs = qs.filter(date__lte=_parse_iso_date(date_to, timezone.localdate()))
        qs = qs.order_by('-date', '-created_at')[:180]
        return Response(QueueSerializer(qs, many=True).data)


class StaffQueueOpenView(APIView):
    permission_classes = [IsStaffRequest]

    def post(self, request) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'queue_open')
        if denied:
            return denied
        clinic_id = request.data.get('clinic') or request.query_params.get('clinic')
        clinic, error = _staff_clinic_for_request(actor, clinic_id)
        if error:
            return error
        target_date = _parse_iso_date(request.data.get('date') or request.query_params.get('date'), timezone.localdate())
        queue, _ = Queue.objects.get_or_create(clinic=clinic, date=target_date, defaults={'is_active': True})
        if not queue.is_active:
            queue.open()
            queue.save(update_fields=['is_active', 'opened_at', 'closed_at', 'updated_at'])
            QueueEvent.objects.create(
                queue=queue,
                ticket=None,
                event_type=QueueEvent.QueueEventType.QUEUE_OPENED,
                user=actor,
                user_name=actor.get_full_name(),
                metadata={'message': 'Queue opened by staff endpoint'},
            )
        return Response(QueueSerializer(queue).data, status=status.HTTP_201_CREATED)


class StaffQueueCloseView(APIView):
    permission_classes = [IsStaffRequest]

    def post(self, request, queue_id: str) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'queue_close')
        if denied:
            return denied
        clinic, error = _staff_clinic_or_error(actor)
        if error:
            return error
        queue = get_object_or_404(Queue, id=queue_id, clinic=clinic)
        queue.close()
        queue.save(update_fields=['is_active', 'closed_at', 'updated_at'])
        QueueEvent.objects.create(
            queue=queue,
            ticket=None,
            event_type=QueueEvent.QueueEventType.QUEUE_CLOSED,
            user=actor,
            user_name=actor.get_full_name(),
            metadata={'message': 'Queue closed by staff endpoint'},
        )
        return Response(QueueSerializer(queue).data)


class StaffTicketsView(APIView):
    permission_classes = [IsStaffRequest]

    def get(self, request) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        clinic_id = request.query_params.get('clinic')
        clinic, error = _staff_clinic_for_request(actor, clinic_id)
        if error:
            return error

        qs = Ticket.objects.select_related('clinic', 'queue', 'service')
        if clinic:
            qs = qs.filter(clinic=clinic)
        queue_id = request.query_params.get('queue')
        status_value = request.query_params.get('status')
        service_id = request.query_params.get('service')
        search = request.query_params.get('search')
        date = request.query_params.get('date')
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        if queue_id:
            qs = qs.filter(queue_id=queue_id)
        if status_value:
            qs = qs.filter(status=status_value)
        if service_id:
            qs = qs.filter(service_id=service_id)
        if date:
            qs = qs.filter(queue__date=_parse_iso_date(date, timezone.localdate()))
        else:
            if date_from:
                qs = qs.filter(joined_at__date__gte=_parse_iso_date(date_from, timezone.localdate() - timedelta(days=30)))
            if date_to:
                qs = qs.filter(joined_at__date__lte=_parse_iso_date(date_to, timezone.localdate()))
        if search:
            qs = qs.filter(
                Q(ticket_number__icontains=search)
                | Q(patient_name__icontains=search)
                | Q(patient_phone__icontains=search)
            )
        qs = qs.order_by('-queue__date', 'position', 'joined_at')[:800]
        return Response(TicketSerializer(qs, many=True).data)


class StaffWalkinCreateView(APIView):
    permission_classes = [IsStaffRequest]

    def post(self, request) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'ticket_walkin')
        if denied:
            return denied
        clinic, error = _staff_clinic_or_error(actor)
        if error:
            return error
        settings_obj, _ = ClinicSettings.objects.get_or_create(clinic=clinic)
        if not settings_obj.allow_walkins:
            return Response({'detail': 'Walk-ins are disabled for this clinic.'}, status=status.HTTP_400_BAD_REQUEST)

        queue_id = request.data.get('queue')
        if queue_id:
            queue = get_object_or_404(Queue, id=queue_id, clinic=clinic)
        else:
            target_date = _parse_iso_date(request.data.get('date'), timezone.localdate())
            queue, _ = Queue.objects.get_or_create(clinic=clinic, date=target_date, defaults={'is_active': True})

        payload = {
            'clinic': str(clinic.id),
            'queue': str(queue.id),
            'patient_name': request.data.get('patient_name'),
            'patient_phone': request.data.get('patient_phone'),
            'patient_email': request.data.get('patient_email'),
            'service': request.data.get('service'),
            'is_walkin': True,
        }
        serializer = TicketSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()

        priority = request.data.get('priority') or Ticket.TicketPriority.NORMAL
        valid_priorities = {choice[0] for choice in Ticket.TicketPriority.choices}
        if priority not in valid_priorities:
            return Response({'detail': 'Invalid priority.'}, status=status.HTTP_400_BAD_REQUEST)
        notes = request.data.get('notes')
        patch_fields = []
        if ticket.priority != priority:
            ticket.priority = priority
            patch_fields.append('priority')
        if notes is not None:
            ticket.notes = notes
            patch_fields.append('notes')
        if patch_fields:
            patch_fields.append('updated_at')
            ticket.save(update_fields=patch_fields)
            queue.update_statistics()
            queue.save(update_fields=[
                'total_tickets', 'waiting', 'called', 'serving', 'completed',
                'cancelled', 'no_show', 'avg_wait_time', 'avg_service_time', 'current_wait_time'
            ])
        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)


def _get_staff_ticket(actor: User, ticket_id: str):
    clinic, error = _staff_clinic_or_error(actor)
    if error:
        return None, error
    ticket = get_object_or_404(Ticket.objects.select_related('queue', 'clinic'), id=ticket_id, clinic=clinic)
    return ticket, None


def _no_status_change(detail: str) -> Response:
    return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)


class StaffTicketCallView(APIView):
    permission_classes = [IsStaffRequest]

    def post(self, request, ticket_id: str) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'ticket_call')
        if denied:
            return denied
        ticket, error = _get_staff_ticket(actor, ticket_id)
        if error:
            return error
        before = ticket.status
        ticket.call(actor)
        ticket.save(update_fields=['status', 'called_at', 'called_by', 'updated_at'])
        if before == ticket.status:
            return _no_status_change('Ticket cannot be called from its current status.')
        return Response(TicketSerializer(ticket).data)


class StaffTicketStartView(APIView):
    permission_classes = [IsStaffRequest]

    def post(self, request, ticket_id: str) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'ticket_start')
        if denied:
            return denied
        ticket, error = _get_staff_ticket(actor, ticket_id)
        if error:
            return error
        before = ticket.status
        ticket.start_serving(actor)
        ticket.refresh_from_db()
        if before == ticket.status:
            return _no_status_change('Ticket cannot move to serving from its current status.')
        return Response(TicketSerializer(ticket).data)


class StaffTicketCompleteView(APIView):
    permission_classes = [IsStaffRequest]

    def post(self, request, ticket_id: str) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'ticket_complete')
        if denied:
            return denied
        ticket, error = _get_staff_ticket(actor, ticket_id)
        if error:
            return error
        before = ticket.status
        ticket.complete(actor)
        ticket.refresh_from_db()
        if before == ticket.status:
            return _no_status_change('Ticket cannot be completed from its current status.')
        return Response(TicketSerializer(ticket).data)


class StaffTicketCancelView(APIView):
    permission_classes = [IsStaffRequest]

    def post(self, request, ticket_id: str) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'ticket_cancel')
        if denied:
            return denied
        ticket, error = _get_staff_ticket(actor, ticket_id)
        if error:
            return error
        before = ticket.status
        ticket.cancel(actor, reason=request.data.get('reason'))
        ticket.refresh_from_db()
        if before == ticket.status:
            return _no_status_change('Ticket cannot be cancelled from its current status.')
        return Response(TicketSerializer(ticket).data)


class StaffTicketNoShowView(APIView):
    permission_classes = [IsStaffRequest]

    def post(self, request, ticket_id: str) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'ticket_no_show')
        if denied:
            return denied
        ticket, error = _get_staff_ticket(actor, ticket_id)
        if error:
            return error
        before = ticket.status
        ticket.mark_no_show(actor)
        ticket.refresh_from_db()
        if before == ticket.status:
            return _no_status_change('Ticket can only be marked no-show when currently called.')
        return Response(TicketSerializer(ticket).data)


class StaffTicketReorderView(APIView):
    permission_classes = [IsStaffRequest]

    def post(self, request, ticket_id: str) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'ticket_reorder')
        if denied:
            return denied
        ticket, error = _get_staff_ticket(actor, ticket_id)
        if error:
            return error
        if ticket.status != Ticket.TicketStatus.WAITING:
            return Response({'detail': 'Only waiting tickets can be reordered.'}, status=status.HTTP_400_BAD_REQUEST)

        direction = request.data.get('direction')
        requested_position = request.data.get('position')
        waiting = list(ticket.queue.tickets.filter(status=Ticket.TicketStatus.WAITING).order_by('position', 'joined_at'))
        ids = [str(t.id) for t in waiting]
        if str(ticket.id) not in ids:
            return Response({'detail': 'Ticket not found in waiting list.'}, status=status.HTTP_400_BAD_REQUEST)
        current_index = ids.index(str(ticket.id))

        target_index = current_index
        if direction == 'up':
            target_index = max(0, current_index - 1)
        elif direction == 'down':
            target_index = min(len(waiting) - 1, current_index + 1)
        elif requested_position is not None:
            try:
                target_index = max(0, min(len(waiting) - 1, int(requested_position) - 1))
            except (TypeError, ValueError):
                return Response({'detail': 'Invalid position value.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Provide direction (up/down) or position.'}, status=status.HTTP_400_BAD_REQUEST)

        if target_index == current_index:
            return Response(TicketSerializer(ticket).data)

        moving = waiting.pop(current_index)
        waiting.insert(target_index, moving)
        est_service_time = getattr(ticket.queue.clinic.settings, 'estimated_service_time', 15)

        with transaction.atomic():
            for idx, waiting_ticket in enumerate(waiting, start=1):
                waiting_ticket.position = idx
                waiting_ticket.estimated_wait_time = est_service_time * (idx - 1)
                waiting_ticket.save(update_fields=['position', 'estimated_wait_time', 'updated_at'])
            ticket.queue.update_statistics()
            ticket.queue.save(update_fields=[
                'total_tickets', 'waiting', 'called', 'serving', 'completed',
                'cancelled', 'no_show', 'avg_wait_time', 'avg_service_time', 'current_wait_time'
            ])
            QueueEvent.objects.create(
                queue=ticket.queue,
                ticket=ticket,
                event_type=QueueEvent.QueueEventType.TICKET_UPDATED,
                user=actor,
                user_name=actor.get_full_name(),
                metadata={'action': 'reorder', 'ticket_id': str(ticket.id), 'target_index': target_index + 1},
            )
        ticket.refresh_from_db()
        return Response(TicketSerializer(ticket).data)


class StaffTicketPatchView(APIView):
    permission_classes = [IsStaffRequest]

    def patch(self, request, ticket_id: str) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'ticket_update')
        if denied:
            return denied
        ticket, error = _get_staff_ticket(actor, ticket_id)
        if error:
            return error

        allowed = {'notes', 'service', 'priority'}
        payload = {k: v for k, v in request.data.items() if k in allowed}
        if not payload:
            return Response({'detail': 'No editable ticket fields provided.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'service' in payload and payload['service']:
            service = get_object_or_404(Service, id=payload['service'], clinic=ticket.clinic)
            ticket.service = service
        elif 'service' in payload:
            ticket.service = None

        if 'priority' in payload:
            valid_priorities = {choice[0] for choice in Ticket.TicketPriority.choices}
            if payload['priority'] not in valid_priorities:
                return Response({'detail': 'Invalid priority.'}, status=status.HTTP_400_BAD_REQUEST)
            ticket.priority = payload['priority']

        if 'notes' in payload:
            ticket.notes = payload['notes']

        ticket.save(update_fields=['service', 'priority', 'notes', 'updated_at'])
        QueueEvent.objects.create(
            queue=ticket.queue,
            ticket=ticket,
            event_type=QueueEvent.QueueEventType.TICKET_UPDATED,
            user=actor,
            user_name=actor.get_full_name(),
            metadata={'fields': list(payload.keys())},
        )
        return Response(TicketSerializer(ticket).data)


class StaffServicesView(APIView):
    permission_classes = [IsStaffRequest]

    def get(self, request) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        clinic, error = _staff_clinic_or_error(actor)
        if error:
            return error
        services = Service.objects.filter(clinic=clinic).order_by('display_order', 'name')
        return Response(ServiceSerializer(services, many=True).data)

    def post(self, request) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'service_manage')
        if denied:
            return denied
        clinic, error = _staff_clinic_or_error(actor)
        if error:
            return error
        payload = dict(request.data)
        payload['clinic'] = str(clinic.id)
        serializer = ServiceSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        service = serializer.save()
        return Response(ServiceSerializer(service).data, status=status.HTTP_201_CREATED)


class StaffServiceDetailView(APIView):
    permission_classes = [IsStaffRequest]

    def patch(self, request, service_id: str) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'service_manage')
        if denied:
            return denied
        clinic, error = _staff_clinic_or_error(actor)
        if error:
            return error
        service = get_object_or_404(Service, id=service_id, clinic=clinic)
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(ServiceSerializer(updated).data)

    def delete(self, request, service_id: str) -> Response:
        actor, error = _staff_actor_or_error(request)
        if error:
            return error
        denied = _staff_action_allowed_or_error(actor, 'service_manage')
        if denied:
            return denied
        clinic, error = _staff_clinic_or_error(actor)
        if error:
            return error
        service = get_object_or_404(Service, id=service_id, clinic=clinic)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IsAdminRequest(BasePermission):
    """Allow access for authenticated admins or role declared in request headers."""

    def has_permission(self, request, view) -> bool:
        user = getattr(request, 'user', None)
        if user and getattr(user, 'is_authenticated', False):
            return getattr(user, 'role', None) == User.UserRole.ADMIN
        return request.headers.get('X-User-Role') == User.UserRole.ADMIN


def _request_actor(request) -> Optional[User]:
    user = getattr(request, 'user', None)
    if user and getattr(user, 'is_authenticated', False):
        return user
    actor_id = request.headers.get('X-User-Id')
    if actor_id:
        return (
            User.objects
            .select_related('clinic')
            .only('id', 'clinic', 'email', 'first_name', 'last_name', 'role', 'is_active', 'force_password_change')
            .filter(id=actor_id)
            .first()
        )
    return None


def _log_admin_action(
    request,
    *,
    action_type: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    clinic: Optional[Clinic] = None,
    before_data: Optional[dict] = None,
    after_data: Optional[dict] = None,
    metadata: Optional[dict] = None,
) -> None:
    actor = _request_actor(request)
    AdminAuditLog.objects.create(
        actor=actor,
        actor_email=(actor.email if actor else request.headers.get('X-User-Email')),
        clinic=clinic,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        before_data=before_data,
        after_data=after_data,
        metadata=metadata,
    )


class AdminClinicListCreateView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request) -> Response:
        qs = Clinic.objects.select_related('settings').all()
        search = request.query_params.get('search')
        city = request.query_params.get('city')
        is_active = request.query_params.get('is_active')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(slug__icontains=search))
        if city:
            qs = qs.filter(city__icontains=city)
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        return Response(AdminClinicSerializer(qs.order_by('name'), many=True).data)

    def post(self, request) -> Response:
        serializer = AdminClinicSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        clinic = serializer.save()
        ClinicSettings.objects.get_or_create(clinic=clinic)
        _log_admin_action(
            request,
            action_type='clinic_created',
            entity_type='clinic',
            entity_id=str(clinic.id),
            clinic=clinic,
            after_data=AdminClinicSerializer(clinic).data,
        )
        return Response(AdminClinicSerializer(clinic).data, status=status.HTTP_201_CREATED)


class AdminClinicDetailView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request, pk: str) -> Response:
        clinic = get_object_or_404(Clinic.objects.select_related('settings'), id=pk)
        data = AdminClinicSerializer(clinic).data
        data['staff_count'] = clinic.users.count()
        data['services_count'] = clinic.services.count()
        return Response(data)

    def patch(self, request, pk: str) -> Response:
        clinic = get_object_or_404(Clinic, id=pk)
        before = AdminClinicSerializer(clinic).data
        serializer = AdminClinicSerializer(clinic, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        clinic = serializer.save()
        _log_admin_action(
            request,
            action_type='clinic_updated',
            entity_type='clinic',
            entity_id=str(clinic.id),
            clinic=clinic,
            before_data=before,
            after_data=AdminClinicSerializer(clinic).data,
        )
        return Response(AdminClinicSerializer(clinic).data)


class AdminClinicToggleActiveView(APIView):
    permission_classes = [IsAdminRequest]

    def post(self, request, pk: str) -> Response:
        clinic = get_object_or_404(Clinic, id=pk)
        before = {'is_active': clinic.is_active}
        clinic.is_active = not clinic.is_active
        clinic.save(update_fields=['is_active', 'updated_at'])
        after = {'is_active': clinic.is_active}
        _log_admin_action(
            request,
            action_type='clinic_toggled_active',
            entity_type='clinic',
            entity_id=str(clinic.id),
            clinic=clinic,
            before_data=before,
            after_data=after,
        )
        return Response({'id': str(clinic.id), 'is_active': clinic.is_active})


class AdminClinicLogoView(APIView):
    permission_classes = [IsAdminRequest]

    def post(self, request, pk: str) -> Response:
        clinic = get_object_or_404(Clinic, id=pk)
        logo = request.data.get('logo')
        if not logo:
            return Response({'detail': 'logo is required'}, status=status.HTTP_400_BAD_REQUEST)
        before = {'logo': clinic.logo}
        clinic.logo = logo
        clinic.save(update_fields=['logo', 'updated_at'])
        _log_admin_action(
            request,
            action_type='clinic_logo_updated',
            entity_type='clinic',
            entity_id=str(clinic.id),
            clinic=clinic,
            before_data=before,
            after_data={'logo': clinic.logo},
        )
        return Response({'id': str(clinic.id), 'logo': clinic.logo})


class AdminClinicBrandingView(APIView):
    permission_classes = [IsAdminRequest]

    def patch(self, request, pk: str) -> Response:
        clinic = get_object_or_404(Clinic, id=pk)
        allowed = {'primary_color', 'secondary_color', 'logo', 'cover_image'}
        patch_data = {k: v for k, v in request.data.items() if k in allowed}
        if not patch_data:
            return Response({'detail': 'No branding fields provided.'}, status=status.HTTP_400_BAD_REQUEST)
        before = {field: getattr(clinic, field) for field in allowed}
        for key, value in patch_data.items():
            setattr(clinic, key, value)
        clinic.save(update_fields=list(patch_data.keys()) + ['updated_at'])
        _log_admin_action(
            request,
            action_type='clinic_branding_updated',
            entity_type='clinic',
            entity_id=str(clinic.id),
            clinic=clinic,
            before_data=before,
            after_data={field: getattr(clinic, field) for field in allowed},
        )
        return Response(AdminClinicSerializer(clinic).data)


class AdminClinicRulesView(APIView):
    permission_classes = [IsAdminRequest]

    def patch(self, request, pk: str) -> Response:
        clinic = get_object_or_404(Clinic.objects.select_related('settings'), id=pk)
        settings_obj, _ = ClinicSettings.objects.get_or_create(clinic=clinic)
        before = AdminClinicSettingsPatchSerializer(settings_obj).data
        serializer = AdminClinicSettingsPatchSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        _log_admin_action(
            request,
            action_type='clinic_rules_updated',
            entity_type='clinic_settings',
            entity_id=str(settings_obj.id),
            clinic=clinic,
            before_data=before,
            after_data=AdminClinicSettingsPatchSerializer(settings_obj).data,
        )
        return Response(AdminClinicSettingsPatchSerializer(settings_obj).data)


class AdminClinicHoursView(APIView):
    permission_classes = [IsAdminRequest]

    def patch(self, request, pk: str) -> Response:
        clinic = get_object_or_404(Clinic.objects.select_related('settings'), id=pk)
        settings_obj, _ = ClinicSettings.objects.get_or_create(clinic=clinic)
        before = AdminHoursPatchSerializer(settings_obj).data
        serializer = AdminHoursPatchSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        _log_admin_action(
            request,
            action_type='clinic_hours_updated',
            entity_type='clinic_settings',
            entity_id=str(settings_obj.id),
            clinic=clinic,
            before_data=before,
            after_data=AdminHoursPatchSerializer(settings_obj).data,
        )
        return Response(AdminHoursPatchSerializer(settings_obj).data)


class AdminClinicServicesView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request, pk: str) -> Response:
        clinic = get_object_or_404(Clinic, id=pk)
        qs = clinic.services.order_by('display_order', 'name')
        return Response(AdminServiceSerializer(qs, many=True).data)

    def post(self, request, pk: str) -> Response:
        clinic = get_object_or_404(Clinic, id=pk)
        payload = dict(request.data)
        payload['clinic'] = str(clinic.id)
        serializer = AdminServiceSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        service = serializer.save()
        _log_admin_action(
            request,
            action_type='service_created',
            entity_type='service',
            entity_id=str(service.id),
            clinic=clinic,
            after_data=AdminServiceSerializer(service).data,
        )
        return Response(AdminServiceSerializer(service).data, status=status.HTTP_201_CREATED)


class AdminServiceDetailView(APIView):
    permission_classes = [IsAdminRequest]

    def patch(self, request, service_id: str) -> Response:
        service = get_object_or_404(Service, id=service_id)
        before = AdminServiceSerializer(service).data
        serializer = AdminServiceSerializer(service, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        service = serializer.save()
        _log_admin_action(
            request,
            action_type='service_updated',
            entity_type='service',
            entity_id=str(service.id),
            clinic=service.clinic,
            before_data=before,
            after_data=AdminServiceSerializer(service).data,
        )
        return Response(AdminServiceSerializer(service).data)

    def delete(self, request, service_id: str) -> Response:
        service = get_object_or_404(Service, id=service_id)
        before = AdminServiceSerializer(service).data
        clinic = service.clinic
        entity_id = str(service.id)
        service.delete()
        _log_admin_action(
            request,
            action_type='service_deleted',
            entity_type='service',
            entity_id=entity_id,
            clinic=clinic,
            before_data=before,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminServiceReorderView(APIView):
    permission_classes = [IsAdminRequest]

    def post(self, request) -> Response:
        ordered_ids = request.data.get('service_ids')
        if not isinstance(ordered_ids, list) or not ordered_ids:
            return Response({'detail': 'service_ids list is required.'}, status=status.HTTP_400_BAD_REQUEST)
        services = list(Service.objects.filter(id__in=ordered_ids))
        services_map = {str(s.id): s for s in services}
        for idx, sid in enumerate(ordered_ids, start=1):
            service = services_map.get(str(sid))
            if service:
                service.display_order = idx
                service.save(update_fields=['display_order', 'updated_at'])
        _log_admin_action(
            request,
            action_type='service_reordered',
            entity_type='service',
            metadata={'service_ids': ordered_ids},
        )
        return Response({'detail': 'Services reordered.'})


class AdminUsersListCreateView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request) -> Response:
        role = request.query_params.get('role')
        clinic = request.query_params.get('clinic')
        is_active = request.query_params.get('is_active')
        query = """
            SELECT
                u.id,
                u.email,
                u.first_name,
                u.last_name,
                u.phone_number,
                u.role,
                u.clinic_id,
                c.name AS clinic_name,
                u.is_active,
                u.force_password_change,
                u.created_at,
                u.updated_at,
                u.last_login_at
            FROM users u
            LEFT JOIN clinics c ON c.id = u.clinic_id
            WHERE 1=1
        """
        params: list = []
        if role:
            query += " AND u.role = %s"
            params.append(role)
        if clinic:
            query += " AND u.clinic_id = %s"
            params.append(clinic)
        if is_active is not None:
            query += " AND u.is_active = %s"
            params.append(is_active.lower() == 'true')
        query += " ORDER BY u.first_name ASC, u.last_name ASC"

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

        users = []
        for row in rows:
            users.append({
                'id': str(row[0]),
                'email': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'phone_number': row[4],
                'role': row[5],
                'clinic': str(row[6]) if row[6] else None,
                'clinic_name': row[7],
                'is_active': row[8],
                'force_password_change': row[9],
                'full_name': f"{row[2]} {row[3]}".strip(),
                'date_joined': row[10].isoformat() if row[10] else None,
                'updated_at': row[11].isoformat() if row[11] else None,
                'last_login_at': row[12].isoformat() if row[12] else None,
            })
        return Response(users)

    def post(self, request) -> Response:
        payload = dict(request.data)
        temp_password = payload.pop('temp_password', None) or _generate_temp_password()
        payload.setdefault('is_active', True)
        serializer = UserSerializer(data={**payload, 'password': temp_password})
        serializer.is_valid(raise_exception=True)
        user = serializer.save(force_password_change=True)
        _log_admin_action(
            request,
            action_type='user_created',
            entity_type='user',
            entity_id=str(user.id),
            clinic=user.clinic,
            after_data=AdminUserSerializer(user).data,
        )
        data = AdminUserSerializer(user).data
        data['temp_password'] = temp_password
        return Response(data, status=status.HTTP_201_CREATED)


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request, pk: str) -> Response:
        user = get_object_or_404(User.objects.select_related('clinic'), id=pk)
        return Response(AdminUserSerializer(user).data)

    def patch(self, request, pk: str) -> Response:
        user = get_object_or_404(User, id=pk)
        before = AdminUserSerializer(user).data
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        _log_admin_action(
            request,
            action_type='user_updated',
            entity_type='user',
            entity_id=str(user.id),
            clinic=user.clinic,
            before_data=before,
            after_data=AdminUserSerializer(user).data,
        )
        return Response(AdminUserSerializer(user).data)


class AdminUserToggleActiveView(APIView):
    permission_classes = [IsAdminRequest]

    def post(self, request, pk: str) -> Response:
        user = get_object_or_404(User, id=pk)
        before = {'is_active': user.is_active}
        user.is_active = not user.is_active
        user.save(update_fields=['is_active', 'updated_at'])
        _log_admin_action(
            request,
            action_type='user_toggled_active',
            entity_type='user',
            entity_id=str(user.id),
            clinic=user.clinic,
            before_data=before,
            after_data={'is_active': user.is_active},
        )
        return Response({'id': str(user.id), 'is_active': user.is_active})


class AdminUserResetPasswordView(APIView):
    permission_classes = [IsAdminRequest]

    def post(self, request, pk: str) -> Response:
        user = get_object_or_404(User, id=pk)
        temp_password = _generate_temp_password()
        user.set_password(temp_password)
        user.force_password_change = True
        user.save(update_fields=['password', 'force_password_change', 'updated_at'])
        _log_admin_action(
            request,
            action_type='user_password_reset',
            entity_type='user',
            entity_id=str(user.id),
            clinic=user.clinic,
            metadata={'forced_password_change': True},
        )
        return Response({'id': str(user.id), 'temp_password': temp_password, 'force_password_change': True})


class AdminUserSetRoleView(APIView):
    permission_classes = [IsAdminRequest]

    def post(self, request, pk: str) -> Response:
        user = get_object_or_404(User, id=pk)
        role = request.data.get('role')
        valid_roles = {choice[0] for choice in User.UserRole.choices}
        if role not in valid_roles:
            return Response({'detail': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)
        before = {'role': user.role}
        user.role = role
        user.save(update_fields=['role', 'updated_at'])
        _log_admin_action(
            request,
            action_type='user_role_changed',
            entity_type='user',
            entity_id=str(user.id),
            clinic=user.clinic,
            before_data=before,
            after_data={'role': user.role},
        )
        return Response({'id': str(user.id), 'role': user.role})


class AdminUserAssignClinicView(APIView):
    permission_classes = [IsAdminRequest]

    def post(self, request, pk: str) -> Response:
        user = get_object_or_404(User, id=pk)
        clinic_id = request.data.get('clinic')
        clinic = None
        if clinic_id:
            clinic = get_object_or_404(Clinic, id=clinic_id)
        before = {'clinic': str(user.clinic_id) if user.clinic_id else None}
        user.clinic = clinic
        user.save(update_fields=['clinic', 'updated_at'])
        _log_admin_action(
            request,
            action_type='user_clinic_assigned',
            entity_type='user',
            entity_id=str(user.id),
            clinic=clinic,
            before_data=before,
            after_data={'clinic': str(user.clinic_id) if user.clinic_id else None},
        )
        return Response(AdminUserSerializer(user).data)


def _parse_date_range(request):
    today = timezone.localdate()
    earliest_queue = Queue.objects.order_by('date').values_list('date', flat=True).first()
    earliest_ticket = Ticket.objects.order_by('joined_at').values_list('joined_at', flat=True).first()
    earliest_ticket_date = earliest_ticket.date() if earliest_ticket else None
    if earliest_queue and earliest_ticket_date:
        default_from = min(earliest_queue, earliest_ticket_date)
    else:
        default_from = earliest_queue or earliest_ticket_date or (today - timedelta(days=30))
    from_param = request.query_params.get('from')
    to_param = request.query_params.get('to')
    try:
        from_date = timezone.datetime.fromisoformat(from_param).date() if from_param else default_from
    except ValueError:
        from_date = default_from
    try:
        to_date = timezone.datetime.fromisoformat(to_param).date() if to_param else today
    except ValueError:
        to_date = today
    return from_date, to_date


class AdminAnalyticsOverviewView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request) -> Response:
        from_date, to_date = _parse_date_range(request)
        queues = Queue.objects.filter(date__range=[from_date, to_date])
        tickets = Ticket.objects.filter(joined_at__date__range=[from_date, to_date])
        total_tickets = tickets.count()
        avg_wait = queues.aggregate(v=Avg('avg_wait_time'))['v'] or 0
        active_clinics = Clinic.objects.filter(is_active=True).count()
        no_show_count = tickets.filter(status=Ticket.TicketStatus.NO_SHOW).count()
        no_show_rate = (no_show_count / total_tickets * 100) if total_tickets else 0
        today = timezone.localdate()
        week_start = today - timedelta(days=6)
        month_start = today.replace(day=1)
        today_tickets = Ticket.objects.filter(joined_at__date=today).count()
        week_tickets = Ticket.objects.filter(joined_at__date__range=[week_start, today]).count()
        month_tickets = Ticket.objects.filter(joined_at__date__range=[month_start, today]).count()
        top_clinics = (
            Queue.objects.filter(date__range=[from_date, to_date])
            .values(name=F('clinic__name'))
            .annotate(total=Sum('total_tickets'))
            .order_by('-total')[:5]
        )
        status_counts = (
            tickets.values('status')
            .annotate(total=Count('id'))
            .order_by('status')
        )
        priority_counts = (
            tickets.values('priority')
            .annotate(total=Count('id'))
            .order_by('priority')
        )
        users_total = User.objects.count()
        users_active = User.objects.filter(is_active=True).count()
        services_total = Service.objects.count()
        queues_total = Queue.objects.count()
        notifications_total = Notification.objects.count()
        notifications_delivered = Notification.objects.filter(status=Notification.NotificationStatus.DELIVERED).count()
        notification_delivery_rate = (
            (notifications_delivered / notifications_total * 100) if notifications_total else 0
        )
        return Response({
            'from': from_date.isoformat(),
            'to': to_date.isoformat(),
            'total_clinics': Clinic.objects.count(),
            'active_clinics': active_clinics,
            'tickets_today': today_tickets,
            'tickets_week': week_tickets,
            'tickets_month': month_tickets,
            'total_tickets': total_tickets,
            'total_queues': queues_total,
            'total_users': users_total,
            'active_users': users_active,
            'total_services': services_total,
            'avg_wait_time': round(float(avg_wait), 2),
            'no_show_rate': round(no_show_rate, 2),
            'notifications_total': notifications_total,
            'notifications_delivery_rate': round(notification_delivery_rate, 2),
            'status_counts': list(status_counts),
            'priority_counts': list(priority_counts),
            'system_status': {
                'api': 'UP',
                'db': 'UP',
                'websocket': 'UNKNOWN',
            },
            'top_clinics': list(top_clinics),
        })


class AdminAnalyticsClinicRankingView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request) -> Response:
        from_date, to_date = _parse_date_range(request)
        ranking = (
            Queue.objects.filter(date__range=[from_date, to_date])
            .values('clinic_id', 'clinic__name')
            .annotate(total_tickets=Sum('total_tickets'), avg_wait=Avg('avg_wait_time'))
            .order_by('-total_tickets')
        )
        return Response(list(ranking))


class AdminAnalyticsTicketsTimeseriesView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request) -> Response:
        from_date, to_date = _parse_date_range(request)
        group = request.query_params.get('group', 'day')
        if group == 'week':
            rows = (
                Ticket.objects.filter(joined_at__date__range=[from_date, to_date])
                .extra(select={'bucket': "DATE_TRUNC('week', joined_at)"})
                .values('bucket')
                .annotate(total=Count('id'))
                .order_by('bucket')
            )
            data = [{'bucket': r['bucket'].date().isoformat(), 'total': r['total']} for r in rows]
        else:
            rows = (
                Ticket.objects.filter(joined_at__date__range=[from_date, to_date])
                .values('joined_at__date')
                .annotate(total=Count('id'))
                .order_by('joined_at__date')
            )
            data = [{'bucket': r['joined_at__date'].isoformat(), 'total': r['total']} for r in rows]
        return Response(data)


class AdminAnalyticsStatusDistributionView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request) -> Response:
        from_date, to_date = _parse_date_range(request)
        rows = (
            Ticket.objects.filter(joined_at__date__range=[from_date, to_date])
            .values('status')
            .annotate(total=Count('id'))
            .order_by('status')
        )
        return Response(list(rows))


class AdminAnalyticsPeakHoursView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request) -> Response:
        from_date, to_date = _parse_date_range(request)
        rows = (
            Ticket.objects.filter(joined_at__date__range=[from_date, to_date])
            .extra(
                select={
                    'hour': "EXTRACT(HOUR FROM joined_at)",
                    'weekday': "EXTRACT(DOW FROM joined_at)",
                }
            )
            .values('hour', 'weekday')
            .annotate(total=Count('id'))
            .order_by('weekday', 'hour')
        )
        return Response(list(rows))


class AdminAnalyticsExportCsvView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request) -> HttpResponse:
        from_date, to_date = _parse_date_range(request)
        rows = (
            Queue.objects.filter(date__range=[from_date, to_date])
            .values('date', 'clinic__name', 'total_tickets', 'avg_wait_time', 'avg_service_time', 'no_show')
            .order_by('date', 'clinic__name')
        )
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="admin-analytics.csv"'
        writer = csv.writer(response)
        writer.writerow(['date', 'clinic', 'total_tickets', 'avg_wait_time', 'avg_service_time', 'no_show'])
        for row in rows:
            writer.writerow([
                row['date'],
                row['clinic__name'],
                row['total_tickets'],
                row['avg_wait_time'],
                row['avg_service_time'],
                row['no_show'],
            ])
        return response


def _simple_pdf_bytes(title: str, lines: list[str]) -> bytes:
    safe_lines = [line.replace('(', '[').replace(')', ']') for line in lines]
    content = f"BT /F1 14 Tf 50 780 Td ({title}) Tj ET\n"
    y = 760
    for line in safe_lines:
        content += f"BT /F1 10 Tf 50 {y} Td ({line[:110]}) Tj ET\n"
        y -= 14
        if y < 60:
            break
    stream = content.encode('latin-1', errors='ignore')
    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    objects.append(b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n")
    objects.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
    objects.append(f"5 0 obj << /Length {len(stream)} >> stream\n".encode('latin-1') + stream + b"endstream endobj\n")
    pdf = b"%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf += obj
    xref_start = len(pdf)
    pdf += f"xref\n0 {len(offsets)}\n".encode('latin-1')
    pdf += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        pdf += f"{off:010d} 00000 n \n".encode('latin-1')
    pdf += f"trailer << /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode('latin-1')
    return pdf


class AdminAnalyticsExportPdfView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request) -> HttpResponse:
        overview = AdminAnalyticsOverviewView().get(request).data
        lines = [
            f"Date range: {overview['from']} -> {overview['to']}",
            f"Total clinics: {overview['total_clinics']}",
            f"Active clinics: {overview['active_clinics']}",
            f"Tickets today/week/month: {overview['tickets_today']}/{overview['tickets_week']}/{overview['tickets_month']}",
            f"Average wait time: {overview['avg_wait_time']} minutes",
            f"No-show rate: {overview['no_show_rate']}%",
        ]
        pdf = _simple_pdf_bytes("QueueLess Admin Summary", lines)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="admin-summary.pdf"'
        return response


class AdminAuditLogsListView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request) -> Response:
        qs = AdminAuditLog.objects.select_related('actor', 'clinic').all()
        actor = request.query_params.get('actor')
        clinic = request.query_params.get('clinic')
        action = request.query_params.get('action')
        from_date, to_date = _parse_date_range(request)
        if actor:
            qs = qs.filter(Q(actor_id=actor) | Q(actor_email__icontains=actor))
        if clinic:
            qs = qs.filter(clinic_id=clinic)
        if action:
            qs = qs.filter(action_type__icontains=action)
        qs = qs.filter(created_at__date__range=[from_date, to_date])
        return Response(AdminAuditLogSerializer(qs[:300], many=True).data)


class AdminAuditLogDetailView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request, pk: str) -> Response:
        log = get_object_or_404(AdminAuditLog.objects.select_related('actor', 'clinic'), id=pk)
        return Response(AdminAuditLogSerializer(log).data)


def _get_or_create_system_settings() -> SystemSettings:
    settings_obj = SystemSettings.objects.order_by('created_at').first()
    if settings_obj:
        return settings_obj
    return SystemSettings.objects.create(
        default_queue_rules={
            'max_capacity': 50,
            'estimated_service_time': 15,
            'allow_walkins': True,
        },
        allowed_countries=['Tunisia'],
        allowed_phone_formats=['+216########'],
    )


class AdminSystemSettingsView(APIView):
    permission_classes = [IsAdminRequest]

    def get(self, request) -> Response:
        settings_obj = _get_or_create_system_settings()
        return Response(SystemSettingsSerializer(settings_obj).data)

    def patch(self, request) -> Response:
        settings_obj = _get_or_create_system_settings()
        before = SystemSettingsSerializer(settings_obj).data
        serializer = SystemSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save(updated_by=_request_actor(request))
        _log_admin_action(
            request,
            action_type='system_settings_updated',
            entity_type='system_settings',
            entity_id=str(updated.id),
            before_data=before,
            after_data=SystemSettingsSerializer(updated).data,
        )
        return Response(SystemSettingsSerializer(updated).data)


class AdminSystemSettingsTestNotificationView(APIView):
    permission_classes = [IsAdminRequest]

    def post(self, request) -> Response:
        target = request.data.get('target') or 'test@localhost'
        channel = request.data.get('channel') or 'EMAIL'
        _log_admin_action(
            request,
            action_type='system_test_notification',
            entity_type='system_settings',
            metadata={'target': target, 'channel': channel},
        )
        return Response({'detail': f'Test {channel} notification queued for {target}.'})


def _generate_temp_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(secrets.choice(alphabet) for _ in range(length))