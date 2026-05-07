import { Component, HostListener, OnDestroy, OnInit } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthSessionService } from '../services/auth-session.service';
import { LocalTicketStoreService, StoredTicket } from '../services/local-ticket-store.service';
import { Subscription } from 'rxjs';
import { filter } from 'rxjs/operators';


@Component({
  selector: 'app-public-layout',
  templateUrl: './public-layout.component.html',
  styleUrls: ['./public-layout.component.scss']
})
export class PublicLayoutComponent implements OnInit, OnDestroy {
  mobileMenuOpen = false;
  currentYear = new Date().getFullYear();
  isScrolled = false;
  recentTickets: StoredTicket[] = [];
  private routerSub?: Subscription;

  constructor(
    private router: Router,
    private snackBar: MatSnackBar,
    private authSession: AuthSessionService,
    private ticketStore: LocalTicketStoreService
  ) {}

  ngOnInit(): void {
    this.loadRecentTickets();
    this.routerSub = this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => this.loadRecentTickets());
  }

  ngOnDestroy(): void {
    this.routerSub?.unsubscribe();
  }

  @HostListener('window:scroll')
  onWindowScroll() {
    this.isScrolled = window.scrollY > 50;
  }

  @HostListener('window:resize')
  onWindowResize() {
    if (window.innerWidth > 768) {
      this.mobileMenuOpen = false;
    }
  }

  toggleMobileMenu(): void {
    this.mobileMenuOpen = !this.mobileMenuOpen;

    // Prevent body scrolling when mobile menu is open
    if (this.mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
  }

  logout(): void {
    this.authSession.clearSession();

    this.snackBar.open('Logged out successfully', 'Close', {
      duration: 3000,
      panelClass: ['success-snackbar']
    });

    this.router.navigate(['/public'], { replaceUrl: true });
  }

  onRouteChange(): void {
    if (this.mobileMenuOpen) {
      this.toggleMobileMenu();
    }
    this.loadRecentTickets();
  }

  scrollToClinics(): void {
    const scrollNow = () => {
      const clinicsSection = document.querySelector('.clinics-section');
      if (clinicsSection) {
        clinicsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    };

    if (this.router.url.startsWith('/public')) {
      scrollNow();
      return;
    }

    this.router.navigate(['/public']).then(() => {
      setTimeout(scrollNow, 50);
    });
  }

  scrollToFooter(): void {
    const scrollNow = () => {
      const footer = document.querySelector('.public-footer');
      if (footer) {
        footer.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    };

    if (this.router.url.startsWith('/public')) {
      scrollNow();
      return;
    }

    this.router.navigate(['/public']).then(() => {
      setTimeout(scrollNow, 50);
    });
  }
  loadRecentTickets(): void {
    this.recentTickets = this.ticketStore.getTickets();
  }

  openTicket(ticket: StoredTicket): void {
    this.router.navigate(['/public/ticket', ticket.id]);
  }

  removeTicket(ticket: StoredTicket): void {
    this.ticketStore.removeTicket(ticket.id);
    this.loadRecentTickets();
  }

  clearRecentTickets(): void {
    this.ticketStore.clear();
    this.loadRecentTickets();
    this.snackBar.open('Recent tickets cleared', 'Close', {
      duration: 2000,
      panelClass: ['success-snackbar']
    });
  }

  trackByTicketId(index: number, ticket: StoredTicket): string {
    return ticket.id;
  }

  get unreadNotificationsCount(): number {
    return this.recentTickets.length;
  }

  markAllAsRead(): void {
    // Kept for template compatibility; no-op for anonymous patients.
    this.snackBar.open('No account notifications for guest users', 'Close', {
      duration: 2000,
      panelClass: ['success-snackbar']
    });
  }
}
