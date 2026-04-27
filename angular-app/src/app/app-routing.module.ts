import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthRoleGuard } from './auth-role.guard';

// Layouts
import { PublicLayoutComponent } from './layouts/public-layout.component';
import { StaffLayoutComponent } from './layouts/staff-layout.component';
import { AdminLayoutComponent } from './layouts/admin-layout.component';

// Public pages
import { JoinQueuePageComponent } from './pages/public/join-queue-page.component';
import { TicketStatusPageComponent } from './pages/public/ticket-status-page.component';
import { TrackTicketPageComponent } from './pages/public/track-ticket-page.component';
import { PublicBoardPageComponent } from './pages/public/public-board-page.component';
import { PublicHomePageComponent } from './pages/public/public-home-page.component';

// Auth pages
import { LoginPageComponent } from './pages/auth/login-page.component';

// Staff pages
import { DashboardPageComponent } from './pages/staff/dashboard-page.component';
import { QueueHistoryPageComponent } from './pages/staff/queue-history-page.component';
import { ReportsPageComponent } from './pages/staff/reports-page.component';
import { ClinicSettingsPageComponent } from './pages/staff/clinic-settings-page.component';
import { ServicesSettingsPageComponent } from './pages/staff/services-settings-page.component';
import { UserProfilePageComponent } from './pages/staff/user-profile-page.component';

// Admin pages
import { ClinicsPageComponent } from './pages/admin/clinics-page.component';
import { ClinicDetailPageComponent } from './pages/admin/clinic-detail-page.component';
import { UsersManagementPageComponent } from './pages/admin/users-management-page.component';
import { AnalyticsPageComponent } from './pages/admin/analytics-page.component';
import { AuditLogsPageComponent } from './pages/admin/audit-logs-page.component';
import { SystemSettingsPageComponent } from './pages/admin/system-settings-page.component';

const routes: Routes = [
  { path: '', redirectTo: 'public', pathMatch: 'full' },
  {
    path: 'public',
    component: PublicLayoutComponent,
    children: [
      { path: '', component: PublicHomePageComponent },
      { path: 'clinics', component: PublicHomePageComponent },
      { path: 'join', component: PublicHomePageComponent },
      { path: 'join/:slug', component: JoinQueuePageComponent },
      { path: 'ticket/:id', component: TicketStatusPageComponent },
      { path: 'track', component: TrackTicketPageComponent },
      { path: 'appointments', component: PublicHomePageComponent },
      { path: 'contact', component: PublicHomePageComponent },
      { path: 'board/:clinicSlug', component: PublicBoardPageComponent }
    ]
  },
  {
    path: 'auth/login',
    component: LoginPageComponent
  },
  {
    path: 'staff',
    component: StaffLayoutComponent,
    canActivate: [AuthRoleGuard],
    canActivateChild: [AuthRoleGuard],
    data: { roles: ['STAFF', 'DOCTOR', 'NURSE', 'RECEPTIONIST'] },
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: DashboardPageComponent },
      { path: 'queue-history', component: QueueHistoryPageComponent },
      { path: 'reports', component: ReportsPageComponent },
      { path: 'settings', component: ClinicSettingsPageComponent },
      { path: 'services', component: ServicesSettingsPageComponent }
      ,
      { path: 'profile', component: UserProfilePageComponent }
    ]
  },
  {
    path: 'admin',
    component: AdminLayoutComponent,
    canActivate: [AuthRoleGuard],
    canActivateChild: [AuthRoleGuard],
    data: { roles: ['ADMIN'] },
    children: [
      { path: '', redirectTo: 'analytics', pathMatch: 'full' },
      { path: 'dashboard', redirectTo: 'analytics', pathMatch: 'full' },
      { path: 'clinics', component: ClinicsPageComponent },
      { path: 'clinics/:id', component: ClinicDetailPageComponent },
      { path: 'users', component: UsersManagementPageComponent },
      { path: 'analytics', component: AnalyticsPageComponent },
      { path: 'audit-logs', component: AuditLogsPageComponent },
      { path: 'settings', component: SystemSettingsPageComponent }
    ]
  },
  { path: '**', redirectTo: 'public' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
