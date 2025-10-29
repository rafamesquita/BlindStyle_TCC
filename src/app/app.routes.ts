import { Routes } from '@angular/router';
import { FotoComponent } from './pages/foto/foto.component';
import { LoginComponent } from './pages/login/login.component';
import { HistoricoComponent } from './pages/historico/historico.component';
import { CadastroComponent } from './pages/cadastro/cadastro.component';

export const routes: Routes = [
    { path: '', redirectTo: '/cadastro', pathMatch: 'full' },
    { path: 'foto', component: FotoComponent },
    { path: 'login', component: LoginComponent },
    { path: 'cadastro', component: CadastroComponent },
    { path: 'historico', component: HistoricoComponent },
];