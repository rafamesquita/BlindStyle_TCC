import { Component } from '@angular/core';
import { HeaderComponent } from "../../components/header/header.component";
import { MenuComponent } from "../../components/menu/menu.component";

@Component({
  selector: 'app-foto',
  standalone: true,
  imports: [HeaderComponent, MenuComponent],
  templateUrl: './foto.component.html',
  styleUrl: './foto.component.scss'
})
export class FotoComponent {

}
