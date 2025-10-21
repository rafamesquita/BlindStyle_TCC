import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ModalRoupaComponent } from "../modal-roupa/modal-roupa.component";
import { TextToSpeechService } from './../../services/text-speech/text-to-speech.service';

@Component({
  selector: 'app-roupa-hist',
  standalone: true,
  imports: [CommonModule, ModalRoupaComponent],
  templateUrl: './roupa-hist.component.html',
  styleUrl: './roupa-hist.component.scss'
})
export class RoupaHistComponent {

  @Input() data: any

  modal: boolean = false

  constructor(private ttsService: TextToSpeechService) {}

  openModal() {
    this.modal = !this.modal
  }
  
  openImg(base64: string, contentType: string = 'image/jpg') {
    const byteCharacters = atob(base64);
    const byteNumbers = Array.from(byteCharacters).map(char => char.charCodeAt(0));
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: contentType }); // Cria o Blob corretamente
    this.displayImageFromBlob(blob); // Passa a instância de Blob para o método
  }

  displayImageFromBlob(blob: Blob) { // Define o tipo como Blob
    const imageUrl = URL.createObjectURL(blob);
    const imgElement = document.createElement('img');
    imgElement.src = imageUrl;
    imgElement.alt = "Imagem Decodificada";
    imgElement.style.maxWidth = "50%";
    imgElement.style.height = "150px";
    const container = document.getElementById('imageContainer');
    if (container) {
        container.appendChild(imgElement);
    } else {
        console.error("Elemento com ID 'imageContainer' não encontrado.");
    }
  }

  onSpeak(text: string): void {
    this.ttsService.speak(text);
  }
}
