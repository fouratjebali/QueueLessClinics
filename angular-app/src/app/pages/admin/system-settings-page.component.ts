import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-system-settings-page',
  templateUrl: './system-settings-page.component.html',
  styleUrls: ['./system-settings-page.component.scss']
})
export class SystemSettingsPageComponent implements OnInit {
  settingsForm: FormGroup;

  constructor(private fb: FormBuilder, private api: ApiService) {
    this.settingsForm = this.fb.group({
      maintenance_mode: [false],
      maintenance_banner: [''],
      data_retention_days: [90, [Validators.required, Validators.min(1)]],
      sms_template: ['', Validators.required],
      email_template: ['', Validators.required],
      allowed_countries: ['Tunisia'],
      allowed_phone_formats: ['+216########'],
      twilio_config: ['{}'],
      smtp_config: ['{}'],
      default_queue_rules: ['{}']
    });
  }

  ngOnInit(): void {
    this.api.adminGetSystemSettings().subscribe(data => {
      this.settingsForm.patchValue({
        ...data,
        allowed_countries: (data.allowed_countries || []).join(','),
        allowed_phone_formats: (data.allowed_phone_formats || []).join(','),
        twilio_config: JSON.stringify(data.twilio_config || {}, null, 2),
        smtp_config: JSON.stringify(data.smtp_config || {}, null, 2),
        default_queue_rules: JSON.stringify(data.default_queue_rules || {}, null, 2)
      });
    });
  }

  save(): void {
    if (this.settingsForm.invalid) return;
    const raw = this.settingsForm.value;
    try {
      this.api.adminPatchSystemSettings({
        maintenance_mode: raw.maintenance_mode,
        maintenance_banner: raw.maintenance_banner,
        data_retention_days: Number(raw.data_retention_days),
        sms_template: raw.sms_template,
        email_template: raw.email_template,
        allowed_countries: String(raw.allowed_countries).split(',').map((s: string) => s.trim()).filter(Boolean),
        allowed_phone_formats: String(raw.allowed_phone_formats).split(',').map((s: string) => s.trim()).filter(Boolean),
        twilio_config: JSON.parse(raw.twilio_config || '{}'),
        smtp_config: JSON.parse(raw.smtp_config || '{}'),
        default_queue_rules: JSON.parse(raw.default_queue_rules || '{}')
      }).subscribe(() => alert('System settings saved'));
    } catch {
      alert('Invalid JSON in provider/default rules fields');
    }
  }

  sendTest(channel: 'EMAIL' | 'SMS'): void {
    const target = prompt(`Target ${channel.toLowerCase()} address/number`);
    if (!target) return;
    this.api.adminTestNotification({ target, channel }).subscribe(res => alert(res.detail));
  }
}