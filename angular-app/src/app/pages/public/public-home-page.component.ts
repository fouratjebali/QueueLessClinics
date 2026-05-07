import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { catchError, forkJoin, of } from 'rxjs';
import { ApiService } from '../../../app/services/api.service';
import { Clinic, PublicStats, Queue } from '../../../app/models';

type PublicClinic = Clinic & {
  type: string;
  isOpenNow: boolean;
  waitingCount: number;
  avgWaitTime: number;
  hours: string;
};

@Component({
  selector: 'app-public-home-page',
  templateUrl: './public-home-page.component.html',
  styleUrls: ['./public-home-page.component.scss']
})
export class PublicHomePageComponent implements OnInit {
  clinics: PublicClinic[] = [];
  filteredClinics: PublicClinic[] = [];
  loading = true;
  showQuickActions = true;
  searchControl = new FormControl('');
  heroStats: PublicStats = {
    total_patients: 0,
    partner_clinics: 0,
    open_queues: 0,
    in_queue: 0,
    serving_now: 0,
    next_available_time: '--:--'
  };
  
  constructor(
    private api: ApiService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadClinics();
    
    // Set up search filter
    this.searchControl.valueChanges.subscribe(value => {
      this.applyFilter(value || '');
    });
  }

  loadClinics(): void {
    this.loading = true;
    forkJoin({
      clinics: this.api.getClinics(),
      queues: this.api.getQueues(),
      stats: this.api.getPublicStats().pipe(
        catchError(() => of(this.heroStats))
      )
    }).subscribe({
      next: ({ clinics, queues, stats }) => {
        this.clinics = clinics
          .filter(c => c.is_active !== false)
          .map(c => this.toPublicClinic(c, queues));
        this.heroStats = stats;
        this.filteredClinics = [...this.clinics];
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading public data:', error);
        this.loading = false;
        this.showErrorMessage('Failed to load clinics. Please try again.');
      }
    });
  }

  private toPublicClinic(clinic: Clinic, queues: Queue[]): PublicClinic {
    const activeQueue = queues.find(q => q.clinic === clinic.id && q.is_active);
    const avgWaitTime = Number(activeQueue?.current_wait_time ?? activeQueue?.avg_wait_time ?? 0);

    return {
      ...clinic,
      type: this.getClinicType(clinic),
      isOpenNow: clinic.is_active && !!activeQueue,
      waitingCount: activeQueue?.waiting ?? 0,
      avgWaitTime: Math.max(0, Math.round(avgWaitTime)),
      hours: this.getOperatingHours(clinic)
    };
  }

  private getClinicType(clinic: Clinic): string {
    const source = `${clinic.name} ${clinic.description || ''}`.toLowerCase();
    if (source.includes('dental')) return 'dental';
    if (source.includes('pedia')) return 'pediatric';
    if (source.includes('cardio')) return 'cardiology';
    if (source.includes('derma')) return 'dermatology';
    if (source.includes('ortho')) return 'orthopedic';
    return 'general';
  }

  private getOperatingHours(clinic: Clinic): string {
    const settings: any = clinic.settings;
    const monday = settings?.operating_hours?.monday;
    if (monday?.isOpen && monday?.openTime && monday?.closeTime) {
      return `${monday.openTime} - ${monday.closeTime}`;
    }
    return '8:00 AM - 8:00 PM';
  }

  applyFilter(filterValue: string): void {
    const searchTerm = filterValue.toLowerCase().trim();
    
    if (!searchTerm) {
      this.filteredClinics = [...this.clinics];
      return;
    }

    this.filteredClinics = this.clinics.filter(clinic => 
      clinic.name.toLowerCase().includes(searchTerm) ||
      clinic.city.toLowerCase().includes(searchTerm) ||
      clinic.state.toLowerCase().includes(searchTerm) ||
      (clinic as any).type?.toLowerCase().includes(searchTerm)
    );
  }

  filterByType(event: any): void {
    const selectedType = Array.isArray(event?.value) ? event.value[0] : event?.value;
    
    if (!selectedType || selectedType === 'All Clinics') {
      this.filteredClinics = [...this.clinics];
    } else {
      this.filteredClinics = this.clinics.filter(clinic =>
        (clinic as any).type?.toLowerCase() === selectedType.toLowerCase()
      );
    }
  }

  scrollToClinics(): void {
    const clinicsSection = document.querySelector('.clinics-section');
    if (clinicsSection) {
      clinicsSection.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }
  }

  getClinicIcon(type: string): string {
    const icons: { [key: string]: string } = {
      'general': 'local_hospital',
      'dental': 'tooth',
      'pediatric': 'child_care',
      'cardiology': 'favorite',
      'dermatology': 'spa',
      'orthopedic': 'accessibility',
      'default': 'medical_services'
    };
    return icons[type?.toLowerCase()] || icons['default'];
  }

  findNearestClinic(): void {
    if (!navigator.geolocation) {
      this.showErrorMessage('Geolocation is not supported by your browser');
      return;
    }

    this.showInfoMessage('Finding nearest clinics...');

    navigator.geolocation.getCurrentPosition(
      (position) => {
        // Here you would call an API to find clinics near these coordinates
        console.log('User location:', position.coords);
        
        this.sortClinicsByProximity(position.coords);
        
        this.showSuccessMessage('Found clinics near you!');
      },
      (error) => {
        console.error('Geolocation error:', error);
        this.showErrorMessage('Unable to get your location. Please enable location services.');
      }
    );
  }

  private sortClinicsByProximity(coords: GeolocationCoordinates): void {
    if (!coords) return;
    // Placeholder until geospatial support is added server-side.
    this.filteredClinics = [...this.clinics];
  }

  openHelp(): void {
    // You can implement a help dialog or chat here
    this.showInfoMessage('How can we help you? Our support team is ready to assist.');
    
    // Example: Open a dialog
    // const dialogRef = this.dialog.open(HelpDialogComponent, {
    //   width: '400px',
    //   data: { /* any data you want to pass */ }
    // });
  }

  refreshClinics(): void {
    this.loading = true;
    this.showInfoMessage('Refreshing clinics list...');
    
    // Simulate network delay
    setTimeout(() => {
      this.loadClinics();
    }, 1000);
  }

  // Utility methods for showing messages
  private showSuccessMessage(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      panelClass: ['success-snackbar'],
      horizontalPosition: 'center',
      verticalPosition: 'bottom'
    });
  }

  private showErrorMessage(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 5000,
      panelClass: ['error-snackbar'],
      horizontalPosition: 'center',
      verticalPosition: 'bottom'
    });
  }

  private showInfoMessage(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      panelClass: ['info-snackbar'],
      horizontalPosition: 'center',
      verticalPosition: 'bottom'
    });
  }

  // Track by function for *ngFor optimization
  trackByClinicId(index: number, clinic: PublicClinic): string {
    return clinic.id;
  }
}