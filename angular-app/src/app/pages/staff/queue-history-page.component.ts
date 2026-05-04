import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { Queue, Ticket } from '../../models';

@Component({
  selector: 'app-queue-history-page',
  templateUrl: './queue-history-page.component.html',
  styleUrls: ['./queue-history-page.component.scss']
})
export class QueueHistoryPageComponent implements OnInit {
  queues: Queue[] = [];
  selectedQueue?: Queue;
  queueTickets: Ticket[] = [];

  displayedColumns: string[] = ['date', 'tickets', 'completed', 'avgWait', 'noShow', 'actions'];
  ticketColumns: string[] = ['ticket', 'patient', 'service', 'status', 'wait'];

  fromDate = '';
  toDate = '';
  loading = false;
  errorMessage = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    const today = new Date();
    const monthAgo = new Date();
    monthAgo.setDate(today.getDate() - 30);
    this.fromDate = this.isoDate(monthAgo);
    this.toDate = this.isoDate(today);
    this.loadQueues();
  }

  loadQueues(): void {
    this.loading = true;
    this.errorMessage = '';
    this.selectedQueue = undefined;
    this.queueTickets = [];

    this.api.staffGetQueues({ from: this.fromDate, to: this.toDate }).subscribe({
      next: queues => {
        const todayIso = this.isoDate(new Date());
        this.queues = queues
          .filter(q => q.date < todayIso || !q.is_active)
          .sort((a, b) => (a.date < b.date ? 1 : -1));
        this.loading = false;
      },
      error: err => {
        this.loading = false;
        this.errorMessage = err?.error?.detail || 'Unable to load queue history.';
      }
    });
  }

  viewQueueDetails(queue: Queue): void {
    this.selectedQueue = queue;
    this.api.staffGetTickets({ queue: queue.id }).subscribe({
      next: tickets => {
        this.queueTickets = tickets.sort((a, b) => a.position - b.position);
      },
      error: err => {
        this.errorMessage = err?.error?.detail || 'Unable to load selected queue details.';
        this.queueTickets = [];
      }
    });
  }

  private isoDate(value: Date): string {
    const year = value.getFullYear();
    const month = `${value.getMonth() + 1}`.padStart(2, '0');
    const day = `${value.getDate()}`.padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
}