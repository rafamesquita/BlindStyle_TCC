import { Component, Input, Output, OnInit, EventEmitter } from '@angular/core';
import { ApiService } from './../../services/api.service';
import { CommonModule } from '@angular/common';
import { TextToSpeechService } from './../../services/text-speech/text-to-speech.service';

@Component({
  selector: 'app-modal-roupa',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './modal-roupa.component.html',
  styleUrl: './modal-roupa.component.scss'
})
export class ModalRoupaComponent implements OnInit{
  @Input() data: any
  @Input() img: any
  @Input() modal: boolean = true
  @Output() close: EventEmitter<void> = new EventEmitter<void>();
  toggle: Boolean = false
  loading: Boolean = true
  suggestion: any
  base64: any
  
  constructor(private ApiService: ApiService, private ttsService: TextToSpeechService) {}

  clothe: any

  ngOnInit(): void {
    if (this.img) {
      this.base64 = this.img.replace(/^data:image\/\w+;base64,/, '');
      this.convertBase64ToJpg(this.img);
    }
    else {
      this.base64 = this.data.image_url.replace(/^data:image\/\w+;base64,/, '');
      this.getSpecificClothe();
      this.convertBase64ToJpg(this.data.image_url);
    }
  }

  closeModal() {
    this.close.emit();
    this.modal = false;
  }

  getSpecificClothe() {
    this.ApiService.getSpecificClothe(this.data.id).subscribe({
      next: (res)=>{
        this.clothe = res
        console.log(this.clothe)
        setTimeout(() => {
          this.loading = false 
        }, 2000);
        
      },
      error: (error)=>{
        console.error(error)
      }
    })
  }

  convertBase64ToJpg(base64Data: string) {
    // Remove o prefixo "data:image/png;base64," ou similar
    const base64Content = base64Data.replace(/^data:image\/\w+;base64,/, '');

    // Converte o conteúdo Base64 para um Blob
    const byteCharacters = atob(base64Content);
    const byteNumbers = new Array(byteCharacters.length).fill(null).map((_, i) => byteCharacters.charCodeAt(i));
    const byteArray = new Uint8Array(byteNumbers);

    const blob = new Blob([byteArray], { type: 'image/jpeg' });

    // Cria uma URL para o Blob
    if (this.img) {
      this.img = URL.createObjectURL(blob);
    }
    else {
    this.data.image_url = URL.createObjectURL(blob);
    }
    this.loading = false
  }

  save(){
    let name =  `${this.data.certain[0]}, ${this.data.certain[1]}`
    let description = this.data.description
    let imageUrl = this.base64
    this.ApiService.postItems(name, description, imageUrl).subscribe({
      next: (res)=>{
      },
      error: (error)=>{
        console.error(error)
      }
    })
    this.closeModal();
  }

  toggleSuggestion(){
    this.toggle = !this.toggle

    if (this.toggle = true) {
      this.getSuggestion(this.data.id)
    }
  }

  getSuggestion(itemId: string) {
    this.ApiService.getSuggestion(itemId).subscribe({
      next: (res)=>{
        this.suggestion = res
      },
      error: (error)=>{
        this.postSuggestion(itemId)
      }
    })
  }

  postSuggestion(itemId: string) {
    this.ApiService.postSuggestion(itemId).subscribe({
      next: (res)=>{
        this.getSuggestion(itemId)
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
