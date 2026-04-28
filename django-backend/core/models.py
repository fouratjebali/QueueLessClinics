"""
Database models for the QueueLess backend.

These models mirror the PostgreSQL schema defined in ``schema.sql``
and include additional convenience methods for queue management. The
primary keys are UUIDs to align with the existing SQL and to avoid
accidental leakage of predictable IDs. Enumerations are modelled
using Django's ``TextChoices`` to provide readable values and
validation.
"""

from __future__ import annotations

import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager using email as the unique identifier."""

    def create_user(self, email: str, password: str | None = None, **extra_fields) -> 'User':
        """Create and return a regular user.

        Email is required. Password may be omitted; in this case the
        user will not be able to log in without resetting their
        password via the admin. Additional fields are passed through
        directly to the model constructor.
        """
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields) -> 'User':
        """Create and return a superuser.

        Superusers have admin privileges and can access the Django admin.
        They default to the ``ADMIN`` role and have ``is_staff`` and
        ``is_superuser`` flags set to ``True``.
        """
        extra_fields.setdefault('role', User.UserRole.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Clinic(models.Model):
    """Healthcare clinic or facility.

    This model stores metadata about each clinic including contact
    information, address, branding and whether it is currently active.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    # Address
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Tunisia')
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    # Contact
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.CharField(max_length=255, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)
    timezone = models.CharField(max_length=64, default='Africa/Tunis')
    # Branding
    logo = models.TextField(blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#1e88e5')
    secondary_color = models.CharField(max_length=7, default='#4caf50')
    cover_image = models.TextField(blank=True, null=True)
    # Status
    is_active = models.BooleanField(default=True)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clinics'
        indexes = [
            models.Index(fields=['slug'], name='idx_clinics_slug'),
            models.Index(fields=['is_active'], name='idx_clinics_is_active'),
        ]
        verbose_name = 'Clinic'
        verbose_name_plural = 'Clinics'

    def __str__(self) -> str:
        return self.name


def default_operating_hours() -> dict:
    """Return default operating hours for a clinic settings entry.

    This function returns a dictionary matching the JSON format used in
    the SQL schema. Each weekday has an ``isOpen`` flag and optional
    opening and closing times. When stored in the database this
    becomes a JSON column (``JSONField``).
    """
    return {
        "monday": {"isOpen": True, "openTime": "08:00", "closeTime": "17:00"},
        "tuesday": {"isOpen": True, "openTime": "08:00", "closeTime": "17:00"},
        "wednesday": {"isOpen": True, "openTime": "08:00", "closeTime": "17:00"},
        "thursday": {"isOpen": True, "openTime": "08:00", "closeTime": "17:00"},
        "friday": {"isOpen": True, "openTime": "08:00", "closeTime": "17:00"},
        "saturday": {"isOpen": False, "openTime": "09:00", "closeTime": "13:00"},
        "sunday": {"isOpen": False, "openTime": "09:00", "closeTime": "13:00"},
    }


class ClinicSettings(models.Model):
    """Configuration and preferences for each clinic.

    There is a one‑to‑one relationship between a clinic and its settings.
    This model stores queue capacities, notification preferences and
    display options. Many fields mirror the original SQL schema but
    sensible defaults are provided for easier setup.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.OneToOneField(Clinic, on_delete=models.CASCADE, related_name='settings')
    operating_hours = models.JSONField(default=default_operating_hours)
    # Queue settings
    max_capacity = models.IntegerField(default=50)
    allow_walkins = models.BooleanField(default=True)
    allow_online_joining = models.BooleanField(default=True)
    auto_call_next = models.BooleanField(default=False)
    estimated_service_time = models.IntegerField(default=15)  # minutes
    emergency_priority_rules = models.JSONField(default=dict, blank=True)
    warning_threshold = models.IntegerField(default=80)  # percentage
    closed_message = models.TextField(blank=True, null=True)
    # Notification settings
    enable_sms = models.BooleanField(default=True)
    enable_email = models.BooleanField(default=True)
    reminder_before_minutes = models.IntegerField(default=10)
    ready_notification = models.BooleanField(default=True)
    missed_turn_notification = models.BooleanField(default=True)
    # Display settings
    show_estimated_wait_time = models.BooleanField(default=True)
    show_queue_position = models.BooleanField(default=True)
    show_people_ahead = models.BooleanField(default=True)
    # Stored as TEXT[] in PostgreSQL schema; use ArrayField for compatibility.
    display_languages = ArrayField(models.CharField(max_length=10), default=list)
    custom_welcome_message = models.TextField(blank=True, null=True)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clinic_settings'
        verbose_name = 'Clinic Settings'
        verbose_name_plural = 'Clinic Settings'

    def __str__(self) -> str:
        return f"Settings for {self.clinic.name}"


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user representing staff and administrative accounts.

    Users authenticate via e‑mail addresses and have roles defined by
    the ``UserRole`` enumeration. Each user may optionally be
    associated with a clinic. Roles govern access to different parts
    of the application but fine‑grained permissions should be
    enforced at the view level (see ``permissions.py``).
    """

    class UserRole(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        STAFF = 'STAFF', 'Staff'
        DOCTOR = 'DOCTOR', 'Doctor'
        NURSE = 'NURSE', 'Nurse'
        RECEPTIONIST = 'RECEPTIONIST', 'Receptionist'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.STAFF)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    force_password_change = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    objects: UserManager = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email'], name='idx_users_email'),
            models.Index(fields=['clinic'], name='idx_users_clinic_id'),
            models.Index(fields=['role'], name='idx_users_role'),
            models.Index(fields=['is_active'], name='idx_users_is_active'),
        ]
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def save(self, *args, **kwargs) -> None:
        # Keep last_login_at in sync when last_login field updates via
        # Django's authentication backend. ``last_login`` comes from
        # ``AbstractBaseUser``.
        if self.last_login and not self.last_login_at:
            self.last_login_at = self.last_login
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.get_full_name() or self.email

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        return self.first_name


