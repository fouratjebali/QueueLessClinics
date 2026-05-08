import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { AdminOverview } from '../../models';

@Component({
  selector: 'app-analytics-page',
  templateUrl: './analytics-page.component.html',
  styleUrls: ['./analytics-page.component.scss']
})
export class AnalyticsPageComponent implements OnInit {
  overview?: AdminOverview;
  ranking: any[] = [];
  timeseries: any[] = [];
  statusDistribution: any[] = [];
  peakHours: any[] = [];

  fromDate = '';
  toDate = '';
  group: 'day' | 'week' = 'day';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    const params = {
      from: this.fromDate || undefined,
      to: this.toDate || undefined
    };
    this.api.adminGetOverview(params).subscribe(data => (this.overview = data));
    this.api.adminGetClinicRanking(params).subscribe(data => (this.ranking = data));
    this.api.adminGetTicketsTimeseries({ ...params, group: this.group }).subscribe(data => (this.timeseries = data));
    this.api.adminGetStatusDistribution(params).subscribe(data => (this.statusDistribution = data));
    this.api.adminGetPeakHours(params).subscribe(data => (this.peakHours = data));
  }

  exportCsv(): void {
    this.api.adminDownloadCsv({ from: this.fromDate || undefined, to: this.toDate || undefined }).subscribe(blob => {
      this.downloadBlob(blob, 'admin-analytics.csv');
    });
  }

  exportPdf(): void {
    this.api.adminDownloadPdf({ from: this.fromDate || undefined, to: this.toDate || undefined }).subscribe(blob => {
      this.downloadBlob(blob, 'admin-summary.pdf');
    });
  }

  private downloadBlob(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }
}
