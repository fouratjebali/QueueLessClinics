import { Component, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { MatSidenav } from '@angular/material/sidenav';
import { AuthSessionService } from '../services/auth-session.service';

@Component({
  selector: 'app-admin-layout',
  templateUrl: './admin-layout.component.html',
  styleUrls: ['./admin-layout.component.scss']
})
export class AdminLayoutComponent {
  @ViewChild('drawer') drawer!: MatSidenav;
  readonly currentUser = this.authSession.getUser<any>();

  constructor(
    private router: Router,
    private authSession: AuthSessionService
  ) {}

  get userFullName(): string {
    const first = this.currentUser?.first_name || '';
    const last = this.currentUser?.last_name || '';
    const full = `${first} ${last}`.trim();
    return full || 'Admin User';
  }

  get userInitials(): string {
    const first = (this.currentUser?.first_name || 'A').charAt(0);
    const last = (this.currentUser?.last_name || 'U').charAt(0);
    return `${first}${last}`.toUpperCase();
  }

  logout(): void {
    this.authSession.clearSession();
    this.router.navigate(['/auth/login'], { replaceUrl: true });
  }
}