import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-location-details',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './location-details.component.html',
  styleUrls: ['./location-details.component.scss']
})
export class LocationDetailsComponent implements OnInit {
  form: FormGroup;
  currentStep = 3;
  totalSteps = 6;
  
  // Lookup options
  hostingTypeOptions = [
    { value: 'digital', label: 'Digital Event' },
    { value: 'physical', label: 'Physical Event' },
    { value: 'hybrid', label: 'Hybrid Event' }
  ];

  businessRegionOptions = [
    { value: 'north_america', label: 'North America' },
    { value: 'europe', label: 'Europe' },
    { value: 'asia_pacific', label: 'Asia Pacific' },
    { value: 'latin_america', label: 'Latin America' },
    { value: 'middle_east_africa', label: 'Middle East & Africa' }
  ];

  countryOptions = [
    { value: 'usa', label: 'United States' },
    { value: 'canada', label: 'Canada' },
    { value: 'uk', label: 'United Kingdom' },
    { value: 'germany', label: 'Germany' },
    { value: 'france', label: 'France' },
    { value: 'japan', label: 'Japan' },
    { value: 'australia', label: 'Australia' },
    { value: 'india', label: 'India' },
    { value: 'singapore', label: 'Singapore' },
    { value: 'brazil', label: 'Brazil' },
    { value: 'mexico', label: 'Mexico' }
  ];

  constructor(private fb: FormBuilder, private router: Router) {
    this.form = this.fb.group({
      howIsEventHosted: [null, Validators.required],
      businessRegion: [null, Validators.required],
      country: [null, Validators.required]
    });
  }

  ngOnInit(): void {
    this.setupFormListeners();
  }

  private setupFormListeners(): void {
    // Hosting type changes
    this.form.get('howIsEventHosted')?.valueChanges.subscribe(hostingType => {
      console.log('Hosting type changed:', hostingType);
      // Reset dependent fields if needed
      if (hostingType === 'digital') {
        // For digital events, country might not be required
        this.form.get('country')?.clearValidators();
        this.form.get('country')?.updateValueAndValidity();
      } else {
        // For physical/hybrid events, country is required
        this.form.get('country')?.setValidators([Validators.required]);
        this.form.get('country')?.updateValueAndValidity();
      }
    });
  }

  onBack(): void {
    console.log('Back clicked');
    this.router.navigate(['/event-categorisation']);
  }

  onContinue(): void {
    if (this.form.valid) {
      console.log('Form submitted:', this.form.value);
      // Navigate to Budget Details
      this.router.navigate(['/budget-details']);
    } else {
      console.log('Form is invalid');
      this.markFormGroupTouched();
    }
  }

  private markFormGroupTouched(): void {
    Object.keys(this.form.controls).forEach(key => {
      const control = this.form.get(key);
      control?.markAsTouched();
    });
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
      howIsEventHosted: 'How is the event hosted?',
      businessRegion: 'Business Region',
      country: 'Country'
    };
    return labels[fieldName] || fieldName;
  }
}
