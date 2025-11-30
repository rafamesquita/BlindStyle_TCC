import { Component, Input, Output, OnInit, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from './../../services/api.service';
import { CommonModule } from '@angular/common';
import { TextToSpeechService } from './../../services/text-speech/text-to-speech.service';

@Component({
  selector: 'app-modal-roupa',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './modal-roupa.component.html',
  styleUrl: './modal-roupa.component.scss'
})
export class ModalRoupaComponent implements OnInit {

  @Input() data: any;
  @Input() img: any;
  @Input() modal: boolean = true;
  @Output() close: EventEmitter<void> = new EventEmitter<void>();
  loading: Boolean = true;
  modalSugestao: boolean = false;
  suggestion: any;
  itemName: string = '';
  base64: any;
  showBtn: boolean = false;
  isEmpty: boolean = false;
  
  constructor(
    private activatedRoute: ActivatedRoute,
    private ApiService: ApiService,
    private ttsService: TextToSpeechService,
  ) {}

  ngOnInit (): void {
    const url = this.activatedRoute.snapshot.url.map(segmento => segmento.path).join('/')
    if (url.includes('foto')) {
      this.showBtn = true;
    }
    if (this.img) {
      this.base64 = this.img.replace(/^data:image\/\w+;base64,/, '');
      this.convertBase64ToJpg(this.img);
    }
    else {
      this.base64 = this.data.image_url.replace(/^data:image\/\w+;base64,/, '');
      this.convertBase64ToJpg(this.data.image_url);
    }
  }

  closeModal () {
    this.close.emit();
    this.modal = false;
  }

  convertBase64ToJpg (base64Data: string) {
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
    this.loading = false;
  }

  save () {
    this.loading = true;

    let body = {
      "name": this.itemName || 'Roupa',
      "description": this.data.description,
      "category": this.data.features.category,
      "item_type": this.data.features.item_type,
      "primary_color": this.data.features.primary_color,
      "usage": this.data.features.usage,
      "texture": this.data.features.texture,
      "print_category": this.data.features.print_category,
      "image_url": this.base64,
      "ownership": true
    }

    this.ApiService.postItems(body).subscribe({
      next: ()=>{
        this.loading = false;
      },
      error: ()=>{
        this.loading = false;
      }
    })
    this.closeModal();
  }

  postSuggestion (itemId: string) {
    this.loading = true;
    this.isEmpty = false;

    this.ApiService.postSuggestion(itemId).subscribe({
      next: (res)=>{
        this.suggestion = res;

        const isEmpty = Object.values(this.suggestion).every(v => v === null);
        if (isEmpty) this.isEmpty = true;
        else this.isEmpty = false;

        this.suggestion = Object.entries(this.suggestion)
        .filter(([_, value]) => value !== null)
        .map(([key, value]: [string, any], index) => ({ title: `Sugestão ${index + 1}`, ...value }));

        this.modalSugestao = true;
        this.loading = false;
      },
      error: ()=>{
        this.loading = false;
      }
    })
  }

  back () {
    this.modalSugestao = false;
  }
  
  onSpeak (text: string): void {
    this.ttsService.speak(text);
  }
}
