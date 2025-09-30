import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-execution-details',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './execution-details.component.html',
  styleUrls: ['./execution-details.component.scss']
})
export class ExecutionDetailsComponent implements OnInit {
  form: FormGroup;
  currentStep = 6;
  totalSteps = 6;
  currentSection = 1;
  totalSections = 6;
  
  // Global campaign options
  globalCampaignOptions = [
    { value: 'gcp_ai', label: 'GCP - AI: Win the AI era' },
    { value: 'gcp_data', label: 'GCP - Data: Future-proof your data' },
    { value: 'not_tied', label: 'Tactic is not tied to any Global Campaign Program (this is rare)' }
  ];

  // Partner involvement options
  partnerInvolvementOptions = [
    { value: 'partner_host', label: 'Partner Host' },
    { value: 'partner_involved', label: 'Partner Involved' },
    { value: 'no_partner_involvement', label: 'No Partner Involvement' }
  ];

  // Why no partner options
  whyNoPartnerOptions = [
    { value: 'no_qualified_partner', label: 'No qualified partner available' },
    { value: 'insufficient_bandwidth', label: 'Qualified partner has insufficient bandwidth' },
    { value: 'insufficient_time', label: 'Insufficient time to integrate for launch' },
    { value: 'not_relevant', label: 'Partner integration is not relevant' }
  ];
  
  constructor(private fb: FormBuilder, private router: Router) {
    this.form = this.fb.group({
      // Execution Details 1
      eventVenue: ['', Validators.required],
      registrationLink: ['', [Validators.required, Validators.pattern(/^https?:\/\/.+/)]],
      salesKitLink: ['', [Validators.required, Validators.pattern(/^https?:\/\/.+/)]],
      
      // Execution Details 2
      expectedRegistrations: ['', Validators.required],
      expectedAttendees: ['', Validators.required],
      globalCampaigns: [[], Validators.required],
      
      // Execution Details 3
      buyerSegment1: ['', Validators.required],
      buyerSegment2: ['', Validators.required],
      buyerSegment3: ['', Validators.required],
      buyerSegment4: ['', Validators.required],
      buyerSegment5: ['', Validators.required],
      allBuyerSegments: [''],
      
      // Execution Details 4
      coreMessaging1: ['', Validators.required],
      coreMessaging2: ['', Validators.required],
      allCoreMessaging: [''],
      partnerInvolvement: ['', Validators.required],
      whyNoPartner: [''],
      
      // Execution Details 5
      accountSegment1: ['', Validators.required],
      accountSegment2: ['', Validators.required],
      accountSegment3: ['', Validators.required],
      accountSegment4: ['', Validators.required],
      accountSegment5: ['', Validators.required],
      allAccountSegments: [''],
      
      // Execution Details 6
      existingCustomer: ['', Validators.required],
      greenfieldCustomer: ['', Validators.required],
      allCustomerLifecycle: ['']
    });
  }

  ngOnInit(): void {
    this.setupFormListeners();
  }

  private setupFormListeners(): void {
    // Partner involvement changes
    this.form.get('partnerInvolvement')?.valueChanges.subscribe(value => {
      if (value === 'no_partner_involvement') {
        this.form.get('whyNoPartner')?.setValidators([Validators.required]);
      } else {
        this.form.get('whyNoPartner')?.clearValidators();
      }
      this.form.get('whyNoPartner')?.updateValueAndValidity();
    });

    // Auto-calculate "All" fields
    this.setupAutoCalculation('buyerSegment1', 'buyerSegment2', 'buyerSegment3', 'buyerSegment4', 'buyerSegment5', 'allBuyerSegments');
    this.setupAutoCalculation('coreMessaging1', 'coreMessaging2', 'allCoreMessaging');
    this.setupAutoCalculation('accountSegment1', 'accountSegment2', 'accountSegment3', 'accountSegment4', 'accountSegment5', 'allAccountSegments');
    this.setupAutoCalculation('existingCustomer', 'greenfieldCustomer', 'allCustomerLifecycle');
  }

  private setupAutoCalculation(...fieldNames: string[]): void {
    const allField = fieldNames[fieldNames.length - 1];
    const inputFields = fieldNames.slice(0, -1);
    
    inputFields.forEach(fieldName => {
      this.form.get(fieldName)?.valueChanges.subscribe(() => {
        this.updateAllField(inputFields, allField);
      });
    });
  }