class Service(models.Model):
    """Medical service offered by a clinic.

    Services describe procedures such as consultations, vaccinations or
    laboratory work. Each service belongs to a specific clinic and
    includes an estimated duration used when calculating wait times.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    estimated_duration = models.IntegerField(default=15)
    code = models.CharField(max_length=50, blank=True, null=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'services'
        indexes = [
            models.Index(fields=['clinic'], name='idx_services_clinic_id'),
            models.Index(fields=['is_active'], name='idx_services_is_active'),
            models.Index(fields=['clinic', 'display_order'], name='idx_services_display_order'),
        ]
        ordering = ['clinic', 'display_order']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self) -> str:
        return self.name


class Queue(models.Model):
    """Daily queue for a clinic.

    Each queue corresponds to a specific day and clinic. It tracks
    aggregated statistics for the tickets in that queue and exposes
    helper methods to update those statistics when tickets change
    state. Only one queue per clinic per day may exist (see
    ``unique_together``).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='queues')
    date = models.DateField()
    is_active = models.BooleanField(default=True)
    opened_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    # Statistics
    total_tickets = models.IntegerField(default=0)
    waiting = models.IntegerField(default=0)
    called = models.IntegerField(default=0)
    serving = models.IntegerField(default=0)
    completed = models.IntegerField(default=0)
    cancelled = models.IntegerField(default=0)
    no_show = models.IntegerField(default=0)
    avg_wait_time = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_service_time = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_wait_time = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'queues'
        unique_together = [('clinic', 'date')]
        indexes = [
            models.Index(fields=['clinic'], name='idx_queues_clinic_id'),
            models.Index(fields=['date'], name='idx_queues_date'),
            models.Index(fields=['is_active'], name='idx_queues_is_active'),
            models.Index(fields=['clinic', 'date'], name='idx_queues_clinic_date'),
        ]
        ordering = ['clinic__name', 'date']
        verbose_name = 'Queue'
        verbose_name_plural = 'Queues'

    def __str__(self) -> str:
        return f"Queue for {self.clinic.name} on {self.date.isoformat()}"

    def open(self, opened_at: timezone.datetime | None = None) -> None:
        """Mark the queue as opened and log an event.

        If the queue was previously closed this resets its status. The
        ``opened_at`` timestamp defaults to now. Calling this method
        does not commit any changes; callers should save the model.
        """
        self.is_active = True
        self.opened_at = opened_at or timezone.now()
        self.closed_at = None

    def close(self, closed_at: timezone.datetime | None = None) -> None:
        """Mark the queue as closed and log an event.

        The ``closed_at`` timestamp defaults to now. Once closed no
        additional tickets should be accepted for this queue. Calling
        this method does not commit any changes; callers should save
        the model.
        """
        self.is_active = False
        self.closed_at = closed_at or timezone.now()

    def update_statistics(self) -> None:
        """Recalculate and persist queue statistics.

        This method aggregates the underlying tickets table to update
        counts and averages. It should be called whenever tickets are
        created or change status. For performance reasons the
        aggregation is done in Python; for large datasets you may
        prefer to issue raw SQL queries.
        """
        qs = self.tickets.all()
        now_value = timezone.now()
        if timezone.is_aware(now_value):
            now_naive = timezone.make_naive(now_value, timezone.get_current_timezone())
        else:
            now_naive = now_value
        self.total_tickets = qs.count()
        self.waiting = qs.filter(status=Ticket.TicketStatus.WAITING).count()
        self.called = qs.filter(status=Ticket.TicketStatus.CALLED).count()
        self.serving = qs.filter(status=Ticket.TicketStatus.SERVING).count()
        self.completed = qs.filter(status=Ticket.TicketStatus.COMPLETED).count()
        self.cancelled = qs.filter(status=Ticket.TicketStatus.CANCELLED).count()
        self.no_show = qs.filter(status=Ticket.TicketStatus.NO_SHOW).count()
        # Average wait time is the mean of difference between called_at and joined_at
        wait_durations: list[int] = []
        for t in qs.exclude(called_at__isnull=True):
            delta = t.called_at - t.joined_at
            wait_durations.append(int(delta.total_seconds() // 60))
        if wait_durations:
            self.avg_wait_time = sum(wait_durations) / len(wait_durations)
            # Current wait time approximates the difference between now and
            # the oldest waiting ticket's join time.
            waiting_tickets = qs.filter(status=Ticket.TicketStatus.WAITING).order_by('joined_at')
            if waiting_tickets.exists():
                delta = now_naive - waiting_tickets.first().joined_at
                self.current_wait_time = int(delta.total_seconds() // 60)
        # Average service time is the mean of difference between completed_at and serving_started_at
        service_durations: list[int] = []
        for t in qs.exclude(serving_started_at__isnull=True).exclude(completed_at__isnull=True):
            delta = t.completed_at - t.serving_started_at
            service_durations.append(int(delta.total_seconds() // 60))
        if service_durations:
            self.avg_service_time = sum(service_durations) / len(service_durations)


class Ticket(models.Model):
    """Individual patient ticket in a queue.

    Tickets represent a patient's place in line. They carry contact
    details and track progress through the queue. Helper methods
    encapsulate state transitions such as calling, serving, completing
    or cancelling a ticket.
    """

    class TicketStatus(models.TextChoices):
        WAITING = 'WAITING', 'Waiting'
        CALLED = 'CALLED', 'Called'
        SERVING = 'SERVING', 'Serving'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        NO_SHOW = 'NO_SHOW', 'No show'

    class TicketPriority(models.TextChoices):
        NORMAL = 'NORMAL', 'Normal'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name='tickets')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='tickets')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    ticket_number = models.CharField(max_length=10)
    patient_name = models.CharField(max_length=255)
    patient_phone = models.CharField(max_length=20)
    patient_email = models.EmailField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=TicketStatus.choices, default=TicketStatus.WAITING)
    priority = models.CharField(max_length=20, choices=TicketPriority.choices, default=TicketPriority.NORMAL)
    position = models.IntegerField()
    estimated_wait_time = models.IntegerField(default=0)
    is_walkin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(default=timezone.now)
    called_at = models.DateTimeField(blank=True, null=True)
    serving_started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    # Underlying DB columns are ``called_by`` and ``served_by`` (UUID FKs),
    # so we map the Django ForeignKey fields explicitly to those names.
    called_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='called_tickets',
        db_column='called_by',
    )
    served_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='served_tickets',
        db_column='served_by',
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tickets'
        indexes = [
            models.Index(fields=['queue'], name='idx_tickets_queue_id'),
            models.Index(fields=['clinic'], name='idx_tickets_clinic_id'),
            models.Index(fields=['ticket_number'], name='idx_tickets_ticket_number'),
            models.Index(fields=['status'], name='idx_tickets_status'),
            models.Index(fields=['queue', 'position'], name='idx_tickets_position'),
            models.Index(fields=['created_at'], name='idx_tickets_created_at'),
        ]
        ordering = ['queue', 'position']
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'

    def __str__(self) -> str:
        return f"{self.ticket_number} - {self.patient_name}"

    def call(self, user: User | None = None) -> None:
        """Call the patient: update status, assign caller, set timestamp and log event."""
        if self.status != self.TicketStatus.WAITING:
            return
        self.status = self.TicketStatus.CALLED
        self.called_at = timezone.now()
        self.called_by = user
        # update queue counts
        q = self.queue
        q.update_statistics()
        q.save(update_fields=[
            'waiting', 'called', 'serving', 'completed', 'cancelled', 'no_show',
            'avg_wait_time', 'current_wait_time', 'total_tickets', 'avg_service_time'
        ])
        QueueEvent.objects.create(
            queue=q,
            ticket=self,
            event_type=QueueEvent.QueueEventType.TICKET_CALLED,
            user=user,
            user_name=user.get_full_name() if user else 'System',
            metadata={'ticket_number': self.ticket_number},
        )

    def start_serving(self, user: User) -> None:
        """Begin serving the patient."""
        if self.status not in (self.TicketStatus.CALLED, self.TicketStatus.WAITING):
            return
        self.status = self.TicketStatus.SERVING
        self.serving_started_at = timezone.now()
        self.served_by = user
        self.save(update_fields=['status', 'serving_started_at', 'served_by'])
        # update statistics and log event
        self.queue.update_statistics()
        self.queue.save(update_fields=['serving'])
        QueueEvent.objects.create(
            queue=self.queue,
            ticket=self,
            event_type=QueueEvent.QueueEventType.TICKET_SERVING,
            user=user,
            user_name=user.get_full_name(),
            metadata={'ticket_number': self.ticket_number},
        )

    def complete(self, user: User | None = None) -> None:
        """Mark the ticket as completed."""
        if self.status != self.TicketStatus.SERVING:
            return
        self.status = self.TicketStatus.COMPLETED
        self.completed_at = timezone.now()
        if user:
            self.served_by = user
        self.save(update_fields=['status', 'completed_at', 'served_by'])
        # update statistics and log event
        self.queue.update_statistics()
        self.queue.save(update_fields=['completed'])
        QueueEvent.objects.create(
            queue=self.queue,
            ticket=self,
            event_type=QueueEvent.QueueEventType.TICKET_COMPLETED,
            user=user,
            user_name=user.get_full_name() if user else '',
            metadata={'ticket_number': self.ticket_number},
        )

    def cancel(self, user: User | None = None, reason: str | None = None) -> None:
        """Cancel the ticket."""
        if self.status in (self.TicketStatus.CANCELLED, self.TicketStatus.COMPLETED):
            return
        self.status = self.TicketStatus.CANCELLED
        self.cancelled_at = timezone.now()
        self.notes = reason or self.notes
        self.save(update_fields=['status', 'cancelled_at', 'notes'])
        self.queue.update_statistics()
        self.queue.save(update_fields=['cancelled'])
        QueueEvent.objects.create(
            queue=self.queue,
            ticket=self,
            event_type=QueueEvent.QueueEventType.TICKET_CANCELLED,
            user=user,
            user_name=user.get_full_name() if user else '',
            metadata={'ticket_number': self.ticket_number, 'reason': reason},
        )

    def mark_no_show(self, user: User | None = None) -> None:
        """Mark the ticket as a no‑show."""
        if self.status != self.TicketStatus.CALLED:
            return
        self.status = self.TicketStatus.NO_SHOW
        self.save(update_fields=['status'])
        self.queue.update_statistics()
        self.queue.save(update_fields=['no_show'])
        QueueEvent.objects.create(
            queue=self.queue,
            ticket=self,
            event_type=QueueEvent.QueueEventType.TICKET_NO_SHOW,
            user=user,
            user_name=user.get_full_name() if user else '',
            metadata={'ticket_number': self.ticket_number},
        )


class QueueEvent(models.Model):
    """Audit log of queue and ticket events.

    Events capture meaningful changes to queues and tickets such as
    opening/closing a queue or changing a ticket's state. Each event
    carries an optional metadata payload to enrich context.
    """

    class QueueEventType(models.TextChoices):
        QUEUE_OPENED = 'QUEUE_OPENED', 'Queue opened'
        QUEUE_CLOSED = 'QUEUE_CLOSED', 'Queue closed'
        TICKET_CREATED = 'TICKET_CREATED', 'Ticket created'
        TICKET_CALLED = 'TICKET_CALLED', 'Ticket called'
        TICKET_SERVING = 'TICKET_SERVING', 'Ticket serving'
        TICKET_COMPLETED = 'TICKET_COMPLETED', 'Ticket completed'
        TICKET_CANCELLED = 'TICKET_CANCELLED', 'Ticket cancelled'
        TICKET_NO_SHOW = 'TICKET_NO_SHOW', 'Ticket no show'
        TICKET_UPDATED = 'TICKET_UPDATED', 'Ticket updated'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name='events')
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    event_type = models.CharField(max_length=30, choices=QueueEventType.choices)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'queue_events'
        indexes = [
            models.Index(fields=['queue'], name='idx_queue_events_queue_id'),
            models.Index(fields=['ticket'], name='idx_queue_events_ticket_id'),
            models.Index(fields=['timestamp'], name='idx_queue_events_timestamp'),
            models.Index(fields=['event_type'], name='idx_queue_events_event_type'),
        ]
        ordering = ['-timestamp']
        verbose_name = 'Queue Event'
        verbose_name_plural = 'Queue Events'

    def __str__(self) -> str:
        return f"{self.event_type} on {self.timestamp.isoformat()}"


