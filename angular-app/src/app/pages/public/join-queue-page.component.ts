import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ApiService } from '../../../app/services/api.service';
import { Clinic, Service, Ticket, Queue } from '../../../app/models';
import { LocalTicketStoreService } from '../../../app/services/local-ticket-store.service';

@Component({
  selector: 'app-join-queue-page',
  templateUrl: './join-queue-page.component.html',
  styleUrls: ['./join-queue-page.component.scss']
})
export class JoinQueuePageComponent implements OnInit {
  clinic?: Clinic;
  services: Service[] = [];
  joinForm: FormGroup;
  queueLength = 0;
  estimatedWait = 0;
  activeQueue?: Queue;
  loading = false;
  message?: string;

  constructor(private api: ApiService, private route: ActivatedRoute, private fb: FormBuilder, private router: Router, private ticketStore: LocalTicketStoreService) {
    this.joinForm = this.fb.group({
      fullName: ['', Validators.required],
      phone: ['', [Validators.required]],
      email: [''],
      service: ['', Validators.required],
      notes: [''],
      accept: [false, Validators.requiredTrue]
    });
  }

  ngOnInit(): void {
    const slug = this.route.snapshot.paramMap.get('slug');
    this.api.getClinics().subscribe(clinics => {
      if (slug) {
        this.clinic = clinics.find(c => (c as any).slug === slug || c.id === slug);
      }
      if (!this.clinic && clinics.length) {
        this.clinic = clinics[0];
      }
      if (this.clinic) {
        this.api.getServices(this.clinic.id).subscribe(services => (this.services = services));
        this.api.getQueues(this.clinic.id).subscribe(queues => {
          this.activeQueue = queues.find(q => q.is_active) || queues[0];
          this.loadQueueStats();
        });
      }
    });
  }

  loadQueueStats(): void {
    if (!this.activeQueue) return;
    this.queueLength = this.activeQueue.waiting || 0;
    this.estimatedWait = Math.max(
      0,
      Math.round(Number(this.activeQueue.current_wait_time ?? this.activeQueue.avg_wait_time ?? 0))
    );
  }

  joinQueue(): void {
    if (this.joinForm.invalid || !this.clinic) {
      return;
    }
    const data: any = {
      clinic: this.clinic.id,
      queue: this.activeQueue?.id,
      service: this.joinForm.value.service,
      patient_name: this.joinForm.value.fullName,
      patient_phone: this.joinForm.value.phone,
      patient_email: this.joinForm.value.email || undefined,
      notes: this.joinForm.value.notes,
      is_walkin: true
    };
    this.loading = true;
    this.api.createTicket(data).subscribe({
      next: (ticket: Ticket) => {
        this.loading = false;
        this.message = 'Votre ticket a Ã©tÃ© crÃ©Ã©.';
        this.ticketStore.addTicket({
          id: ticket.id,
          ticketNumber: ticket.ticket_number,
          clinicName: ticket.clinic_name || this.clinic?.name,
          patientName: ticket.patient_name,
          status: ticket.status
        });
        this.router.navigate(['/public/ticket', ticket.id]);
      },
      error: () => {
        this.loading = false;
        this.message = 'Erreur lors de la crÃ©ation du ticket';
      }
    });
  }
}