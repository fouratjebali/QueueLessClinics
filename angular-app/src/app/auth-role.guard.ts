import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, CanActivateChild, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { AuthSessionService } from './services/auth-session.service';

@Injectable({ providedIn: 'root' })
export class AuthRoleGuard implements CanActivate, CanActivateChild {
  constructor(
    private router: Router,
    private authSession: AuthSessionService
  ) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean | UrlTree | Promise<boolean | UrlTree> {
    if (!this.authSession.hasValidSession()) {
      return this.router.navigate(['/auth/login'], { replaceUrl: true }).then(() => false);
    }

    const user = this.authSession.getUser<any>();
    const role = user?.role as string | undefined;
    const allowedRoles = (route.data['roles'] as string[] | undefined)
      || (route.parent?.data['roles'] as string[] | undefined);

    if (!allowedRoles || !allowedRoles.length) {
      return true;
    }
    if (role && allowedRoles.includes(role)) {
      return true;
    }

    return this.router.navigate(['/auth/login'], { replaceUrl: true }).then(() => false);
  }

  canActivateChild(childRoute: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean | UrlTree | Promise<boolean | UrlTree> {
    return this.canActivate(childRoute, state);
  }
}