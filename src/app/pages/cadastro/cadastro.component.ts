import { Component } from '@angular/core';
import { HeaderComponent } from '../../components/header/header.component';
import { Router } from '@angular/router';
import { FooterComponent } from "../../components/footer/footer.component";
import { AuthService } from '../../services/auth/auth.service';
import { FormsModule } from '@angular/forms';
import { TextToSpeechService } from './../../services/text-speech/text-to-speech.service';

@Component({
  selector: 'app-cadastro',
  standalone: true,
  imports: [
    HeaderComponent,
    FooterComponent,
    FormsModule,
  ],
  templateUrl: './cadastro.component.html',
  styleUrl: './cadastro.component.scss'
})
export class CadastroComponent {

  user: any;
  username: string = '';
  email: string = '';
  password: string = '';

  constructor(
    private router: Router,
    private AuthService: AuthService,
    private ttsService: TextToSpeechService,
  ) {}

  login () {
    this.router.navigate(['/login']);
  }

  registerUser () {
    this.AuthService.registerUser(this.username, this.email, this.password).subscribe({
      next: (res)=>{
        this.user = res;
        this.router.navigate(['/login']);
      }
    })
  }

  onSpeak(text: string): void {
    this.ttsService.speak(text);
  }
}
