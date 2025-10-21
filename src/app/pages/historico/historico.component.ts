import { CommonModule } from '@angular/common';
import { ApiService } from './../../services/api.service';
import { Component, OnInit } from '@angular/core';
import { HeaderComponent } from '../../components/header/header.component';
import { RoupaHistComponent } from '../../components/roupa-hist/roupa-hist.component';

@Component({
  selector: 'app-historico',
  standalone: true,
  imports: [HeaderComponent, RoupaHistComponent, CommonModule],
  templateUrl: './historico.component.html',
  styleUrl: './historico.component.scss'
})

export class HistoricoComponent implements OnInit {

  clothes: any
  loading: Boolean = true

  constructor(private ApiService: ApiService) {}

  ngOnInit(): void {
   this.getClothes()
  }

  getClothes() {
    this.ApiService.getClothes().subscribe({
      next: (res)=>{
        this.clothes = res
        this.loading = false
      },
      error: (error)=>{
        console.error(error)
        this.loading = false
      }
    })
  }
}
