import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../../../app/services/api.service';
import { Ticket } from '../../../app/models';
import { Subscription, interval } from 'rxjs';
import { LocalTicketStoreService } from '../../../app/services/local-ticket-store.service';

@Component({
  selector: 'app-ticket-status-page',
  templateUrl: './ticket-status-page.component.html',
  styleUrls: ['./ticket-status-page.component.scss']
})
export class TicketStatusPageComponent implements OnInit, OnDestroy {
  ticket?: Ticket;
  position = 0;
  servedCount = 0;
  totalCount = 0;
  estimatedWait = 0;
  refreshSub?: Subscription;
  loading = true;

  constructor(
    private route: ActivatedRoute,
    private api: ApiService,
    private ticketStore: LocalTicketStoreService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadStatus(id);
      // auto refresh every 30s
      this.refreshSub = interval(30000).subscribe(() => this.loadStatus(id));
    }
  }

  loadStatus(id: string): void {
    this.loading = true;
    this.api.getTickets({ id }).subscribe(tickets => {
      const ticket = tickets[0];
      this.ticket = ticket;
      if (ticket) {
        this.ticketStore.addTicket({
          id: ticket.id,
          ticketNumber: ticket.ticket_number,
          clinicName: ticket.clinic_name,
          patientName: ticket.patient_name,
          status: ticket.status
        });
        // fetch all tickets in same queue
        this.api.getTickets({ queue: ticket.queue }).subscribe(all => {
          // waiting tickets in queue by order
          const waiting = all.filter(t => t.status === 'WAITING');
          this.totalCount = waiting.length;
          this.position = waiting.findIndex(t => t.id === ticket.id) + 1;
          this.estimatedWait = (this.position - 1) * 15;
          this.servedCount = all.filter(t => t.status === 'COMPLETED').length;
          this.loading = false;
        });
      } else {
        this.loading = false;
      }
    });
  }

  cancelTicket(): void {
    if (!this.ticket) return;
    if (!confirm('Êtes‑vous sûr de vouloir annuler ce ticket ?')) return;
    this.api.cancelTicket(this.ticket.id, 'Cancelled by patient').subscribe(() => {
      this.ticket!.status = 'CANCELLED';
    });
  }

  ngOnDestroy(): void {
    this.refreshSub?.unsubscribe();
  }
}
