import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { forkJoin } from 'rxjs';
import { ApiService } from '../../services/api.service';
import { Clinic, Queue, Service, Ticket } from '../../models';
import { AddWalkinModalComponent } from './add-walkin-modal.component';

@Component({
  selector: 'app-dashboard-page',
  templateUrl: './dashboard-page.component.html',
  styleUrls: ['./dashboard-page.component.scss']
})
export class DashboardPageComponent implements OnInit {
  clinic?: Clinic;
  currentQueue?: Queue;
  services: Service[] = [];
  tickets: Ticket[] = [];
  filteredTickets: Ticket[] = [];
  waitingTickets: Ticket[] = [];
  servingTicket?: Ticket;
  metrics = {
    waiting: 0,
    avgWait: 0,
    done: 0,
    noShow: 0
  };
  filterStatus = '';
  filterService = '';
  search = '';
  displayedColumns: string[] = ['ticket', 'patient', 'service', 'wait', 'status', 'priority', 'actions'];
  loading = true;
  actionBusyId = '';
  actionError = '';
  infoMessage = '';
  selectedDate = this.isoDate(new Date());

  constructor(private api: ApiService, private dialog: MatDialog) {}

  ngOnInit(): void {
    this.loadContext();
  }

  get nextTicket(): Ticket | undefined {
    const priorityRank: Record<string, number> = { URGENT: 0, HIGH: 1, NORMAL: 2 };
    return [...this.waitingTickets].sort((a, b) => {
      const pa = priorityRank[a.priority] ?? 99;
      const pb = priorityRank[b.priority] ?? 99;
      if (pa !== pb) {
        return pa - pb;
      }
      return a.position - b.position;
    })[0];
  }

  loadContext(): void {
    this.loading = true;
    this.api.staffGetClinicContext().subscribe({
      next: context => {
        this.clinic = context.clinic;
        this.loadServices();
        this.loadData();
      },
      error: err => {
        this.loading = false;
        this.actionError = err?.error?.detail || 'Unable to load staff clinic context.';
      }
    });
  }

  loadServices(): void {
    this.api.staffGetServices().subscribe({
      next: data => {
        this.services = data;
      },
      error: () => {
        this.services = [];
      }
    });
  }

  loadData(): void {
    this.loading = true;
    this.actionError = '';
    this.infoMessage = '';

    forkJoin({
      kpis: this.api.staffGetClinicKpis(this.selectedDate),
      queues: this.api.staffGetQueues({ date: this.selectedDate }),
      tickets: this.api.staffGetTickets({ date: this.selectedDate })
    }).subscribe({
      next: ({ kpis, queues, tickets }) => {
        this.metrics.waiting = kpis.waiting;
        this.metrics.avgWait = Math.round(kpis.avg_wait || 0);
        this.metrics.done = kpis.completed;
        this.metrics.noShow = kpis.no_show;

        this.currentQueue = queues.find(q => q.is_active) || queues[0];
        this.tickets = [...tickets].sort((a, b) => a.position - b.position);
        this.waitingTickets = this.tickets.filter(t => t.status === 'WAITING');
        this.servingTicket = this.tickets.find(t => t.status === 'SERVING');
        this.applyFilters();
        this.loading = false;
      },
      error: err => {
        this.loading = false;
        this.actionError = err?.error?.detail || 'Unable to load dashboard data.';
      }
    });
  }

  applyFilters(): void {
    this.filteredTickets = this.tickets.filter(t => {
      if (this.filterStatus && t.status !== this.filterStatus) {
        return false;
      }
      if (this.filterService && t.service !== this.filterService) {
        return false;
      }
      if (this.search) {
        const needle = this.search.toLowerCase();
        const haystack = `${t.ticket_number} ${t.patient_name} ${t.patient_phone}`.toLowerCase();
        if (!haystack.includes(needle)) {
          return false;
        }
      }
      return true;
    });
  }

  onDateChange(): void {
    this.loadData();
  }

  isSelectedDateToday(): boolean {
    return this.selectedDate === this.isoDate(new Date());
  }

