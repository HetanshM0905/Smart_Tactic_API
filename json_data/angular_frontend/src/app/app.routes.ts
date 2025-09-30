import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: '/create-tactic', pathMatch: 'full' },
  { path: 'create-tactic', loadComponent: () => import('./create-tactic/create-tactic.component').then(m => m.CreateTacticComponent) },
  { path: 'basic-details', loadComponent: () => import('./basic-details/basic-details.component').then(m => m.BasicDetailsComponent) },
  { path: 'event-categorisation', loadComponent: () => import('./event-categorisation/event-categorisation.component').then(m => m.EventCategorisationComponent) },
  { path: 'location-details', loadComponent: () => import('./location-details/location-details.component').then(m => m.LocationDetailsComponent) },
  { path: 'budget-details', loadComponent: () => import('./budget-details/budget-details.component').then(m => m.BudgetDetailsComponent) },
  { path: 'initiative-details', loadComponent: () => import('./initiative-details/initiative-details.component').then(m => m.InitiativeDetailsComponent) },
  { path: 'execution-details', loadComponent: () => import('./execution-details/execution-details.component').then(m => m.ExecutionDetailsComponent) }
];
