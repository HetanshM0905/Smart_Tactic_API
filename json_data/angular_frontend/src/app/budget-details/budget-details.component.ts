import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-budget-details',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './budget-details.component.html',
  styleUrls: ['./budget-details.component.scss']
})
export class BudgetDetailsComponent implements OnInit {
  form: FormGroup;
  
  budgetLevel1Options = [
    { value: 'marketing', label: 'Marketing' },
    { value: 'sales', label: 'Sales' },
    { value: 'operations', label: 'Operations' }
  ];

  budgetLevel2Options = [
    { value: 'digital', label: 'Digital Marketing', parent: 'marketing' },
    { value: 'events', label: 'Events', parent: 'marketing' },
    { value: 'direct', label: 'Direct Sales', parent: 'sales' },
    { value: 'channel', label: 'Channel Sales', parent: 'sales' }
  ];

  budgetLevel3Options = [
    { value: 'online', label: 'Online Campaigns', parent: 'digital' },
    { value: 'social', label: 'Social Media', parent: 'digital' },
    { value: 'conferences', label: 'Conferences', parent: 'events' },
    { value: 'webinars', label: 'Webinars', parent: 'events' }
  ];

  budgetLevel4Options = [
    { value: 'google', label: 'Google Ads', parent: 'online' },
    { value: 'facebook', label: 'Facebook Ads', parent: 'online' },
    { value: 'linkedin', label: 'LinkedIn', parent: 'social' },
    { value: 'twitter', label: 'Twitter', parent: 'social' }
  ];

  constructor(
    private fb: FormBuilder,
    private router: Router
  ) {
    this.form = this.fb.group({
      level1: ['', Validators.required],
      level2: ['', Validators.required],
      level3: ['', Validators.required],
      level4: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    // Watch for changes in level1 to reset dependent fields
    this.form.get('level1')?.valueChanges.subscribe(() => {
      this.form.patchValue({ level2: '', level3: '', level4: '' });
    });

    // Watch for changes in level2 to reset dependent fields
    this.form.get('level2')?.valueChanges.subscribe(() => {
      this.form.patchValue({ level3: '', level4: '' });
    });

    // Watch for changes in level3 to reset dependent fields
    this.form.get('level3')?.valueChanges.subscribe(() => {
      this.form.patchValue({ level4: '' });
    });
  }

  get filteredLevel2Options() {
    const level1Value = this.form.get('level1')?.value;
    return this.budgetLevel2Options.filter(option => option.parent === level1Value);
  }

  get filteredLevel3Options() {
    const level2Value = this.form.get('level2')?.value;
    return this.budgetLevel3Options.filter(option => option.parent === level2Value);
  }

  get filteredLevel4Options() {
    const level3Value = this.form.get('level3')?.value;
    return this.budgetLevel4Options.filter(option => option.parent === level3Value);
  }

  getSelectedPath(): string {
    const level1 = this.form.get('level1')?.value;
    const level2 = this.form.get('level2')?.value;
    const level3 = this.form.get('level3')?.value;
    const level4 = this.form.get('level4')?.value;

    if (!level1) return '';

    let path = this.getOptionLabel(level1, this.budgetLevel1Options);
    
    if (level2) {
      path += ' > ' + this.getOptionLabel(level2, this.budgetLevel2Options);
    }
    if (level3) {
      path += ' > ' + this.getOptionLabel(level3, this.budgetLevel3Options);
    }
    if (level4) {
      path += ' > ' + this.getOptionLabel(level4, this.budgetLevel4Options);
    }

    return path;
  }

  private getOptionLabel(value: string, options: any[]): string {
    const option = options.find(opt => opt.value === value);
    return option ? option.label : value;
  }

  getFieldError(fieldName: string): string {
    const field = this.form.get(fieldName);
    if (field?.errors && field.touched) {
      if (field.errors['required']) {
        return `${this.getFieldLabel(fieldName)} is required`;
      }
    }
    return '';
  }

  private getFieldLabel(fieldName: string): string {
    const labels: { [key: string]: string } = {
      'level1': 'Level 1',
      'level2': 'Level 2',
      'level3': 'Level 3',
      'level4': 'Level 4'
    };
    return labels[fieldName] || fieldName;
  }

  onBack(): void {
    this.router.navigate(['/location-details']);
  }

  onContinue(): void {
    if (this.form.valid) {
      // Save form data and navigate to next step
      console.log('Budget details:', this.form.value);
      this.router.navigate(['/initiative-details']);
    } else {
      // Mark all fields as touched to show validation errors
      Object.keys(this.form.controls).forEach(key => {
        this.form.get(key)?.markAsTouched();
      });
    }
  }
}
