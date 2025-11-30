import { Component, OnInit } from '@angular/core';
import { ActivatedRoute , Router } from '@angular/router';
import { TextToSpeechService } from './../../services/text-speech/text-to-speech.service';

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [],
  templateUrl: './menu.component.html',
  styleUrl: './menu.component.scss'
})
export class MenuComponent implements OnInit{

  activeButton: 'historico' | 'foto' = 'historico';

  constructor(
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private ttsService: TextToSpeechService,
  ) {}

  ngOnInit (): void {
    const url = this.activatedRoute.snapshot.url.map(segmento => segmento.path).join('/')
    if (url.includes('foto')) {
      this.activeButton = 'foto';
    }
    else if (url.includes('historico')) {
      this.activeButton = 'historico';
    }
    else {
      this.activeButton = 'foto'; // padrão
    }
  }

  goTo (route: string) {
    this.router.navigate([`/${route}`]);
  }

  onSpeak (text: string): void {
    this.ttsService.speak(text);
  }

}
