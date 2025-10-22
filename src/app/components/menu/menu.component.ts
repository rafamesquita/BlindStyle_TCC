import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { TextToSpeechService } from './../../services/text-speech/text-to-speech.service';

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [],
  templateUrl: './menu.component.html',
  styleUrl: './menu.component.scss'
})
export class MenuComponent {

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
