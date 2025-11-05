import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../environments/environments';

@Injectable({
  providedIn: 'root',
})
export class ApiService {

  protected apiUrl = environment.apiUrl;
  protected headers = new HttpHeaders();
  protected accessToken = localStorage.getItem('access_token');
  
  constructor(
    private http: HttpClient
  ) {
    this.headers = new HttpHeaders({
      'Authorization': `Bearer ${this.accessToken}`,
      'ngrok-skip-browser-warning': 'any',
      'accept': 'application/json'
    });
  }

  // Gera a descrição da roupa
  postDescription (parametro: string) {
    const payload = { image_base64: parametro}
    return this.http.post(`${this.apiUrl}/api/v1/api/descriptions/extract-features/upload`, payload, { headers: this.headers });
  }

  // Salva a roupa no histórico
  postItems (body: any) {
    return this.http.post(`${this.apiUrl}/api/v1/items/create`, body, { headers: this.headers });
  }

  // Lista as roupas no histórico
  getClothes () {
    return this.http.get(`${this.apiUrl}/api/v1/items/list-all?page=1&size=10&status=active`, { headers: this.headers })
  }
  
  // Gera a sugestão da roupa
  postSuggestion(itemId: string) {
    return this.http.post(`${this.apiUrl}/api/v1/suggestions/generate?item_id=${itemId}`, '', { headers: this.headers });
  }

}