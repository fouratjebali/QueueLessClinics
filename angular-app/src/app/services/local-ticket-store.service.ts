import { Injectable } from '@angular/core';

export interface StoredTicket {
  id: string;
  ticketNumber: string;
  clinicName?: string;
  patientName?: string;
  status?: string;
  savedAt: string;
}

@Injectable({ providedIn: 'root' })
export class LocalTicketStoreService {
  private readonly storageKey = 'public_recent_tickets';
  private readonly maxItems = 8;

  getTickets(): StoredTicket[] {
    const raw = localStorage.getItem(this.storageKey);
    if (!raw) return [];
    try {
      const parsed = JSON.parse(raw) as StoredTicket[];
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }

  addTicket(ticket: Omit<StoredTicket, 'savedAt'>): void {
    const current = this.getTickets().filter(t => t.id !== ticket.id);
    const next: StoredTicket[] = [
      { ...ticket, savedAt: new Date().toISOString() },
      ...current
    ].slice(0, this.maxItems);
    localStorage.setItem(this.storageKey, JSON.stringify(next));
  }

  removeTicket(id: string): void {
    const next = this.getTickets().filter(t => t.id !== id);
    localStorage.setItem(this.storageKey, JSON.stringify(next));
  }

  clear(): void {
    localStorage.removeItem(this.storageKey);
  }
}