  openQueue(): void {
    this.api.staffOpenQueue({ date: this.selectedDate }).subscribe({
      next: () => {
        this.infoMessage = `Queue opened for ${this.selectedDate}.`;
        this.loadData();
      },
      error: err => {
        this.actionError = err?.error?.detail || 'Unable to open queue.';
      }
    });
  }

  closeQueue(): void {
    if (!this.currentQueue) return;
    this.api.staffCloseQueue(this.currentQueue.id).subscribe({
      next: () => {
        this.infoMessage = 'Queue closed.';
        this.loadData();
      },
      error: err => {
        this.actionError = err?.error?.detail || 'Unable to close queue.';
      }
    });
  }

  callNext(): void {
    if (!this.isSelectedDateToday()) {
      this.actionError = 'Ticket actions are available only for today.';
      return;
    }
    if (!this.nextTicket) {
      return;
    }
    this.performAction(this.nextTicket.id, this.api.staffCallTicket(this.nextTicket.id));
  }

  openWalkinModal(): void {
    if (!this.isSelectedDateToday()) {
      this.actionError = 'Walk-ins can be added only for today.';
      return;
    }
    if (!this.clinic) return;
    const dialogRef = this.dialog.open(AddWalkinModalComponent, {
      width: '560px',
      data: { clinic: this.clinic }
    });
    dialogRef.afterClosed().subscribe(payload => {
      if (!payload) return;
      this.api.staffCreateWalkin(payload).subscribe({
        next: () => {
          this.infoMessage = 'Walk-in ticket added.';
          this.loadData();
        },
        error: err => {
          this.actionError = err?.error?.detail || 'Unable to add walk-in ticket.';
        }
      });
    });
  }

  callTicket(ticket: Ticket): void {
    if (!this.isSelectedDateToday()) return;
    this.performAction(ticket.id, this.api.staffCallTicket(ticket.id));
  }

  markServing(ticket: Ticket): void {
    if (!this.isSelectedDateToday()) return;
    this.performAction(ticket.id, this.api.staffStartTicket(ticket.id));
  }

  completeTicket(ticket: Ticket): void {
    if (!this.isSelectedDateToday()) return;
    this.performAction(ticket.id, this.api.staffCompleteTicket(ticket.id));
  }

  cancelTicket(ticket: Ticket): void {
    if (!this.isSelectedDateToday()) return;
    this.performAction(ticket.id, this.api.staffCancelTicket(ticket.id));
  }

  markNoShow(ticket: Ticket): void {
    if (!this.isSelectedDateToday()) return;
    this.performAction(ticket.id, this.api.staffNoShowTicket(ticket.id));
  }

  moveUp(ticket: Ticket): void {
    if (!this.isSelectedDateToday()) return;
    this.performAction(ticket.id, this.api.staffReorderTicket(ticket.id, { direction: 'up' }));
  }

  moveDown(ticket: Ticket): void {
    if (!this.isSelectedDateToday()) return;
    this.performAction(ticket.id, this.api.staffReorderTicket(ticket.id, { direction: 'down' }));
  }

  canMoveUp(ticket: Ticket): boolean {
    if (ticket.status !== 'WAITING') return false;
    const list = this.waitingTickets;
    return list.findIndex(t => t.id === ticket.id) > 0;
  }

  canMoveDown(ticket: Ticket): boolean {
    if (ticket.status !== 'WAITING') return false;
    const list = this.waitingTickets;
    const index = list.findIndex(t => t.id === ticket.id);
    return index >= 0 && index < list.length - 1;
  }

  isBusy(ticketId: string): boolean {
    return this.actionBusyId === ticketId;
  }

  private performAction(ticketId: string, request$: any): void {
    this.actionBusyId = ticketId;
    this.actionError = '';
    request$.subscribe({
      next: () => {
        this.actionBusyId = '';
        this.loadData();
      },
      error: (err: any) => {
        this.actionBusyId = '';
        this.actionError = err?.error?.detail || 'Ticket action failed.';
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