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
  
  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {
    const accessToken = localStorage.getItem('access_token');
    this.headers = new HttpHeaders({
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    });
  }

  getClothes() {
    return this.http.get(`${this.apiUrl}/api/v1/items/list-all?page=1&size=10&status=active`, { headers: this.headers });
  }

  getSpecificClothe(id: number) {
    return this.http.get(`${this.apiUrl}/api/v1/items/get_item/${id}`, { headers: this.headers });
  }

  getDescription(parametro: string) {
    const payload = { image_base64: parametro}
    return this.http.post(`${this.apiUrl}/api/v1/api/descriptions/extract-features/upload`, payload, { headers: this.headers });
  }

  postItems(body: any) {
    return this.http.post(`${this.apiUrl}/api/v1/itemscreate`, body, { headers: this.headers });
  }
  
  getSuggestion(itemId: string) {
    return this.http.get(`${this.apiUrl}/api/v1/suggestions/generate?item_id=${itemId}`, { headers: this.headers });
  }
  
  postSuggestion(clothingId: string) { 
    return this.http.post(`${this.apiUrl}/api/v1/suggestion/suggest_item/${clothingId}`, null, { headers: this.headers });
  } 
}