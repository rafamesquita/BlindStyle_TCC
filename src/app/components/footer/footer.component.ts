import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [],
  templateUrl: './footer.component.html',
  styleUrl: './footer.component.scss'
})
export class FooterComponent {

  openGit() {
    const url = 'https://github.com/rafamesquita/BlindStyle';
    window.open(url, '_blank');
  }

}
