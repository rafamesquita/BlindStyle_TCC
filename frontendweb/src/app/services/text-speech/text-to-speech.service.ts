import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class TextToSpeechService {
  private synth = window.speechSynthesis;

  speak(text: string): void {
    if (this.synth.speaking) return;

    const utterance = new SpeechSynthesisUtterance(text);
    this.synth.speak(utterance);
  }
}
