import { Component } from '@angular/core';
import { HeaderComponent } from '../../components/header/header.component';
import { Router } from '@angular/router';
import { FooterComponent } from "../../components/footer/footer.component";
import { ApiService } from './../../services/api.service';
import { FormsModule } from '@angular/forms';
import { TextToSpeechService } from './../../services/text-speech/text-to-speech.service';

@Component({
  selector: 'app-cadastro',
  standalone: true,
  imports: [HeaderComponent, FooterComponent, FormsModule],
  templateUrl: './cadastro.component.html',
  styleUrl: './cadastro.component.scss'
})
export class CadastroComponent {
  user: any
  username: string = ''
  password: string = ''

  constructor(
    private router: Router,
    private ApiService: ApiService,
    private ttsService: TextToSpeechService,
  ) {}

  login(){
    this.router.navigate(['/login']);
  }

  register(){
    this.registerUser(this.username, this.password);
  }

  registerUser(username: string, password: string) {
    this.ApiService.registerUser(username, password).subscribe({
      next: (res)=>{
        this.user = res
        console.log(this.user);
        this.router.navigate(['/login']);
      },
      error: (error)=>{
        console.error(error)
      }
    })
  }

  onSpeak(text: string): void {
    this.ttsService.speak(text);
  }
}
