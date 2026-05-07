import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { User } from '../../models';
import { AuthSessionService } from '../../services/auth-session.service';

@Component({
  selector: 'app-user-profile-page',
  templateUrl: './user-profile-page.component.html',
  styleUrls: ['./user-profile-page.component.scss']
})
export class UserProfilePageComponent implements OnInit {
  profileForm!: FormGroup;
  user?: User;
  loading = true;
  errorMessage = '';
  infoMessage = '';

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    private authSession: AuthSessionService
  ) {}

  ngOnInit(): void {
    this.profileForm = this.fb.group({
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      email: [{ value: '', disabled: true }, [Validators.required, Validators.email]],
      phone: [''],
      current_password: [''],
      new_password: [''],
      confirm_password: ['']
    });

    const current = this.authSession.getUser<User>();
    if (current?.id) {
      this.api.getUser(current.id).subscribe({
        next: user => {
          this.applyUser(user);
        },
        error: () => {
          this.api.authMe().subscribe({
            next: me => {
              this.applyUser(me);
            },
            error: err => {
              this.loading = false;
              this.errorMessage = err?.error?.detail || 'Unable to load profile.';
            }
          });
        }
      });
      return;
    }

    this.api.authMe().subscribe({
      next: me => this.applyUser(me),
      error: err => {
        this.loading = false;
        this.errorMessage = err?.error?.detail || 'Unable to load profile.';
      }
    });
  }

  saveProfile(): void {
    if (this.profileForm.invalid || !this.user) return;

    this.errorMessage = '';
    this.infoMessage = '';

    const newPassword = this.profileForm.value.new_password;
    const confirmPassword = this.profileForm.value.confirm_password;
    const currentPassword = this.profileForm.value.current_password;

    if (newPassword || confirmPassword || currentPassword) {
      if (!currentPassword) {
        this.errorMessage = 'Current password is required to set a new password.';
        return;
      }
      if (newPassword !== confirmPassword) {
        this.errorMessage = 'New password and confirmation do not match.';
        return;
      }
      if (newPassword && newPassword.length < 8) {
        this.errorMessage = 'New password must be at least 8 characters.';
        return;
      }
    }

    const payload = {
      first_name: this.profileForm.value.first_name,
      last_name: this.profileForm.value.last_name,
      phone_number: this.profileForm.value.phone || null
    };

    this.api.updateUser(this.user.id, payload).subscribe({
      next: updated => {
        this.user = updated;
        this.authSession.updateStoredUser(updated);

        if (newPassword) {
          this.api.changePassword(currentPassword, newPassword).subscribe({
            next: () => {
              this.infoMessage = 'Profile and password updated successfully.';
              this.profileForm.patchValue({
                current_password: '',
                new_password: '',
                confirm_password: ''
              });
            },
            error: err => {
              this.errorMessage = err?.error?.detail || 'Profile updated, but password change failed.';
            }
          });
          return;
        }

        this.infoMessage = 'Profile updated successfully.';
      },
      error: err => {
        this.errorMessage = err?.error?.detail || 'Unable to update profile.';
      }
    });
  }

  private applyUser(user: User): void {
    this.user = user;
    this.profileForm.patchValue({
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      phone: user.phone_number || ''
    });
    this.loading = false;
  }
}