import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { ApiService } from '../../services/api.service';
import { Clinic, Queue } from '../../models';

type ClinicRow = Clinic & {
  is_open_now: boolean;
  total_tickets_today: number;
  waiting_now: number;
  avg_wait_time: number;
};

type NewClinicForm = {
  name: string;
  city: string;
};

type NewStaffUserForm = {
  email: string;
  first_name: string;
  last_name: string;
  clinic: string;
};

type EditClinicForm = {
  name: string;
  city: string;
};

@Component({
  selector: 'app-clinics-page',
  templateUrl: './clinics-page.component.html',
  styleUrls: ['./clinics-page.component.scss']
})
export class ClinicsPageComponent implements OnInit {
  clinics: ClinicRow[] = [];
  displayedColumns: string[] = ['name', 'city', 'open', 'stats', 'active', 'actions'];
  search = '';
  city = '';
  isActive = '';

  showAddClinicForm = false;
  isSubmittingClinic = false;
  addClinicError = '';
  newClinic: NewClinicForm = this.emptyClinicForm();
  showQuickStaffForm = false;
  isSubmittingStaff = false;
  addStaffError = '';
  staffTemporaryPassword = '';
  newStaff: NewStaffUserForm = this.emptyStaffForm();
  showEditClinicForm = false;
  isSubmittingEditClinic = false;
  editClinicError = '';
  editingClinicId = '';
  editClinicForm: EditClinicForm = this.emptyEditClinicForm();

  constructor(private api: ApiService, private router: Router) {}

  ngOnInit(): void {
    this.loadClinics();
  }

  loadClinics(): void {
    forkJoin({
      clinics: this.api.adminGetClinics({
        search: this.search,
        city: this.city,
        is_active: this.isActive
      }),
      queues: this.api.getQueues()
    }).subscribe(({ clinics, queues }) => {
      this.clinics = clinics.map(c => this.buildRow(c, queues));
    });
  }

  private buildRow(clinic: Clinic, queues: Queue[]): ClinicRow {
    const clinicQueues = queues.filter(q => q.clinic === clinic.id);
    const activeQueue = clinicQueues.find(q => q.is_active);
    const todayQueue = clinicQueues
      .slice()
      .sort((a, b) => (a.date < b.date ? 1 : -1))[0];
    return {
      ...clinic,
      is_open_now: !!activeQueue,
      total_tickets_today: todayQueue?.total_tickets || 0,
      waiting_now: activeQueue?.waiting || 0,
      avg_wait_time: Number(activeQueue?.avg_wait_time || todayQueue?.avg_wait_time || 0)
    };
  }

  openAddClinicForm(): void {
    this.showQuickStaffForm = false;
    this.showEditClinicForm = false;
    this.showAddClinicForm = true;
    this.addClinicError = '';
    this.newClinic = this.emptyClinicForm();
  }

  cancelAddClinic(): void {
    this.showAddClinicForm = false;
    this.isSubmittingClinic = false;
    this.addClinicError = '';
    this.newClinic = this.emptyClinicForm();
  }

  submitAddClinic(): void {
    const name = this.newClinic.name.trim();
    const city = this.newClinic.city.trim();

    if (!name || !city || this.isSubmittingClinic) {
      return;
    }

    const slug = name
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-');

    const payload = {
      name,
      slug,
      street: 'Address pending',
      city,
      state: 'N/A',
      zip_code: '0000',
      country: 'Tunisia',
      phone: '+21600000000',
      email: `contact+${slug}@clinic.local`,
      is_active: true
    };

    this.isSubmittingClinic = true;
    this.addClinicError = '';

    this.api.adminCreateClinic(payload).subscribe({
      next: () => {
        this.cancelAddClinic();
        this.loadClinics();
      },
      error: () => {
        this.addClinicError = 'Creation de clinique impossible';
        this.isSubmittingClinic = false;
      }
    });
  }

  openQuickStaffForm(): void {
    this.showAddClinicForm = false;
    this.showEditClinicForm = false;
    this.showQuickStaffForm = true;
    this.isSubmittingStaff = false;
    this.addStaffError = '';
    this.staffTemporaryPassword = '';
    this.newStaff = this.emptyStaffForm();
  }

  cancelQuickStaffForm(): void {
    this.showQuickStaffForm = false;
    this.isSubmittingStaff = false;
    this.addStaffError = '';
    this.newStaff = this.emptyStaffForm();
  }

  submitQuickStaffForm(): void {
    const email = this.newStaff.email.trim();
    const firstName = this.newStaff.first_name.trim();
    const lastName = this.newStaff.last_name.trim();
    const clinicId = this.newStaff.clinic || null;

    if (!email || !firstName || !lastName || this.isSubmittingStaff) {
      return;
    }

    this.isSubmittingStaff = true;
    this.addStaffError = '';
    this.staffTemporaryPassword = '';

    this.api.adminCreateUser({
      email,
      first_name: firstName,
      last_name: lastName,
      role: 'STAFF',
      clinic: clinicId
    }).subscribe({
      next: (res: any) => {
        this.cancelQuickStaffForm();
        if (res?.temp_password) {
          this.staffTemporaryPassword = `Temporary password: ${res.temp_password}`;
        }
        this.loadClinics();
      },
      error: () => {
        this.addStaffError = 'Creation de staff impossible';
        this.isSubmittingStaff = false;
      }
    });
  }

  openEditClinicForm(clinic: Clinic): void {
    this.showAddClinicForm = false;
    this.showQuickStaffForm = false;
    this.showEditClinicForm = true;
    this.isSubmittingEditClinic = false;
    this.editClinicError = '';
    this.editingClinicId = clinic.id;
    this.editClinicForm = {
      name: clinic.name || '',
      city: clinic.city || ''
    };
  }

  cancelEditClinic(): void {
    this.showEditClinicForm = false;
    this.isSubmittingEditClinic = false;
    this.editClinicError = '';
    this.editingClinicId = '';
    this.editClinicForm = this.emptyEditClinicForm();
  }

  submitEditClinic(): void {
    const clinic = this.clinics.find(c => c.id === this.editingClinicId);
    const name = this.editClinicForm.name.trim();
    const city = this.editClinicForm.city.trim();

    if (!clinic || !name || !city || this.isSubmittingEditClinic) {
      return;
    }

    this.isSubmittingEditClinic = true;
    this.editClinicError = '';

    this.api.adminUpdateClinic(clinic.id, { name, city }).subscribe({
      next: updated => {
        clinic.name = updated.name;
        clinic.city = updated.city;
        this.cancelEditClinic();
      },
      error: () => {
        this.editClinicError = 'Modification de clinique impossible';
        this.isSubmittingEditClinic = false;
      }
    });
  }

  toggleActive(clinic: Clinic): void {
    this.api.adminToggleClinic(clinic.id).subscribe({
      next: res => {
        clinic.is_active = res.is_active;
      },
      error: () => alert('Mise a jour statut impossible')
    });
  }

  openDetails(clinic: Clinic): void {
    this.router.navigate(['/admin/clinics', clinic.id]);
  }

  private emptyClinicForm(): NewClinicForm {
    return {
      name: '',
      city: ''
    };
  }

  private emptyStaffForm(): NewStaffUserForm {
    return {
      email: '',
      first_name: '',
      last_name: '',
      clinic: ''
    };
  }

  private emptyEditClinicForm(): EditClinicForm {
    return {
      name: '',
      city: ''
    };
  }
}