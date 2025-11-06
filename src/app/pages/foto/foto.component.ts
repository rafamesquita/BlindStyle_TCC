import { Component, ViewChild, ElementRef, OnDestroy  } from '@angular/core';
import { CommonModule } from '@angular/common';

//Components
import { HeaderComponent } from "../../components/header/header.component";
import { MenuComponent } from "../../components/menu/menu.component";
import { ModalRoupaComponent } from '../../components/modal-roupa/modal-roupa.component';

//Services
import { ApiService } from './../../services/api.service';
import { TextToSpeechService } from './../../services/text-speech/text-to-speech.service';

@Component({
  selector: 'app-foto',
  standalone: true,
  imports: [
    HeaderComponent,
    MenuComponent,
    CommonModule,
    ModalRoupaComponent,
  ],
  templateUrl: './foto.component.html',
  styleUrl: './foto.component.scss'
})
export class FotoComponent implements OnDestroy{

  description: any;
  @ViewChild('videoElement') videoElement: ElementRef<HTMLVideoElement> | undefined;
  @ViewChild('canvasElement') canvasElement!: ElementRef;
  @ViewChild('fileInput') fileInput!: ElementRef;
  
  isCameraActive = false;  // Para controlar se a câmera está ativa
  photoBase64: string | null = null;
  errorMessage: string | null = null;
  loading: boolean = false;
  modal: boolean = false;
  
  constructor(
    private ApiService: ApiService,
    private ttsService: TextToSpeechService,
  ) {}

  startCamera (type: 'frontal' | 'traseira'): void {
    this.isCameraActive = true;
    this.errorMessage = null;

    // Encerra qualquer stream anterior
    if (this.videoElement?.nativeElement?.srcObject) {
      const oldStream = this.videoElement.nativeElement.srcObject as MediaStream;
      oldStream.getTracks().forEach(track => track.stop());
      this.videoElement.nativeElement.srcObject = null;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      this.errorMessage = 'Seu navegador não suporta acesso à câmera.';
      setTimeout(() => {
        this.errorMessage = '';
      }, 2000);
      return;
    }

    const constraints: MediaStreamConstraints = {
      video: { facingMode: type === 'traseira' ? 'environment' : 'user' }
    };

    navigator.mediaDevices.getUserMedia(constraints)
    .then(stream => {
      if (this.videoElement) {
      this.videoElement.nativeElement.srcObject = stream;
      this.videoElement.nativeElement.play().catch(() => {});
    }
    })
      .catch(async () => {
        this.errorMessage = 'Não foi possível acessar a câmera. ';
        setTimeout(() => {
          this.errorMessage = '';
        }, 2000);
      this.isCameraActive = false;
    });
  }

  // Método para parar a câmera
  stopCamera (): void {
    this.loading = false;
    this.errorMessage = null;
    if (this.videoElement && this.videoElement.nativeElement.srcObject) {
      const stream = this.videoElement.nativeElement.srcObject as MediaStream;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      this.videoElement.nativeElement.srcObject = null;
      this.isCameraActive = false;
    }
  }

  // Método para tirar uma foto e converter para base64
  takePhoto (): void {
    if (this.isCameraActive && this.videoElement && this.canvasElement) {
      this.loading = true;
      const video = this.videoElement.nativeElement as HTMLVideoElement;
      const canvas = this.canvasElement.nativeElement as HTMLCanvasElement;
      const context = canvas.getContext('2d');

      // Ajuste o tamanho do canvas para o tamanho do vídeo
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Desenhar o quadro atual do vídeo no canvas
      context?.drawImage(video, 0, 0, canvas.width, canvas.height);

      this.photoBase64 = canvas.toDataURL('image/jpeg', 0.9);

      video.pause();
      this.getDescription();
    }
  }

  // Abre a galeria ao clicar no botão
  openGallery (): void {
    this.fileInput.nativeElement.click();
  }

  onFileSelected (event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];

    if (file) {
      // Verifica se é imagem
      if (!file.type.startsWith('image/')) {
        alert('Selecione apenas arquivos de imagem.');
        return;
      }

      const reader = new FileReader();
      reader.onload = () => {
        this.photoBase64 = reader.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

  getDescription () {
    if (this.photoBase64) {
      this.loading = true;

      // Remove o prefixo "data:image/png;base64," ou similar
      const base64Content = this.photoBase64.replace(/^data:image\/\w+;base64,/, '');
 
      this.ApiService.postDescription(base64Content).subscribe({
        next: (res)=>{
          this.description = res;
          this.openModal();
          this.stopCamera();
        },
        error: ()=> {
          this.stopCamera();
        }
      })
    }
  }

  openModal () {
    this.modal = !this.modal;
  }

  onSpeak (text: string): void {
    this.ttsService.speak(text);
  }
  
  ngOnDestroy () {
    this.stopCamera();
  }

}
