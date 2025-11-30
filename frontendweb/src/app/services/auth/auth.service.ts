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
  private refreshInterval: any;

  constructor(
    private http: HttpClient,
  ) {}

  registerUser(username: string, email: string, password: string) {
    const payload = { name: username, email: email, password: password}
    return this.http.post(`${this.apiUrl}/register`, payload);
  }

  login(email: string, password: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/login`, { email, password }).pipe(
      switchMap((response) => {
        this.storeTokens(response.access_token, response.refresh_token);

        this.startAutoRefresh();

        return of(response);
      }),
    catchError(this.handleError));
  }

  startAutoRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }

    // 5 minutos = 300.000 ms
    this.refreshInterval = setInterval(() => {
      this.refreshAccessToken().subscribe({
        next: (res) => console.log("Token atualizado", res),
        error: (err) => console.error("Erro ao atualizar token", err)
      });
    }, 300000);
  }

  refreshAccessToken(): Observable<any> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return of(null);
    }

    return this.http.post<any>(this.refreshTokenUrl, { refresh_token: refreshToken }).pipe(
      switchMap((response) => {
        if (response.access_token) {
          this.storeAccessToken(response.access_token);
          return of(response);
        }
        return of(null);
      }),
    catchError(this.handleError));
  }

  logout(): void {
    localStorage.clear();

    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }

  private storeTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  private storeAccessToken(accessToken: string): void {
    localStorage.setItem('access_token', accessToken);
  }

  private getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    throw error;
  }
}