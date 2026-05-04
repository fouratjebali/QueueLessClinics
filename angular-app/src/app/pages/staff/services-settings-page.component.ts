import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { ApiService } from '../../services/api.service';
import { Service } from '../../models';

@Component({
  selector: 'app-services-settings-page',
  templateUrl: './services-settings-page.component.html',
  styleUrls: ['./services-settings-page.component.scss']
})
export class ServicesSettingsPageComponent implements OnInit {
  services: Service[] = [];
  displayedColumns: string[] = ['name', 'duration', 'code', 'active', 'order', 'actions'];
  loading = false;
  errorMessage = '';

  constructor(private api: ApiService, private dialog: MatDialog) {}

  ngOnInit(): void {
    this.loadServices();
  }

  loadServices(): void {
    this.loading = true;
    this.errorMessage = '';
    this.api.staffGetServices().subscribe({
      next: services => {
        this.services = services.sort((a, b) => a.display_order - b.display_order);
        this.loading = false;
      },
      error: err => {
        this.loading = false;
        this.errorMessage = err?.error?.detail || 'Unable to load services.';
      }
    });
  }

  openAddService(): void {
    const dialogRef = this.dialog.open(AddEditServiceDialogComponent, {
      width: '440px',
      data: {}
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadServices();
      }
    });
  }

  openEditService(service: Service): void {
    const dialogRef = this.dialog.open(AddEditServiceDialogComponent, {
      width: '440px',
      data: { service: { ...service } }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadServices();
      }
    });
  }

  toggleActive(service: Service): void {
    this.api.staffUpdateService(service.id, { is_active: !service.is_active }).subscribe({
      next: () => {
        service.is_active = !service.is_active;
      },
      error: err => {
        this.errorMessage = err?.error?.detail || 'Unable to update service state.';
      }
    });
  }

  deleteService(service: Service): void {
    this.api.staffDeleteService(service.id).subscribe({
      next: () => {
        this.loadServices();
      },
      error: err => {
        this.errorMessage = err?.error?.detail || 'Unable to delete service.';
      }
    });
  }

  moveUp(service: Service): void {
    const index = this.services.findIndex(s => s.id === service.id);
    if (index <= 0) return;
    this.swapDisplayOrder(index, index - 1);
  }

  moveDown(service: Service): void {
    const index = this.services.findIndex(s => s.id === service.id);
    if (index < 0 || index >= this.services.length - 1) return;
    this.swapDisplayOrder(index, index + 1);
  }

  private swapDisplayOrder(firstIndex: number, secondIndex: number): void {
    const first = this.services[firstIndex];
    const second = this.services[secondIndex];
    if (!first || !second) return;

    const firstOrder = first.display_order;
    const secondOrder = second.display_order;

    this.api.staffUpdateService(first.id, { display_order: secondOrder }).subscribe({
      next: () => {
        this.api.staffUpdateService(second.id, { display_order: firstOrder }).subscribe({
          next: () => this.loadServices(),
          error: err => {
            this.errorMessage = err?.error?.detail || 'Unable to reorder services.';
          }
        });
      },
      error: err => {
        this.errorMessage = err?.error?.detail || 'Unable to reorder services.';
      }
    });
  }
}

@Component({
  selector: 'app-add-edit-service-dialog',
  templateUrl: './add-edit-service-dialog.component.html',
  styleUrls: ['./add-edit-service-dialog.component.scss']
})
export class AddEditServiceDialogComponent {
  form: FormGroup;
  isEdit = false;

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    private dialogRef: MatDialogRef<AddEditServiceDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { service?: Service }
  ) {
    this.isEdit = !!data.service;
    this.form = this.fb.group({
      name: [data.service?.name || '', Validators.required],
      description: [data.service?.description || ''],
      estimated_duration: [data.service?.estimated_duration || 15, Validators.required],
      code: [data.service?.code || ''],
      is_active: [data.service?.is_active ?? true]
    });
  }

  save(): void {
    if (this.form.invalid) return;
    const payload = this.form.value;
    if (this.isEdit && this.data.service) {
      this.api.staffUpdateService(this.data.service.id, payload).subscribe(service => {
        this.dialogRef.close(service);
      });
    } else {
      this.api.staffCreateService(payload).subscribe(service => {
        this.dialogRef.close(service);
      });
    }
  }

  close(): void {
    this.dialogRef.close();
  }
}