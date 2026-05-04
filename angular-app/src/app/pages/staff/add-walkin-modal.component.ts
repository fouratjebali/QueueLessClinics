import { Component, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ApiService } from '../../services/api.service';
import { Clinic, Service } from '../../models';

@Component({
  selector: 'app-add-walkin-modal',
  templateUrl: './add-walkin-modal.component.html',
  styleUrls: ['./add-walkin-modal.component.scss']
})
export class AddWalkinModalComponent {
  form: FormGroup;
  services: Service[] = [];

  priorities = [
    { label: 'Normale', value: 'NORMAL' },
    { label: 'Haute', value: 'HIGH' },
    { label: 'Urgente', value: 'URGENT' }
  ];

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    private dialogRef: MatDialogRef<AddWalkinModalComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { clinic: Clinic }
  ) {
    this.form = this.fb.group({
      patient_name: ['', Validators.required],
      patient_phone: ['', Validators.required],
      service: ['', Validators.required],
      priority: ['NORMAL', Validators.required],
      notes: ['']
    });
    if (data.clinic) {
      this.api.staffGetServices().subscribe(services => (this.services = services));
    }
  }

  save(): void {
    if (this.form.invalid || !this.data.clinic) return;
    const payload = {
      clinic: this.data.clinic.id,
      ...this.form.value,
      is_walkin: true
    };
    // For now we simply return the form data; actual ticket creation should be handled by caller
    this.dialogRef.close(payload);
  }

  close(): void {
    this.dialogRef.close();
  }
}