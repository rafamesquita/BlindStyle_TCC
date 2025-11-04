import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AuthService } from './auth/auth.service';
import { environment } from '../environments/environments';

@Injectable({
  providedIn: 'root',
})
export class ApiService {

  protected apiUrl = environment.apiUrl;
  protected headers = new HttpHeaders();
  protected accessToken = localStorage.getItem('access_token');
  
  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {
    this.headers = new HttpHeaders({
      'Authorization': `Bearer ${this.accessToken}`,
      'Content-Type': 'application/json'
    });
  }

  getClothes() {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.accessToken}`,
      'ngrok-skip-browser-warning': 'any',
      'accept': 'application/json'
    });
    return this.http.get(`${this.apiUrl}/api/v1/items/list-all?page=1&size=10&status=active`, { headers: headers })
  }

  getDescription(parametro: string) {
    const payload = { image_base64: parametro}
    return this.http.post(`${this.apiUrl}/api/v1/api/descriptions/extract-features/upload`, payload, { headers: this.headers });
  }

  postItems(body: any) {
    return this.http.post(`${this.apiUrl}/api/v1/itemscreate`, body, { headers: this.headers });
  }
  
  getSuggestion(itemId: string) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.accessToken}`,
      'ngrok-skip-browser-warning': 'any',
      'accept': 'application/json'
    });
    return this.http.post(`${this.apiUrl}/api/v1/suggestions/generate?item_id=${itemId}`, '', { headers: headers });
  }

}