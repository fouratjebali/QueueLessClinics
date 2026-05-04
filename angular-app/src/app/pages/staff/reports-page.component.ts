import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { Ticket } from '../../models';

interface HourlyData {
  hour: string;
  count: number;
}

interface StatusDist {
  status: string;
  count: number;
  color: string;
}

interface WaitTrendPoint {
  day: string;
  avg: number;
}

@Component({
  selector: 'app-reports-page',
  templateUrl: './reports-page.component.html',
  styleUrls: ['./reports-page.component.scss']
})
export class ReportsPageComponent implements OnInit {
  fromDate = '';
  toDate = '';

  totalPatients = 0;
  avgWait = 0;
  avgService = 0;
  noShowRate = 0;

  hourlyData: HourlyData[] = [];
  statusDist: StatusDist[] = [];
  waitTrend: WaitTrendPoint[] = [];

  loading = false;
  errorMessage = '';

  private readonly statusColors: Record<string, string> = {
    WAITING: '#4f46e5',
    CALLED: '#0284c7',
    SERVING: '#0d9488',
    COMPLETED: '#16a34a',
    CANCELLED: '#dc2626',
    NO_SHOW: '#f59e0b'
  };

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    const today = new Date();
    const weekAgo = new Date();
    weekAgo.setDate(today.getDate() - 7);
    this.fromDate = this.isoDate(weekAgo);
    this.toDate = this.isoDate(today);
    this.loadReport();
  }

  loadReport(): void {
    this.loading = true;
    this.errorMessage = '';

    this.api.staffGetTickets({ from: this.fromDate, to: this.toDate }).subscribe({
      next: tickets => {
        this.computeKpis(tickets);
        this.computeHourly(tickets);
        this.computeStatusDistribution(tickets);
        this.computeWaitTrend(tickets);
        this.loading = false;
      },
      error: err => {
        this.loading = false;
        this.errorMessage = err?.error?.detail || 'Unable to load reports.';
      }
    });
  }

  exportCsv(): void {
    const header = ['date', 'ticket_number', 'patient_name', 'status', 'priority', 'estimated_wait_time'];
    const rows: string[] = [header.join(',')];

    this.api.staffGetTickets({ from: this.fromDate, to: this.toDate }).subscribe(tickets => {
      tickets.forEach(t => {
        rows.push([
          this.toLocalDate(t.joined_at),
          this.escapeCsv(t.ticket_number),
          this.escapeCsv(t.patient_name),
          t.status,
          t.priority,
          `${t.estimated_wait_time}`
        ].join(','));
      });

      const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `staff-report-${this.fromDate}-to-${this.toDate}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  exportPdfSummary(): void {
    const lines = [
      `Staff Report`,
      `Range: ${this.fromDate} to ${this.toDate}`,
      `Total patients: ${this.totalPatients}`,
      `Avg wait: ${this.avgWait} min`,
      `Avg service: ${this.avgService} min`,
      `No-show rate: ${this.noShowRate}%`
    ];
    const popup = window.open('', '_blank', 'width=800,height=600');
    if (!popup) {
      return;
    }
    popup.document.write(`<pre>${lines.join('\n')}</pre>`);
    popup.document.close();
    popup.focus();
    popup.print();
  }

  private computeKpis(tickets: Ticket[]): void {
    this.totalPatients = tickets.length;
    const completed = tickets.filter(t => t.status === 'COMPLETED');
    const noShow = tickets.filter(t => t.status === 'NO_SHOW');

    const waitSamples = completed.map(t => this.effectiveWait(t));
    const serviceSamples = completed.map(t => this.effectiveServiceTime(t));

    this.avgWait = waitSamples.length ? Math.round(waitSamples.reduce((sum, v) => sum + v, 0) / waitSamples.length) : 0;
    this.avgService = serviceSamples.length ? Math.round(serviceSamples.reduce((sum, v) => sum + v, 0) / serviceSamples.length) : 0;
    this.noShowRate = this.totalPatients ? Math.round((noShow.length / this.totalPatients) * 100) : 0;
  }

  private computeHourly(tickets: Ticket[]): void {
    const buckets: Record<string, number> = {};
    for (let i = 0; i < 24; i++) {
      buckets[`${i}:00`] = 0;
    }
    tickets.forEach(t => {
      const hour = new Date(t.joined_at).getHours();
      const key = `${hour}:00`;
      buckets[key] = (buckets[key] || 0) + 1;
    });
    this.hourlyData = Object.keys(buckets)
      .map(hour => ({ hour, count: buckets[hour] }))
      .filter(d => d.count > 0);
  }

  private computeStatusDistribution(tickets: Ticket[]): void {
    const counts: Record<string, number> = {};
    tickets.forEach(t => {
      counts[t.status] = (counts[t.status] || 0) + 1;
    });
    this.statusDist = Object.entries(counts).map(([status, count]) => ({
      status,
      count,
      color: this.statusColors[status] || '#6b7280'
    }));
  }

  private computeWaitTrend(tickets: Ticket[]): void {
    const grouped: Record<string, number[]> = {};
    tickets.forEach(t => {
      const day = this.toLocalDate(t.joined_at);
      grouped[day] = grouped[day] || [];
      grouped[day].push(this.effectiveWait(t));
    });
    this.waitTrend = Object.entries(grouped)
      .map(([day, values]) => ({
        day,
        avg: values.length ? Math.round(values.reduce((sum, v) => sum + v, 0) / values.length) : 0
      }))
      .sort((a, b) => (a.day > b.day ? 1 : -1));
  }

  private effectiveWait(ticket: Ticket): number {
    if (!ticket.called_at) {
      return ticket.estimated_wait_time || 0;
    }
    const joined = new Date(ticket.joined_at).getTime();
    const called = new Date(ticket.called_at).getTime();
    return Math.max(0, Math.round((called - joined) / 60000));
  }

  private effectiveServiceTime(ticket: Ticket): number {
    if (!ticket.serving_started_at || !ticket.completed_at) {
      return ticket.estimated_wait_time || 0;
    }
    const started = new Date(ticket.serving_started_at).getTime();
    const completed = new Date(ticket.completed_at).getTime();
    return Math.max(0, Math.round((completed - started) / 60000));
  }

  private toLocalDate(value: string): string {
    const d = new Date(value);
    const year = d.getFullYear();
    const month = `${d.getMonth() + 1}`.padStart(2, '0');
    const day = `${d.getDate()}`.padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  private isoDate(value: Date): string {
    const year = value.getFullYear();
    const month = `${value.getMonth() + 1}`.padStart(2, '0');
    const day = `${value.getDate()}`.padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  private escapeCsv(value: string): string {
    const text = `${value || ''}`;
    if (text.includes(',') || text.includes('"') || text.includes('\n')) {
      return `"${text.replace(/"/g, '""')}"`;
    }
    return text;
  }
}