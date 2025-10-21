import { Component, ViewChild, ElementRef, AfterViewInit, Injectable } from '@angular/core';
import { HeaderComponent } from '../../components/header/header.component';
import { CommonModule } from '@angular/common';
import { ApiService } from './../../services/api.service';
import { ModalRoupaComponent } from '../../components/modal-roupa/modal-roupa.component';
import { TextToSpeechService } from './../../services/text-speech/text-to-speech.service';

@Component({
  selector: 'app-galeria',
  standalone: true,
  imports: [HeaderComponent, CommonModule, ModalRoupaComponent],
  templateUrl: './galeria.component.html',
  styleUrl: './galeria.component.scss'
})
export class GaleriaComponent {

  @ViewChild('fileInput') fileInput!: ElementRef;

  selectedImage: string | null = null;
  imageBase64: string | null = null;
  prediction: any
  modal: boolean = false
  loading: boolean = false

  constructor(
    private ApiService: ApiService,
    private ttsService: TextToSpeechService,
  ) {}

  getDescription(img: string) {
    this.ApiService.getDescription(img).subscribe({
      next: (res)=>{
        this.prediction = res
        console.log('Descrição: ', this.prediction);
        setTimeout(() => {
          this.openModal()
          this.loading = false
        }, 2000);
      },
      error: (error)=>{
        console.error(error)
      }
    })
  }

  // Abre a galeria ao clicar no botão
  openGallery(): void {
    this.fileInput.nativeElement.click();
  }

  // Manipula a seleção da imagem
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const file = input.files[0];
      const reader = new FileReader();
      reader.onload = () => {
        this.selectedImage = reader.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

  // Converte a imagem selecionada para Base64
  convertToBase64(): void {
    this.loading = true
    if (this.selectedImage) {
      this.imageBase64 = this.selectedImage;
      console.log('Imagem em Base64:', this.imageBase64);
      this.getDescription(this.imageBase64);
    }
  }

  openModal() {
    this.modal = !this.modal
  }

  onSpeak(text: string): void {
    this.ttsService.speak(text);
  }
}

