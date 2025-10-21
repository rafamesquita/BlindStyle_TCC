import { Component } from '@angular/core';
import { HeaderComponent } from '../../components/header/header.component';
import { Router } from '@angular/router';
import { FooterComponent } from "../../components/footer/footer.component";
import { AuthService } from '../../services/auth/auth.service';
import { FormsModule } from '@angular/forms'; 
import { environment } from '../../environments/environments';
import { TextToSpeechService } from './../../services/text-speech/text-to-speech.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [HeaderComponent, FooterComponent, FormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {

  username: string = '';
  password: string = '';
  errorMessage: string = '';

  constructor(private authService: AuthService,
    private router: Router,
    private ttsService: TextToSpeechService,
  ) {}

  home(): void {
    this.authService.login(this.username, this.password).subscribe(
      (response) => {
        console.log('Usuário logado com sucesso');
        this.router.navigate(['/home']);
      },
      (error) => {
        console.error('Erro no login', error);
        this.errorMessage = error?.error?.detail || 'Erro desconhecido';
      }
    );
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  onSpeak(text: string): void {
    this.ttsService.speak(text);
  }
}