class Notification(models.Model):
    """Notification sent to a patient.

    Notifications represent SMS, email or push messages triggered by
    queue events. In a production system these would interface with
    external messaging services. For the purposes of this backend
    notifications are logged but not delivered.
    """

    class NotificationType(models.TextChoices):
        SMS = 'SMS', 'SMS'
        EMAIL = 'EMAIL', 'Email'
        PUSH = 'PUSH', 'Push'

    class NotificationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SENT = 'SENT', 'Sent'
        DELIVERED = 'DELIVERED', 'Delivered'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=10, choices=NotificationType.choices)
    recipient = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.PENDING)
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['ticket'], name='idx_notifications_ticket_id'),
            models.Index(fields=['status'], name='idx_notifications_status'),
            models.Index(fields=['type'], name='idx_notifications_type'),
            models.Index(fields=['sent_at'], name='idx_notifications_sent_at'),
        ]
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self) -> str:
        return f"{self.type} to {self.recipient} ({self.status})"


class AdminAuditLog(models.Model):
    """Audit log for sensitive administrative actions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='admin_audit_actions',
        null=True,
        blank=True,
    )
    actor_email = models.EmailField(blank=True, null=True)
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
        null=True,
        blank=True,
    )
    action_type = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=64, blank=True, null=True)
    before_data = models.JSONField(blank=True, null=True)
    after_data = models.JSONField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_audit_logs'
        indexes = [
            models.Index(fields=['created_at'], name='idx_admin_audit_created_at'),
            models.Index(fields=['action_type'], name='idx_admin_audit_action_type'),
        ]
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.action_type} ({self.entity_type}) @ {self.created_at.isoformat()}"


class SystemSettings(models.Model):
    """Singleton-like table storing global admin-managed settings."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    twilio_config = models.JSONField(default=dict, blank=True)
    smtp_config = models.JSONField(default=dict, blank=True)
    sms_template = models.TextField(default='Your ticket {ticket_number} has been updated.')
    email_template = models.TextField(default='Hello {patient_name}, your queue update is ready.')
    default_queue_rules = models.JSONField(default=dict, blank=True)
    maintenance_mode = models.BooleanField(default=False)
    maintenance_banner = models.CharField(max_length=255, blank=True, default='')
    data_retention_days = models.IntegerField(default=90)
    allowed_countries = models.JSONField(default=list, blank=True)
    allowed_phone_formats = models.JSONField(default=list, blank=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='updated_system_settings',
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'system_settings'

    def __str__(self) -> str:
        return 'System Settings'