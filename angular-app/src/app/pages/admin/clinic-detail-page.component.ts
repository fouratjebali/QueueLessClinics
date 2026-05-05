import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { Clinic, Service, User } from '../../models';

@Component({
  selector: 'app-clinic-detail-page',
  templateUrl: './clinic-detail-page.component.html',
  styleUrls: ['./clinic-detail-page.component.scss']
})
export class ClinicDetailPageComponent implements OnInit {
  clinicId = '';
  clinic?: Clinic;
  services: Service[] = [];
  staff: User[] = [];
  loading = false;

  constructor(private route: ActivatedRoute, private api: ApiService) {}

  ngOnInit(): void {
    this.clinicId = this.route.snapshot.paramMap.get('id') || '';
    if (this.clinicId) {
      this.loadAll();
    }
  }

  loadAll(): void {
    this.loading = true;
    this.api.adminGetClinic(this.clinicId).subscribe({
      next: clinic => {
        this.clinic = clinic;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
    this.api.adminGetClinicServices(this.clinicId).subscribe(services => (this.services = services));
    this.api.adminGetUsers({ clinic: this.clinicId }).subscribe(users => (this.staff = users));
  }

  saveGeneral(): void {
    if (!this.clinic) return;
    this.api.adminUpdateClinic(this.clinic.id, this.clinic).subscribe(updated => (this.clinic = updated));
  }

  saveBranding(): void {
    if (!this.clinic) return;
    this.api.adminUpdateClinicBranding(this.clinic.id, {
      primary_color: this.clinic.primary_color,
      secondary_color: this.clinic.secondary_color,
      logo: this.clinic.logo
    }).subscribe(updated => (this.clinic = updated));
  }

  saveHours(raw: string): void {
    if (!this.clinic) return;
    try {
      const operating_hours = JSON.parse(raw);
      this.api.adminUpdateClinicHours(this.clinic.id, operating_hours).subscribe(() => alert('Hours updated'));
    } catch {
      alert('Invalid JSON for hours');
    }
  }

  saveRules(maxCapacity: string, serviceTime: string, rulesJson: string): void {
    if (!this.clinic) return;
    let emergency_priority_rules = {};
    try {
      emergency_priority_rules = rulesJson ? JSON.parse(rulesJson) : {};
    } catch {
      alert('Invalid JSON for emergency rules');
      return;
    }
    this.api.adminUpdateClinicRules(this.clinic.id, {
      max_capacity: Number(maxCapacity),
      estimated_service_time: Number(serviceTime),
      emergency_priority_rules
    }).subscribe(() => alert('Queue rules updated'));
  }

  addService(): void {
    if (!this.clinic) return;
    const name = prompt('Service name');
    if (!name) return;
    this.api.adminCreateClinicService(this.clinic.id, {
      name,
      estimated_duration: 15,
      display_order: this.services.length + 1,
      is_active: true
    }).subscribe(() => this.api.adminGetClinicServices(this.clinic!.id).subscribe(data => (this.services = data)));
  }

  updateService(service: Service): void {
    const name = prompt('Service name', service.name);
    if (!name) return;
    this.api.adminUpdateService(service.id, { name }).subscribe(updated => {
      const index = this.services.findIndex(s => s.id === service.id);
      if (index >= 0) this.services[index] = updated;
    });
  }

  deleteService(service: Service): void {
    if (!confirm(`Delete service ${service.name}?`)) return;
    this.api.adminDeleteService(service.id).subscribe(() => {
      this.services = this.services.filter(s => s.id !== service.id);
    });
  }
}