import { Component } from '@angular/core';
import { HeaderComponent } from "../../components/header/header.component";
import { Router } from '@angular/router';
import { TextToSpeechService } from './../../services/text-speech/text-to-speech.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [HeaderComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent {

  constructor(
      private router: Router,
      private ttsService: TextToSpeechService,
    ) {}

  goTo(route: string) {
    this.router.navigate([`/${route}`]);
  }

  onSpeak(text: string): void {
    this.ttsService.speak(text);
  }
}