  private updateAllField(inputFields: string[], allField: string): void {
    const values = inputFields.map(fieldName => this.form.get(fieldName)?.value).filter(value => value);
    this.form.get(allField)?.setValue(values.join(', '));
  }

  onBack(): void {
    console.log('Back clicked');
    this.router.navigate(['/initiative-details']);
  }

  onGlobalCampaignChange(event: any): void {
    const checkbox = event.target;
    const currentValue = this.form.get('globalCampaigns')?.value || [];
    
    if (checkbox.checked) {
      currentValue.push(checkbox.value);
    } else {
      const index = currentValue.indexOf(checkbox.value);
      if (index > -1) {
        currentValue.splice(index, 1);
      }
    }
    
    this.form.get('globalCampaigns')?.setValue(currentValue);
  }

  onContinue(): void {
    if (this.form.valid) {
      console.log('Form submitted:', this.form.value);
      // Navigate to final step or completion
      alert('Execution Details submitted successfully! Form completed!');
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
      if (field.errors['pattern']) {
        return `${this.getFieldLabel(fieldName)} must be a valid URL (starting with http:// or https://)`;
      }
    }
    return '';
  }

  private getFieldLabel(fieldName: string): string {
    const labels: { [key: string]: string } = {
      // Execution Details 1
      eventVenue: 'Event Venue',
      registrationLink: 'Registration Link',
      salesKitLink: 'Sales Kit Link',
      
      // Execution Details 2
      expectedRegistrations: 'Expected no. of Registrations',
      expectedAttendees: 'Expected no. of attendees',
      globalCampaigns: 'Global campaign programs',
      
      // Execution Details 3
      buyerSegment1: 'Buyer Segment 1',
      buyerSegment2: 'Buyer Segment 2',
      buyerSegment3: 'Buyer Segment 3',
      buyerSegment4: 'Buyer Segment 4',
      buyerSegment5: 'Buyer Segment 5',
      allBuyerSegments: 'All',
      
      // Execution Details 4
      coreMessaging1: 'Core Messaging 1',
      coreMessaging2: 'Core Messaging 2',
      allCoreMessaging: 'All',
      partnerInvolvement: 'Level of partner involvement',
      whyNoPartner: 'Why is partner not involved',
      
      // Execution Details 5
      accountSegment1: 'Account Segment 1',
      accountSegment2: 'Account Segment 2',
      accountSegment3: 'Account Segment 3',
      accountSegment4: 'Account Segment 4',
      accountSegment5: 'Account Segment 5',
      allAccountSegments: 'All account segment alignment',
      
      // Execution Details 6
      existingCustomer: 'Existing',
      greenfieldCustomer: 'Greenfield',
      allCustomerLifecycle: 'All'
    };
    return labels[fieldName] || fieldName;
  }

  nextSection(): void {
    if (this.currentSection < this.totalSections) {
      this.currentSection++;
    }
  }

  previousSection(): void {
    if (this.currentSection > 1) {
      this.currentSection--;
    }
  }

  isSectionValid(section: number): boolean {
    switch (section) {
      case 1:
        return !!(this.form.get('eventVenue')?.valid && 
               this.form.get('registrationLink')?.valid && 
               this.form.get('salesKitLink')?.valid);
      case 2:
        return !!(this.form.get('expectedRegistrations')?.valid && 
               this.form.get('expectedAttendees')?.valid && 
               this.form.get('globalCampaigns')?.valid);
      case 3:
        return !!(this.form.get('buyerSegment1')?.valid && 
               this.form.get('buyerSegment2')?.valid && 
               this.form.get('buyerSegment3')?.valid && 
               this.form.get('buyerSegment4')?.valid && 
               this.form.get('buyerSegment5')?.valid);
      case 4:
        return !!(this.form.get('coreMessaging1')?.valid && 
               this.form.get('coreMessaging2')?.valid && 
               this.form.get('partnerInvolvement')?.valid);
      case 5:
        return !!(this.form.get('accountSegment1')?.valid && 
               this.form.get('accountSegment2')?.valid && 
               this.form.get('accountSegment3')?.valid && 
               this.form.get('accountSegment4')?.valid && 
               this.form.get('accountSegment5')?.valid);
      case 6:
        return !!(this.form.get('existingCustomer')?.valid && 
               this.form.get('greenfieldCustomer')?.valid);
      default:
        return false;
    }
  }
}
