import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { AdminAuditLog, Clinic } from '../../models';

@Component({
  selector: 'app-audit-logs-page',
  templateUrl: './audit-logs-page.component.html',
  styleUrls: ['./audit-logs-page.component.scss']
})
export class AuditLogsPageComponent implements OnInit {
  logs: AdminAuditLog[] = [];
  clinics: Clinic[] = [];
  selectedLog?: AdminAuditLog;

  filterActor = '';
  filterAction = '';
  filterClinic = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.adminGetClinics().subscribe(data => (this.clinics = data));
    this.loadLogs();
  }

  loadLogs(): void {
    this.api.adminGetAuditLogs({
      actor: this.filterActor,
      action: this.filterAction,
      clinic: this.filterClinic
    }).subscribe(data => (this.logs = data));
  }

  viewLog(log: AdminAuditLog): void {
    this.api.adminGetAuditLog(log.id).subscribe(data => (this.selectedLog = data));
  }
}