import { CommonModule } from '@angular/common';
import { ApiService } from './../../services/api.service';
import { Component, OnInit } from '@angular/core';
import { HeaderComponent } from '../../components/header/header.component';
import { RoupaHistComponent } from '../../components/roupa-hist/roupa-hist.component';
import { MenuComponent } from "../../components/menu/menu.component";

@Component({
  selector: 'app-historico',
  standalone: true,
  imports: [
    HeaderComponent,
    RoupaHistComponent,
    CommonModule,
    MenuComponent,
  ],
  templateUrl: './historico.component.html',
  styleUrl: './historico.component.scss'
})

export class HistoricoComponent implements OnInit {

  clothes: any;
  loading: boolean = true;

  constructor(
    private ApiService: ApiService,
  ) {}

  ngOnInit (): void {
   this.getClothes();
  }

  getClothes () {
    this.ApiService.getClothes().subscribe({
      next: (res: any)=>{
        this.clothes = res.items;
        this.loading = false;
      },
      error: ()=>{
        this.loading = false;
      }
    })
  }
}
