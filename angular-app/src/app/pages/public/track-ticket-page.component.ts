import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../../app/services/api.service';
import { LocalTicketStoreService } from '../../../app/services/local-ticket-store.service';

@Component({
  selector: 'app-track-ticket-page',
  templateUrl: './track-ticket-page.component.html',
  styleUrls: ['./track-ticket-page.component.scss']
})
export class TrackTicketPageComponent {
  trackForm: FormGroup;
  error?: string;

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    private router: Router,
    private ticketStore: LocalTicketStoreService
  ) {
    this.trackForm = this.fb.group({
      ticketNumber: ['', Validators.required],
      phone: ['', Validators.required]
    });
  }

  track(): void {
    this.error = undefined;
    if (this.trackForm.invalid) return;
    const { ticketNumber, phone } = this.trackForm.value;
    this.api.getTickets({ ticket_number: ticketNumber, patient_phone: phone }).subscribe({
      next: tickets => {
        if (tickets.length) {
          this.ticketStore.addTicket({
            id: tickets[0].id,
            ticketNumber: tickets[0].ticket_number,
            clinicName: tickets[0].clinic_name,
            patientName: tickets[0].patient_name,
            status: tickets[0].status
          });
          this.router.navigate(['/public/ticket', tickets[0].id]);
        } else {
          this.error = 'Ticket non trouvé';
        }
      },
      error: () => {
        this.error = 'Erreur lors de la recherche';
      }
    });
  }
}
