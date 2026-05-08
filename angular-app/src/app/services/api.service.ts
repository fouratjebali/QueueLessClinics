import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { AuthSessionService } from './auth-session.service';

import { AdminAuditLog, AdminOverview, AdminSystemSettings, Clinic, PublicStats, Queue, Service, StaffClinicContext, StaffClinicKpis, Ticket, User } from '../models';

interface PagedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient, private authSession: AuthSessionService) {}

  private actorHeaders(): HttpHeaders {
    const user = this.authSession.getUser<any>();
    let headers = new HttpHeaders();
    if (user?.role) {
      headers = headers.set('X-User-Role', user.role);
    }
    if (user?.id) {
      headers = headers.set('X-User-Id', user.id);
    }
    if (user?.email) {
      headers = headers.set('X-User-Email', user.email);
    }
    return headers;
  }

  private adminHeaders(): HttpHeaders {
    return this.actorHeaders();
  }

  private unwrapList<T>(payload: T[] | PagedResponse<T>): T[] {
    return Array.isArray(payload) ? payload : payload.results ?? [];
  }

  // Clinics
  getClinics(): Observable<Clinic[]> {
    return this.http
      .get<Clinic[] | PagedResponse<Clinic>>(`${this.baseUrl}/clinics/`)
      .pipe(map(data => this.unwrapList(data)));
  }

  getClinic(id: string): Observable<Clinic> {
    return this.http.get<Clinic>(`${this.baseUrl}/clinics/${id}/`);
  }

  createClinic(data: any): Observable<Clinic> {
    return this.http.post<Clinic>(`${this.baseUrl}/clinics/`, data);
  }

  updateClinic(id: string, data: any): Observable<Clinic> {
    return this.http.patch<Clinic>(`${this.baseUrl}/clinics/${id}/`, data);
  }

  // Services
  getServices(clinicId?: string): Observable<Service[]> {
    let params = new HttpParams();
    if (clinicId) {
      params = params.set('clinic', clinicId);
    }
    return this.http
      .get<Service[] | PagedResponse<Service>>(`${this.baseUrl}/services/`, { params })
      .pipe(map(data => this.unwrapList(data)));
  }

  /**
   * Create a new service for a clinic. Payload should include
   * fields: name, description, estimated_duration, code, is_active and clinic ID.
   */
  createService(data: any): Observable<Service> {
    return this.http.post<Service>(`${this.baseUrl}/services/`, data);
  }

  /**
   * Update an existing service. Only fields provided in the payload will be updated.
   */
  updateService(serviceId: string, data: any): Observable<Service> {
    return this.http.patch<Service>(`${this.baseUrl}/services/${serviceId}/`, data);
  }

  /**
   * Delete a service by ID.
   */
  deleteService(serviceId: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/services/${serviceId}/`);
  }

  // Queues
  getQueues(clinicId?: string): Observable<Queue[]> {
    let params = new HttpParams();
    if (clinicId) {
      params = params.set('clinic', clinicId);
    }
    return this.http
      .get<Queue[] | PagedResponse<Queue>>(`${this.baseUrl}/queues/`, { params })
      .pipe(map(data => this.unwrapList(data)));
  }

  openQueue(queueId: string): Observable<Queue> {
    return this.http.post<Queue>(`${this.baseUrl}/queues/${queueId}/open/`, {});
  }

  closeQueue(queueId: string): Observable<Queue> {
    return this.http.post<Queue>(`${this.baseUrl}/queues/${queueId}/close/`, {});
  }

  callNext(queueId: string): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/queues/${queueId}/call_next/`, {});
  }

  // Tickets
  getTickets(params?: any): Observable<Ticket[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key]) {
          httpParams = httpParams.set(key, params[key]);
        }
      });
    }
    return this.http
      .get<Ticket[] | PagedResponse<Ticket>>(`${this.baseUrl}/tickets/`, { params: httpParams })
      .pipe(map(data => this.unwrapList(data)));
  }

  createTicket(data: any): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/tickets/`, data);
  }

  // Queues: create and delete
  createQueue(data: any): Observable<Queue> {
    return this.http.post<Queue>(`${this.baseUrl}/queues/`, data);
  }

  deleteQueue(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/queues/${id}/`);
  }

  callTicket(ticketId: string): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/tickets/${ticketId}/call/`, {});
  }

  startService(ticketId: string): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/tickets/${ticketId}/start_service/`, {});
  }

  completeTicket(ticketId: string): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/tickets/${ticketId}/complete/`, {});
  }

  cancelTicket(ticketId: string, reason?: string): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/tickets/${ticketId}/cancel/`, { reason });
  }

  markNoShow(ticketId: string): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/tickets/${ticketId}/no_show/`, {});
  }

  // Users
  getUsers(params?: any): Observable<User[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
          httpParams = httpParams.set(key, params[key]);
        }
      });
    }
    return this.http
      .get<User[] | PagedResponse<User>>(`${this.baseUrl}/users/`, { params: httpParams })
      .pipe(map(data => this.unwrapList(data)));
  }

  getUser(userId: string): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/users/${userId}/`);
  }

  createUser(data: any): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/users/`, data);
  }

  updateUser(userId: string, data: any): Observable<User> {
    return this.http.patch<User>(`${this.baseUrl}/users/${userId}/`, data);
  }

  // Authentication
  /**
   * Authenticates a user and returns token/user info.
   *
   * @param email User email
   * @param password User password
   */
  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/login/`, { email, password });
  }

  logout(): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/logout/`, {}, { headers: this.actorHeaders() });
  }

  authMe(): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/auth/me/`, { headers: this.actorHeaders() });
  }

  changePassword(current_password: string, new_password: string): Observable<any> {
    return this.http.post(
      `${this.baseUrl}/auth/change-password/`,
      { current_password, new_password },
      { headers: this.actorHeaders() }
    );
  }

  // Public
  getPublicStats(): Observable<PublicStats> {
    return this.http.get<PublicStats>(`${this.baseUrl}/public/stats/`);
  }

  // Staff - Clinic context
  staffGetClinicContext(): Observable<StaffClinicContext> {
    return this.http.get<StaffClinicContext>(`${this.baseUrl}/staff/clinic/`, { headers: this.actorHeaders() });
  }

  staffUpdateClinic(data: any): Observable<Clinic> {
    return this.http.patch<Clinic>(`${this.baseUrl}/staff/clinic/`, data, { headers: this.actorHeaders() });
  }

  staffGetClinicSettings(): Observable<any> {
    return this.http.get(`${this.baseUrl}/staff/clinic/settings/`, { headers: this.actorHeaders() });
  }

  staffUpdateClinicSettings(data: any): Observable<any> {
    return this.http.patch(`${this.baseUrl}/staff/clinic/settings/`, data, { headers: this.actorHeaders() });
  }

  staffGetClinicKpis(date?: string): Observable<StaffClinicKpis> {
    let httpParams = new HttpParams();
    if (date) {
      httpParams = httpParams.set('date', date);
    }
    return this.http.get<StaffClinicKpis>(`${this.baseUrl}/staff/clinic/kpis/`, {
      params: httpParams,
      headers: this.actorHeaders()
    });
  }

  // Staff - Queues
  staffGetQueues(params?: { date?: string; from?: string; to?: string }): Observable<Queue[]> {
    let httpParams = new HttpParams();
    if (params?.date) httpParams = httpParams.set('date', params.date);
    if (params?.from) httpParams = httpParams.set('from', params.from);
    if (params?.to) httpParams = httpParams.set('to', params.to);
    return this.http.get<Queue[]>(`${this.baseUrl}/staff/queues/`, { params: httpParams, headers: this.actorHeaders() });
  }

  staffOpenQueue(payload?: { date?: string }): Observable<Queue> {
    return this.http.post<Queue>(`${this.baseUrl}/staff/queues/open/`, payload || {}, { headers: this.actorHeaders() });
  }

  staffCloseQueue(queueId: string): Observable<Queue> {
    return this.http.post<Queue>(`${this.baseUrl}/staff/queues/${queueId}/close/`, {}, { headers: this.actorHeaders() });
  }

  // Staff - Tickets
  staffGetTickets(params?: { queue?: string; status?: string; service?: string; search?: string; date?: string; from?: string; to?: string }): Observable<Ticket[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') {
          httpParams = httpParams.set(k, v);
        }
      });
    }
    return this.http.get<Ticket[]>(`${this.baseUrl}/staff/tickets/`, { params: httpParams, headers: this.actorHeaders() });
  }

  staffCreateWalkin(data: any): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/staff/tickets/walkin/`, data, { headers: this.actorHeaders() });
  }

  staffCallTicket(ticketId: string): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/staff/tickets/${ticketId}/call/`, {}, { headers: this.actorHeaders() });
  }

  staffStartTicket(ticketId: string): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/staff/tickets/${ticketId}/start/`, {}, { headers: this.actorHeaders() });
  }

  staffCompleteTicket(ticketId: string): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/staff/tickets/${ticketId}/complete/`, {}, { headers: this.actorHeaders() });
  }

  staffCancelTicket(ticketId: string, reason?: string): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/staff/tickets/${ticketId}/cancel/`, { reason }, { headers: this.actorHeaders() });
  }

  staffNoShowTicket(ticketId: string): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/staff/tickets/${ticketId}/no-show/`, {}, { headers: this.actorHeaders() });
  }

  staffReorderTicket(ticketId: string, payload: { direction?: 'up' | 'down'; position?: number }): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.baseUrl}/staff/tickets/${ticketId}/reorder/`, payload, { headers: this.actorHeaders() });
  }

  staffPatchTicket(ticketId: string, data: { notes?: string; service?: string | null; priority?: string }): Observable<Ticket> {
    return this.http.patch<Ticket>(`${this.baseUrl}/staff/tickets/${ticketId}/`, data, { headers: this.actorHeaders() });
  }

  // Staff - Services
  staffGetServices(): Observable<Service[]> {
    return this.http.get<Service[]>(`${this.baseUrl}/staff/services/`, { headers: this.actorHeaders() });
  }

  staffCreateService(data: any): Observable<Service> {
    return this.http.post<Service>(`${this.baseUrl}/staff/services/`, data, { headers: this.actorHeaders() });
  }

  staffUpdateService(serviceId: string, data: any): Observable<Service> {
    return this.http.patch<Service>(`${this.baseUrl}/staff/services/${serviceId}/`, data, { headers: this.actorHeaders() });
  }

  staffDeleteService(serviceId: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/staff/services/${serviceId}/`, { headers: this.actorHeaders() });
  }

  // Admin - Clinics
  adminGetClinics(params?: { search?: string; is_active?: string; city?: string }): Observable<Clinic[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') {
          httpParams = httpParams.set(k, v);
        }
      });
    }
    return this.http.get<Clinic[]>(`${this.baseUrl}/admin/clinics/`, { params: httpParams, headers: this.adminHeaders() });
  }

  adminCreateClinic(data: any): Observable<Clinic> {
    return this.http.post<Clinic>(`${this.baseUrl}/admin/clinics/`, data, { headers: this.adminHeaders() });
  }

  adminGetClinic(id: string): Observable<Clinic> {
    return this.http.get<Clinic>(`${this.baseUrl}/admin/clinics/${id}/`, { headers: this.adminHeaders() });
  }

  adminUpdateClinic(id: string, data: any): Observable<Clinic> {
    return this.http.patch<Clinic>(`${this.baseUrl}/admin/clinics/${id}/`, data, { headers: this.adminHeaders() });
  }

  adminToggleClinic(id: string): Observable<{ id: string; is_active: boolean }> {
    return this.http.post<{ id: string; is_active: boolean }>(`${this.baseUrl}/admin/clinics/${id}/toggle-active/`, {}, { headers: this.adminHeaders() });
  }

  adminUpdateClinicBranding(id: string, data: any): Observable<Clinic> {
    return this.http.patch<Clinic>(`${this.baseUrl}/admin/clinics/${id}/branding/`, data, { headers: this.adminHeaders() });
  }

  adminUpdateClinicLogo(id: string, logo: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/admin/clinics/${id}/logo/`, { logo }, { headers: this.adminHeaders() });
  }

  adminUpdateClinicRules(id: string, data: any): Observable<any> {
    return this.http.patch(`${this.baseUrl}/admin/clinics/${id}/rules/`, data, { headers: this.adminHeaders() });
  }

  adminUpdateClinicHours(id: string, operating_hours: any): Observable<any> {
    return this.http.patch(`${this.baseUrl}/admin/clinics/${id}/hours/`, { operating_hours }, { headers: this.adminHeaders() });
  }

  adminGetClinicServices(id: string): Observable<Service[]> {
    return this.http.get<Service[]>(`${this.baseUrl}/admin/clinics/${id}/services/`, { headers: this.adminHeaders() });
  }

  adminCreateClinicService(id: string, data: any): Observable<Service> {
    return this.http.post<Service>(`${this.baseUrl}/admin/clinics/${id}/services/`, data, { headers: this.adminHeaders() });
  }

  adminUpdateService(serviceId: string, data: any): Observable<Service> {
    return this.http.patch<Service>(`${this.baseUrl}/admin/services/${serviceId}/`, data, { headers: this.adminHeaders() });
  }

  adminDeleteService(serviceId: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/admin/services/${serviceId}/`, { headers: this.adminHeaders() });
  }

  adminReorderServices(service_ids: string[]): Observable<any> {
    return this.http.post(`${this.baseUrl}/admin/services/reorder/`, { service_ids }, { headers: this.adminHeaders() });
  }

  // Admin - Users
  adminGetUsers(params?: { role?: string; clinic?: string; is_active?: string }): Observable<User[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') {
          httpParams = httpParams.set(k, v);
        }
      });
    }
    return this.http.get<User[]>(`${this.baseUrl}/admin/users/`, { params: httpParams, headers: this.adminHeaders() });
  }

  adminCreateUser(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/admin/users/`, data, { headers: this.adminHeaders() });
  }

  adminGetUser(id: string): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/admin/users/${id}/`, { headers: this.adminHeaders() });
  }

  adminUpdateUser(id: string, data: any): Observable<User> {
    return this.http.patch<User>(`${this.baseUrl}/admin/users/${id}/`, data, { headers: this.adminHeaders() });
  }

  adminToggleUser(id: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/admin/users/${id}/toggle-active/`, {}, { headers: this.adminHeaders() });
  }

  adminResetPassword(id: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/admin/users/${id}/reset-password/`, {}, { headers: this.adminHeaders() });
  }

  adminSetRole(id: string, role: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/admin/users/${id}/set-role/`, { role }, { headers: this.adminHeaders() });
  }

  adminAssignClinic(id: string, clinic: string | null): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/admin/users/${id}/assign-clinic/`, { clinic }, { headers: this.adminHeaders() });
  }

  // Admin - Analytics
  adminGetOverview(params?: { from?: string; to?: string }): Observable<AdminOverview> {
    let httpParams = new HttpParams();
    if (params?.from) httpParams = httpParams.set('from', params.from);
    if (params?.to) httpParams = httpParams.set('to', params.to);
    return this.http.get<AdminOverview>(`${this.baseUrl}/admin/analytics/overview/`, { params: httpParams, headers: this.adminHeaders() });
  }

  adminGetClinicRanking(params?: { from?: string; to?: string }): Observable<any[]> {
    let httpParams = new HttpParams();
    if (params?.from) httpParams = httpParams.set('from', params.from);
    if (params?.to) httpParams = httpParams.set('to', params.to);
    return this.http.get<any[]>(`${this.baseUrl}/admin/analytics/clinic-ranking/`, { params: httpParams, headers: this.adminHeaders() });
  }

  adminGetTicketsTimeseries(params?: { from?: string; to?: string; group?: 'day' | 'week' }): Observable<any[]> {
    let httpParams = new HttpParams();
    if (params?.from) httpParams = httpParams.set('from', params.from);
    if (params?.to) httpParams = httpParams.set('to', params.to);
    if (params?.group) httpParams = httpParams.set('group', params.group);
    return this.http.get<any[]>(`${this.baseUrl}/admin/analytics/tickets-timeseries/`, { params: httpParams, headers: this.adminHeaders() });
  }

  adminGetStatusDistribution(params?: { from?: string; to?: string }): Observable<any[]> {
    let httpParams = new HttpParams();
    if (params?.from) httpParams = httpParams.set('from', params.from);
    if (params?.to) httpParams = httpParams.set('to', params.to);
    return this.http.get<any[]>(`${this.baseUrl}/admin/analytics/status-distribution/`, { params: httpParams, headers: this.adminHeaders() });
  }

  adminGetPeakHours(params?: { from?: string; to?: string }): Observable<any[]> {
    let httpParams = new HttpParams();
    if (params?.from) httpParams = httpParams.set('from', params.from);
    if (params?.to) httpParams = httpParams.set('to', params.to);
    return this.http.get<any[]>(`${this.baseUrl}/admin/analytics/peak-hours/`, { params: httpParams, headers: this.adminHeaders() });
  }

  adminDownloadCsv(params?: { from?: string; to?: string }): Observable<Blob> {
    let httpParams = new HttpParams();
    if (params?.from) httpParams = httpParams.set('from', params.from);
    if (params?.to) httpParams = httpParams.set('to', params.to);
    return this.http.get(`${this.baseUrl}/admin/analytics/export-csv/`, {
      params: httpParams,
      headers: this.adminHeaders(),
      responseType: 'blob'
    });
  }

  adminDownloadPdf(params?: { from?: string; to?: string }): Observable<Blob> {
    let httpParams = new HttpParams();
    if (params?.from) httpParams = httpParams.set('from', params.from);
    if (params?.to) httpParams = httpParams.set('to', params.to);
    return this.http.get(`${this.baseUrl}/admin/analytics/export-pdf/`, {
      params: httpParams,
      headers: this.adminHeaders(),
      responseType: 'blob'
    });
  }

  // Admin - Audit logs
  adminGetAuditLogs(params?: { actor?: string; clinic?: string; action?: string; from?: string; to?: string }): Observable<AdminAuditLog[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') {
          httpParams = httpParams.set(k, v);
        }
      });
    }
    return this.http.get<AdminAuditLog[]>(`${this.baseUrl}/admin/audit-logs/`, { params: httpParams, headers: this.adminHeaders() });
  }

  adminGetAuditLog(id: string): Observable<AdminAuditLog> {
    return this.http.get<AdminAuditLog>(`${this.baseUrl}/admin/audit-logs/${id}/`, { headers: this.adminHeaders() });
  }

  // Admin - System settings
  adminGetSystemSettings(): Observable<AdminSystemSettings> {
    return this.http.get<AdminSystemSettings>(`${this.baseUrl}/admin/settings/`, { headers: this.adminHeaders() });
  }

  adminPatchSystemSettings(data: Partial<AdminSystemSettings>): Observable<AdminSystemSettings> {
    return this.http.patch<AdminSystemSettings>(`${this.baseUrl}/admin/settings/`, data, { headers: this.adminHeaders() });
  }

  adminTestNotification(payload: { target: string; channel: 'EMAIL' | 'SMS' }): Observable<any> {
    return this.http.post(`${this.baseUrl}/admin/settings/test-notification/`, payload, { headers: this.adminHeaders() });
  }
}
