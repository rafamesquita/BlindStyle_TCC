import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {

  @Input() title: string = ''

  constructor(private router: Router) {}

  login(){
    this.router.navigate(['/login']);
  }

  back(){
    this.router.navigate(['/home']);
  }

}
