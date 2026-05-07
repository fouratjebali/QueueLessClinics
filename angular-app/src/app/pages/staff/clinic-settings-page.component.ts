import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { AuthSessionService } from '../../services/auth-session.service';
import { Clinic } from '../../models';

type DayKey = 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday';

@Component({
  selector: 'app-clinic-settings-page',
  templateUrl: './clinic-settings-page.component.html',
  styleUrls: ['./clinic-settings-page.component.scss']
})
export class ClinicSettingsPageComponent implements OnInit {
  clinic?: Clinic;
  settings: any = {};
  loading = true;
  errorMessage = '';
  infoMessage = '';
  canEdit = false;

  readonly dayOrder: DayKey[] = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

  constructor(private api: ApiService, private authSession: AuthSessionService) {}

  ngOnInit(): void {
    this.loadContext();
  }

  loadContext(): void {
    this.loading = true;
    this.errorMessage = '';
    this.infoMessage = '';

    this.api.staffGetClinicContext().subscribe({
      next: context => {
        this.clinic = context.clinic;
        this.settings = { ...context.settings };
        this.canEdit = !!context.permissions?.can_edit_settings;
        this.loading = false;
      },
      error: err => {
        this.loading = false;
        this.errorMessage = err?.error?.detail || 'Unable to load clinic settings context.';
      }
    });
  }

  saveGeneral(): void {
    if (!this.clinic || !this.canEdit) return;
    const payload = {
      name: this.clinic.name,
      street: this.clinic.street,
      city: this.clinic.city,
      state: this.clinic.state,
      zip_code: this.clinic.zip_code,
      country: this.clinic.country,
      phone: this.clinic.phone,
      email: this.clinic.email,
      logo: this.clinic.logo,
      primary_color: this.clinic.primary_color,
      secondary_color: this.clinic.secondary_color
    };
    this.api.staffUpdateClinic(payload).subscribe({
      next: updated => {
        this.clinic = updated;
        this.infoMessage = 'General clinic settings saved.';
      },
      error: err => {
        this.errorMessage = err?.error?.detail || 'Unable to save general settings.';
      }
    });
  }

  saveHours(): void {
    this.patchSettings({ operating_hours: this.settings.operating_hours }, 'Operating hours saved.');
  }

  saveQueueRules(): void {
    this.patchSettings({
      max_capacity: this.settings.max_capacity,
      estimated_service_time: this.settings.estimated_service_time,
      allow_walkins: this.settings.allow_walkins,
      allow_online_joining: this.settings.allow_online_joining,
      auto_call_next: this.settings.auto_call_next,
      warning_threshold: this.settings.warning_threshold,
      closed_message: this.settings.closed_message
    }, 'Queue rules saved.');
  }

  saveNotifications(): void {
    this.patchSettings({
      enable_sms: this.settings.enable_sms,
      enable_email: this.settings.enable_email,
      reminder_before_minutes: this.settings.reminder_before_minutes,
      ready_notification: this.settings.ready_notification,
      missed_turn_notification: this.settings.missed_turn_notification
    }, 'Notification preferences saved.');
  }

  saveDisplay(): void {
    this.patchSettings({
      show_estimated_wait_time: this.settings.show_estimated_wait_time,
      show_queue_position: this.settings.show_queue_position,
      show_people_ahead: this.settings.show_people_ahead,
      custom_welcome_message: this.settings.custom_welcome_message,
      display_languages: this.settings.display_languages || []
    }, 'Display settings saved.');
  }

  private patchSettings(payload: any, successMessage: string): void {
    if (!this.canEdit) return;
    this.api.staffUpdateClinicSettings(payload).subscribe({
      next: updated => {
        this.settings = { ...this.settings, ...updated };
        this.infoMessage = successMessage;
      },
      error: err => {
        this.errorMessage = err?.error?.detail || 'Unable to save settings.';
      }
    });
  }
}
