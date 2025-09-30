import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { FormData, Page, LookupOption } from '../models/form-field.model';

@Injectable({
  providedIn: 'root'
})
export class FormDataService {
  private formData: FormData | null = null;

  constructor(private http: HttpClient) {}

  getFormData(): Observable<FormData> {
    if (this.formData) {
      return of(this.formData);
    }
    
    return this.http.get<FormData>('/assets/modified_layout.json');
  }

  getPage(pageId: number): Observable<Page | undefined> {
    return new Observable(observer => {
      this.getFormData().subscribe(data => {
        const page = data.pages.find(p => p.pageId === pageId);
        observer.next(page);
        observer.complete();
      });
    });
  }

  getLookupOptions(lookupKey: string): Observable<LookupOption[]> {
    return new Observable(observer => {
      this.getFormData().subscribe(data => {
        const options = data.lookups[lookupKey] || [];
        observer.next(options);
        observer.complete();
      });
    });
  }

  getTacticTypeOptionsByCategory(category: string): Observable<LookupOption[]> {
    const lookupKey = `tacticTypeOptionsByCategory${this.capitalizeFirst(category)}`;
    return this.getLookupOptions(lookupKey);
  }

  private capitalizeFirst(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
}
