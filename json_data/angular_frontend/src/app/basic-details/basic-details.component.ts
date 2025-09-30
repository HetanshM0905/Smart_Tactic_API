import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-basic-details',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './basic-details.component.html',
  styleUrls: ['./basic-details.component.scss']
})
export class BasicDetailsComponent implements OnInit {
  form: FormGroup;
  currentStep = 1;
  totalSteps = 6;
  
  // Lookup options
  priorityOptions = [
    { value: 'p0', label: 'P0 - In budget' },
    { value: 'p1', label: 'P1 - Nice to have' }
  ];
  
  confidenceOptions = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' }
  ];

  ownerOptions = [
    { value: 'stevens@google.com', label: 'stevens@google.com' },
    { value: 'john.doe@google.com', label: 'john.doe@google.com' },
    { value: 'jane.smith@google.com', label: 'jane.smith@google.com' }
  ];

  constructor(private fb: FormBuilder, private router: Router) {
    this.form = this.fb.group({
      eventName: ['Google Event', Validators.required],
      description: ['A curated series of events for executives to engage in strategic discussions, share insights, and build partnerships with Google leaderships.', Validators.required],
      priority: ['p0', Validators.required],
      owner: ['stevens@google.com', Validators.required],
      startDate: ['2025-04-17', Validators.required],
      endDate: ['2025-07-17', Validators.required],
      eventDateConfidence: ['high', Validators.required],
      willGenerateLeads: [true, Validators.required],
      numberOfInquiries: [5, Validators.required]
    });
  }

  ngOnInit(): void {
    this.setupFormListeners();
  }

  private setupFormListeners(): void {
    this.form.get('willGenerateLeads')?.valueChanges.subscribe(value => {
      const numberOfInquiriesControl = this.form.get('numberOfInquiries');
      if (value) {
        numberOfInquiriesControl?.setValidators([Validators.required, Validators.min(1)]);
        numberOfInquiriesControl?.enable();
      } else {
        numberOfInquiriesControl?.clearValidators();
        numberOfInquiriesControl?.setValue(null);
        numberOfInquiriesControl?.disable();
      }
      numberOfInquiriesControl?.updateValueAndValidity();
    });
  }

  onBack(): void {
    console.log('Back clicked');
    // Navigate back to create tactic
    window.history.back();
  }

  onContinue(): void {
    if (this.form.valid) {
      console.log('Form submitted:', this.form.value);
      // Navigate to Event Categorisation
      this.router.navigate(['/event-categorisation']);
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
      if (field.errors['min']) {
        return `${this.getFieldLabel(fieldName)} must be at least ${field.errors['min'].min}`;
      }
    }
    return '';
  }

  private getFieldLabel(fieldName: string): string {
    const labels: { [key: string]: string } = {
      eventName: 'Event name',
      description: 'Description',
      priority: 'Priority',
      owner: 'Owner',
      startDate: 'Start date',
      endDate: 'End date',
      eventDateConfidence: 'Event date confidence',
      willGenerateLeads: 'Will generate leads',
      numberOfInquiries: 'Number of inquiries'
    };
    return labels[fieldName] || fieldName;
  }
}
