import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [],
  templateUrl: './footer.component.html',
  styleUrl: './footer.component.scss'
})
export class FooterComponent {

  openGit () {
    const url = 'https://github.com/ICEI-PUC-Minas-EC-TCC/pmg-ec-2025-2-tcc2-blindstyle';
    window.open(url, '_blank');
  }

}
