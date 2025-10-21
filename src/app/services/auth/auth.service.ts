import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { environment } from '../../environments/environments';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  
  private apiUrl = `${environment.apiUrl}/api/v1/users`;
  private refreshTokenUrl = `${this.apiUrl}/refresh_token`;

  constructor(
    private http: HttpClient,
  ) {}

  login(username: string, password: string): Observable<any> {
    return this.http
      .post<any>(`${this.apiUrl}/login`, { username, password })
      .pipe(
        switchMap((response) => {
          this.storeTokens(response.access_token, response.refresh_token);
          return of(response);
        }),
        catchError(this.handleError)
      );
  }

  refreshAccessToken(): Observable<any> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return of(null);
    }

    return this.http
      .post<any>(this.refreshTokenUrl, { refresh_token: refreshToken })
      .pipe(
        switchMap((response) => {
          if (response.access_token) {
            this.storeAccessToken(response.access_token);
            return of(response);
          }
          return of(null);
        }),
        catchError(this.handleError)
      );
  }

  logout(): void {
    this.clearTokens();
  }

  private storeTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  private storeAccessToken(accessToken: string): void {
    localStorage.setItem('access_token', accessToken);
  }

  public getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  private clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    console.error(error);
    throw error;
  }
}
