import { Injectable } from '@angular/core';

type StorageArea = 'local' | 'session';

@Injectable({ providedIn: 'root' })
export class AuthSessionService {
  private readonly tokenKey = 'auth_token';
  private readonly userKey = 'current_user';

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey) || sessionStorage.getItem(this.tokenKey);
  }

  getUser<T = any>(): T | null {
    const raw = localStorage.getItem(this.userKey) || sessionStorage.getItem(this.userKey);
    if (!raw) {
      return null;
    }

    try {
      return JSON.parse(raw) as T;
    } catch {
      return null;
    }
  }

  hasValidSession(): boolean {
    return !!this.getToken() && !!this.getUser();
  }

  setSession(token: string, user: any, remember: boolean): void {
    this.clearSession();
    const target = remember ? localStorage : sessionStorage;
    target.setItem(this.tokenKey, token);
    target.setItem(this.userKey, JSON.stringify(user));
  }

  clearSession(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
    sessionStorage.removeItem(this.tokenKey);
    sessionStorage.removeItem(this.userKey);
  }

  getActiveStorage(): StorageArea | null {
    if (localStorage.getItem(this.userKey)) {
      return 'local';
    }
    if (sessionStorage.getItem(this.userKey)) {
      return 'session';
    }
    return null;
  }

  updateStoredUser(partial: any): void {
    const area = this.getActiveStorage();
    if (!area) {
      return;
    }

    const store = area === 'local' ? localStorage : sessionStorage;
    const currentRaw = store.getItem(this.userKey);
    if (!currentRaw) {
      return;
    }

    try {
      const current = JSON.parse(currentRaw);
      store.setItem(this.userKey, JSON.stringify({ ...current, ...partial }));
    } catch {
      // Ignore invalid payload.
    }
  }
}