import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { Clinic, User } from '../../models';

type NewUserForm = {
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  clinic: string;
};

type EditUserForm = {
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  role: string;
  clinic: string;
};

@Component({
  selector: 'app-users-management-page',
  templateUrl: './users-management-page.component.html',
  styleUrls: ['./users-management-page.component.scss']
})
export class UsersManagementPageComponent implements OnInit {
  users: User[] = [];
  clinics: Clinic[] = [];
  displayedColumns: string[] = ['name', 'email', 'role', 'clinic', 'active', 'actions'];
  roleFilter = '';
  clinicFilter = '';
  activeFilter = '';

  readonly roleOptions: string[] = ['ADMIN', 'STAFF', 'DOCTOR', 'NURSE', 'RECEPTIONIST'];

  showAddUserForm = false;
  isSubmittingUser = false;
  addUserError = '';
  temporaryPassword = '';
  newUser: NewUserForm = this.emptyUserForm();
  showEditUserForm = false;
  isSubmittingEditUser = false;
  editUserError = '';
  editingUserId = '';
  editUserForm: EditUserForm = this.emptyEditUserForm();

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.adminGetClinics().subscribe(data => (this.clinics = data));
    this.loadUsers();
  }

  loadUsers(): void {
    this.api.adminGetUsers({
      role: this.roleFilter,
      clinic: this.clinicFilter,
      is_active: this.activeFilter
    }).subscribe(users => {
      this.users = users;
    });
  }

  openAddUserForm(): void {
    this.showEditUserForm = false;
    this.showAddUserForm = true;
    this.isSubmittingUser = false;
    this.addUserError = '';
    this.temporaryPassword = '';
    this.newUser = this.emptyUserForm();
  }

  cancelAddUser(): void {
    this.showAddUserForm = false;
    this.isSubmittingUser = false;
    this.addUserError = '';
    this.newUser = this.emptyUserForm();
  }

  submitAddUser(): void {
    if (this.isSubmittingUser) return;

    const payload: any = {
      email: this.newUser.email.trim(),
      first_name: this.newUser.first_name.trim(),
      last_name: this.newUser.last_name.trim(),
      role: this.newUser.role,
      clinic: this.newUser.clinic || null,
      is_active: true
    };

    if (!payload.email || !payload.first_name || !payload.last_name || !payload.role) {
      return;
    }

    this.isSubmittingUser = true;
    this.addUserError = '';
    this.temporaryPassword = '';

    this.api.adminCreateUser(payload).subscribe({
      next: (res: any) => {
        this.loadUsers();
        if (res?.temp_password) {
          this.temporaryPassword = `Temporary password: ${res.temp_password}`;
        }
        this.cancelAddUser();
      },
      error: () => {
        this.addUserError = 'Impossible de creer utilisateur';
        this.isSubmittingUser = false;
      }
    });
  }

  openEditUserForm(user: User): void {
    this.showAddUserForm = false;
    this.showEditUserForm = true;
    this.isSubmittingEditUser = false;
    this.editUserError = '';
    this.editingUserId = user.id;
    this.editUserForm = {
      email: user.email || '',
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      phone_number: user.phone_number || '',
      role: user.role || 'STAFF',
      clinic: user.clinic || ''
    };
  }

  cancelEditUser(): void {
    this.showEditUserForm = false;
    this.isSubmittingEditUser = false;
    this.editUserError = '';
    this.editingUserId = '';
    this.editUserForm = this.emptyEditUserForm();
  }

  submitEditUser(): void {
    const user = this.users.find(u => u.id === this.editingUserId);
    const payload: any = {
      email: this.editUserForm.email.trim(),
      first_name: this.editUserForm.first_name.trim(),
      last_name: this.editUserForm.last_name.trim(),
      phone_number: this.editUserForm.phone_number.trim() || null,
      role: this.editUserForm.role,
      clinic: this.editUserForm.clinic || null
    };

    if (!user || !payload.email || !payload.first_name || !payload.last_name || !payload.role || this.isSubmittingEditUser) {
      return;
    }

    this.isSubmittingEditUser = true;
    this.editUserError = '';

    this.api.adminUpdateUser(user.id, payload).subscribe({
      next: updated => {
        Object.assign(user, updated);
        this.cancelEditUser();
      },
      error: () => {
        this.editUserError = 'Impossible de modifier utilisateur';
        this.isSubmittingEditUser = false;
      }
    });
  }

  toggleActive(user: User): void {
    this.api.adminToggleUser(user.id).subscribe({
      next: updated => {
        user.is_active = updated.is_active;
      },
      error: () => {
        alert('Impossible de modifier statut utilisateur');
      }
    });
  }

  resetPassword(user: User): void {
    if (!confirm(`Reset password for ${user.email}?`)) return;
    this.api.adminResetPassword(user.id).subscribe({
      next: res => alert(`Temporary password: ${res.temp_password}`),
      error: () => alert('Reset password failed')
    });
  }

  private emptyUserForm(): NewUserForm {
    return {
      email: '',
      first_name: '',
      last_name: '',
      role: 'STAFF',
      clinic: ''
    };
  }

  private emptyEditUserForm(): EditUserForm {
    return {
      email: '',
      first_name: '',
      last_name: '',
      phone_number: '',
      role: 'STAFF',
      clinic: ''
    };
  }
}
