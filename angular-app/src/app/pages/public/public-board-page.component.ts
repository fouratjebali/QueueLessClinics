import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { interval, Subscription } from 'rxjs';
import { ApiService } from '../../../app/services/api.service';
import { Clinic, Ticket, Queue } from '../../../app/models';

@Component({
  selector: 'app-public-board-page',
  templateUrl: './public-board-page.component.html',
  styleUrls: ['./public-board-page.component.scss']
})
export class PublicBoardPageComponent implements OnInit, OnDestroy {
  clinic?: Clinic;
  current?: Ticket;
  next: Ticket[] = [];
  time: Date = new Date();
  refreshSub?: Subscription;
  clockSub?: Subscription;

  constructor(private api: ApiService, private route: ActivatedRoute) {}

  ngOnInit(): void {
    const slug = this.route.snapshot.paramMap.get('clinicSlug');
    this.api.getClinics().subscribe(clinics => {
      this.clinic = clinics.find(c => (c as any).slug === slug || c.id === slug);
      if (!this.clinic && clinics.length) this.clinic = clinics[0];
      this.loadBoard();
      this.refreshSub = interval(5000).subscribe(() => this.loadBoard());
    });
    // update clock every second
    this.clockSub = interval(1000).subscribe(() => (this.time = new Date()));
  }

  loadBoard(): void {
    if (!this.clinic) return;
    this.api.getQueues(this.clinic.id).subscribe(queues => {
      const active = queues.find(q => q.is_active);
      if (active) {
        this.api.getTickets({ queue: active.id }).subscribe(tickets => {
          const calling = tickets.find(t => t.status === 'CALLED' || t.status === 'SERVING');
          this.current = calling;
          const waiting = tickets
            .filter(t => t.status === 'WAITING')
            .sort((a, b) => a.position - b.position);
          this.next = waiting.slice(0, 5);
        });
      }
    });
  }

  ngOnDestroy(): void {
    this.refreshSub?.unsubscribe();
    this.clockSub?.unsubscribe();
  }
}