import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

// Additional Material Modules
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDialogModule } from '@angular/material/dialog';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatRadioModule } from '@angular/material/radio';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatMenuModule } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';

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
import { AddEditServiceDialogComponent } from './pages/staff/services-settings-page.component';
import { AddWalkinModalComponent } from './pages/staff/add-walkin-modal.component';
import { UserProfilePageComponent } from './pages/staff/user-profile-page.component';

// Admin pages
import { ClinicsPageComponent } from './pages/admin/clinics-page.component';
import { ClinicDetailPageComponent } from './pages/admin/clinic-detail-page.component';
import { UsersManagementPageComponent } from './pages/admin/users-management-page.component';
import { AnalyticsPageComponent } from './pages/admin/analytics-page.component';
import { AuditLogsPageComponent } from './pages/admin/audit-logs-page.component';
import { SystemSettingsPageComponent } from './pages/admin/system-settings-page.component';

// Shared components
import { KpiCardComponent } from './shared/kpi-card.component';

// Angular Material Modules
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatListModule } from '@angular/material/list';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';

import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';

import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatBadgeModule } from '@angular/material/badge';

@NgModule({
  declarations: [
    AppComponent,
    // Layouts
    PublicLayoutComponent,
    StaffLayoutComponent,
    AdminLayoutComponent,
    // Public pages
    JoinQueuePageComponent,
    PublicHomePageComponent,
    TicketStatusPageComponent,
    TrackTicketPageComponent,
    PublicBoardPageComponent,
    // Auth pages
    LoginPageComponent,
    // Staff pages
    DashboardPageComponent,
    QueueHistoryPageComponent,
    ReportsPageComponent,
    ClinicSettingsPageComponent,
    ServicesSettingsPageComponent,
    AddEditServiceDialogComponent,
    AddWalkinModalComponent,
    UserProfilePageComponent,
    // Admin pages
    ClinicsPageComponent,
    ClinicDetailPageComponent,
    UsersManagementPageComponent,
    AnalyticsPageComponent,
    AuditLogsPageComponent,
    SystemSettingsPageComponent,
    // Shared components
    KpiCardComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    AppRoutingModule,
    // Material modules
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatTableModule,
    MatListModule,
    MatSnackBarModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatSlideToggleModule,
    MatPaginatorModule,
    MatSortModule,
    // Additional Material modules
    MatSidenavModule,
    MatTabsModule,
    MatDialogModule,
    MatCheckboxModule,
    MatRadioModule,
    MatProgressBarModule,
    MatMenuModule,
    MatDividerModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    MatBadgeModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }