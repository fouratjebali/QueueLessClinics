import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiService } from '../../services/api.service';
import { AuthSessionService } from '../../services/auth-session.service';

@Component({
  selector: 'app-login-page',
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.scss']
})
export class LoginPageComponent implements OnInit {
  loginForm: FormGroup;
  hide = true;
  loading = false;
  error?: string;
  showDemo = false;

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    private router: Router,
    private route: ActivatedRoute,
    private snackBar: MatSnackBar,
    private authSession: AuthSessionService
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      remember: [false]
    });
  }

  ngOnInit(): void {
    this.clearStaleReturnUrl();
  }

  goToPublic(): void {
    this.router.navigate(['/public'], { replaceUrl: true });
  }

  login(): void {
    if (this.loginForm.invalid) {
      this.markFormGroupTouched(this.loginForm);
      return;
    }

    this.loading = true;
    this.error = undefined;

    const { email, password, remember } = this.loginForm.value;

    this.api.login(email, password).subscribe({
      next: (res: any) => {
        this.loading = false;
        if (res?.token && res?.user) {
          this.authSession.setSession(res.token, res.user, remember);
        }

        // Show success message
        this.snackBar.open('Login successful! Redirecting...', 'Close', {
          duration: 3000,
          panelClass: ['success-snackbar'],
          horizontalPosition: 'center',
          verticalPosition: 'top'
        });

        // Handle role-based redirection
        const role = (res?.role || res?.user?.role || '').toUpperCase();
        const returnUrl = this.getSafeReturnUrl(role);

        setTimeout(() => {
          if (returnUrl) {
            this.router.navigateByUrl(returnUrl, { replaceUrl: true });
          } else {
            switch (role) {
              case 'ADMIN':
                this.router.navigate(['/admin/analytics'], { replaceUrl: true });
                break;
              case 'STAFF':
              case 'DOCTOR':
              case 'NURSE':
              case 'RECEPTIONIST':
                this.router.navigate(['/staff/dashboard'], { replaceUrl: true });
                break;
              default:
                this.router.navigate(['/public'], { replaceUrl: true });
            }
          }
        }, 1500);
      },
      error: (error) => {
        this.loading = false;
        console.error('Login error:', error);
        
        if (error.status === 400 || error.status === 401) {
          this.error = 'Invalid email or password';
        } else if (error.status === 403) {
          this.error = 'Account is locked. Please contact support.';
        } else if (error.status === 0) {
          this.error = 'Network error. Please check your connection.';
        } else {
          this.error = 'An unexpected error occurred. Please try again.';
        }

        // Show error message
        this.snackBar.open(this.error!, 'Close', {
          duration: 5000,
          panelClass: ['error-snackbar'],
          horizontalPosition: 'center',
          verticalPosition: 'top'
        });
      }
    });
  }

  // Helper method to mark all form controls as touched
  private markFormGroupTouched(formGroup: FormGroup) {
    Object.values(formGroup.controls).forEach(control => {
      control.markAsTouched();
      if (control instanceof FormGroup) {
        this.markFormGroupTouched(control);
      }
    });
  }

  // Demo login helper
  fillDemoCredentials(role: 'admin' | 'staff'): void {
    if (role === 'admin') {
      this.loginForm.patchValue({
        email: 'admin@queueless.tn',
        password: 'Password123!'
      });
    } else {
      this.loginForm.patchValue({
        email: 'staff@sfaxmedical.tn',
        password: 'Password123!'
      });
    }
  }

  private clearStaleReturnUrl(): void {
    const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl');
    if (!returnUrl || this.authSession.hasValidSession()) {
      return;
    }

    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {},
      replaceUrl: true
    });
  }

  private getSafeReturnUrl(role: string): string | null {
    const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl');
    if (!returnUrl || !returnUrl.startsWith('/')) {
      return null;
    }
    if (returnUrl.startsWith('/auth')) {
      return null;
    }

    if (returnUrl.startsWith('/admin')) {
      return role === 'ADMIN' ? returnUrl : null;
    }

    if (returnUrl.startsWith('/staff')) {
      const staffRoles = ['STAFF', 'DOCTOR', 'NURSE', 'RECEPTIONIST'];
      return staffRoles.includes(role) ? returnUrl : null;
    }

    return returnUrl.startsWith('/public') ? returnUrl : null;
  }
}