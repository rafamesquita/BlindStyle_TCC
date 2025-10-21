import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AuthService } from './auth/auth.service';
import { environment } from '../environments/environments';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private apiUrl = environment.apiUrl;
  
  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  getClothes() {
    const accessToken = this.authService.getAccessToken();
    let headers = new HttpHeaders();
    if (accessToken) {
      headers = headers.set('Authorization', `Bearer ${accessToken}`);
    }
    return this.http.get(`${this.apiUrl}/api/v1/items/get_item_list`,{ headers });
  }

  getSpecificClothe(id: number) {
    const accessToken = this.authService.getAccessToken();
    let headers = new HttpHeaders();
    if (accessToken) {
      headers = headers.set('Authorization', `Bearer ${accessToken}`);
    }
    return this.http.get(`${this.apiUrl}/api/v1/items/get_item/${id}`,{ headers });
  }

  getDescription(parametro: string) {
    const payload = { input: parametro}
    return this.http.post(`${this.apiUrl}/api/v1/description/description/`, payload);
  }

  registerUser(username: string, password: string) {
    const payload = { username: username, password: password}
    return this.http.post(`${this.apiUrl}/api/v1/users/register_user`, payload);
  }

  postItems(name: string, description: string, imageUrl: string) {
    const accessToken = this.authService.getAccessToken();
    let headers = new HttpHeaders();
    if (accessToken) {
      headers = headers.set('Authorization', `Bearer ${accessToken}`);
    }
    const payload = { name, description, image_url: imageUrl };
    return this.http.post(`${this.apiUrl}/api/v1/items/create_item`, payload, { headers });
  }
  
  getSuggestion(itemId: string) {
    const accessToken = this.authService.getAccessToken();
    let headers = new HttpHeaders();
    if (accessToken) {
      headers = headers.set('Authorization', `Bearer ${accessToken}`);
    }
    return this.http.get(`${this.apiUrl}/api/v1/suggestion/get_last_suggestion/${itemId}`, { headers });
  }
  
  postSuggestion(clothingId: string) { 
    const accessToken = this.authService.getAccessToken();
    let headers = new HttpHeaders();
    if (accessToken) {
      headers = headers.set('Authorization', `Bearer ${accessToken}`);
    }
    return this.http.post(`${this.apiUrl}/api/v1/suggestion/suggest_item/${clothingId}`, null, { headers });
  } 
}