import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-event-categorisation',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './event-categorisation.component.html',
  styleUrls: ['./event-categorisation.component.scss']
})
export class EventCategorisationComponent implements OnInit {
  form: FormGroup;
  currentStep = 2;
  totalSteps = 6;
  
  // Lookup options
  eventRingOptions = [
    { value: 'ring1', label: 'Ring 1: Global 1st Party' },
    { value: 'ring2', label: 'Ring 2: Global 3rd Party' },
    { value: 'ring3', label: 'Ring 3: Global 1st Party Series' },
    { value: 'ring4', label: 'Ring 4: Regional / Local' }
  ];

  firstPartyThirdPartyOptions = [
    { value: 'first_party', label: '1st party event' },
    { value: 'third_party', label: '3rd Party Event' }
  ];

  eventCategoryOptions = [
    { value: 'big_moment', label: 'Big Moment (Not Listed)' },
    { value: 'cyber_defense', label: 'Cyber Defense Summit' },
    { value: 'digital_ai', label: 'Digital AI moments' },
    { value: 'gcn', label: 'Google cloud next' },
    { value: 'google_exec', label: 'Google Executive events' },
    { value: 'google_io', label: 'Google I/O' },
    { value: 'public_sector_summit', label: 'Public Sector Summit' }
  ];

  eventSubCategoryOptions = [
    { value: 'gcn24', label: 'Google cloud next \'24' },
    { value: 'gcn25', label: 'Google cloud next \'25' },
    { value: 'gcn26', label: 'Google cloud next \'26' }
  ];

  fundingStatusOptions = [
    { value: 'fully_funded', label: 'Fully Funded' },
    { value: 'partially_funded', label: 'Partially Funded' },
    { value: 'not_funded', label: 'Not Funded' },
    { value: 'unsure', label: 'Unsure' }
  ];

  // Owner options
  ownerOptions = [
    { value: 'stevens@google.com', label: 'stevens@google.com' },
    { value: 'john.doe@google.com', label: 'john.doe@google.com' },
    { value: 'jane.smith@google.com', label: 'jane.smith@google.com' }
  ];

  constructor(private fb: FormBuilder, private router: Router) {
    this.form = this.fb.group({
      eventRing: [null, Validators.required],
      firstPartyOrThirdPartyEvent: [null, Validators.required],
      eventCategory: [null, Validators.required],
      eventCategoryOwner: [null, Validators.required],
      eventSubCategory: [null, Validators.required],
      eventSubCategoryOwner: [null, Validators.required],
      eventOrganiser: [null, Validators.required],
      eventPointOfContact: [null, Validators.required],
      fundingStatus: [null, Validators.required]
    });
  }

  ngOnInit(): void {
    this.setupFormListeners();
  }

  private setupFormListeners(): void {
    // Event Ring changes
    this.form.get('eventRing')?.valueChanges.subscribe(ring => {
      console.log('Event ring changed:', ring);
      // Reset dependent fields
      this.form.get('firstPartyOrThirdPartyEvent')?.setValue(null);
      this.form.get('eventCategory')?.setValue(null);
      this.form.get('eventSubCategory')?.setValue(null);
    });

    // First/Third Party changes
    this.form.get('firstPartyOrThirdPartyEvent')?.valueChanges.subscribe(partyType => {
      console.log('Party type changed:', partyType);
      // Reset dependent fields
      this.form.get('eventCategory')?.setValue(null);
      this.form.get('eventSubCategory')?.setValue(null);
    });

    // Event Category changes
    this.form.get('eventCategory')?.valueChanges.subscribe(category => {
      console.log('Event category changed:', category);
      // Reset subcategory
      this.form.get('eventSubCategory')?.setValue(null);
    });
  }

  onBack(): void {
    console.log('Back clicked');
    this.router.navigate(['/basic-details']);
  }

  onContinue(): void {
    if (this.form.valid) {
      console.log('Form submitted:', this.form.value);
      // Navigate to Location Details
      this.router.navigate(['/location-details']);
    } else {
      console.log('Form is invalid');
      console.log('Form errors:', this.getFormErrors());
      this.markFormGroupTouched();
    }
  }

  private getFormErrors(): any {
    const errors: any = {};
    Object.keys(this.form.controls).forEach(key => {
      const control = this.form.get(key);
      if (control?.errors) {
        errors[key] = control.errors;
      }
    });
    return errors;
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
      eventRing: 'Event Ring',
      firstPartyOrThirdPartyEvent: 'First party or third party event',
      eventCategory: 'Event Category',
      eventCategoryOwner: 'Event Category Owner',
      eventSubCategory: 'Event sub Category',
      eventSubCategoryOwner: 'Event sub Category Owner',
      eventOrganiser: 'Event Organiser',
      eventPointOfContact: 'Event Point of Contact',
      fundingStatus: 'Funding status'
    };
    return labels[fieldName] || fieldName;
  }
}
