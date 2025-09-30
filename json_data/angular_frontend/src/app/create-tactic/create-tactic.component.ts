import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { FormDataService } from '../services/form-data.service';
import { FormField, Page, LookupOption } from '../models/form-field.model';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-create-tactic',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './create-tactic.component.html',
  styleUrls: ['./create-tactic.component.scss']
})
export class CreateTacticComponent implements OnInit {
  form: FormGroup;
  currentPage: Page | undefined;
  categoryOptions: LookupOption[] = [];
  tacticTypeOptions: LookupOption[] = [];
  eventTypeOptions: LookupOption[] = [];
  singleEventYesNoOptions: LookupOption[] = [];

  constructor(
    private fb: FormBuilder,
    private formDataService: FormDataService,
    private router: Router
  ) {
    this.form = this.fb.group({
      category: [null, Validators.required],
      tacticType: [null, Validators.required],
      eventType: [null, Validators.required],
      isAlignedToMultiEvent: [null, Validators.required]
    });
  }

  ngOnInit(): void {
    this.loadFormData();
    this.setupFormListeners();
  }

  private loadFormData(): void {
    // Set default page data
    this.currentPage = {
      workflowName: "Create Tactic",
      pageId: 1,
      pageLabel: "Create Tactic",
      pageSubLabel: "Tell us what youre planning, and well help you identify the tactic type. Be sure to select the right category to make sure your requests are being seen by the right people",
      layout: {},
      fields: []
    };

    // Set default options
    this.categoryOptions = [
      {
        value: "promote",
        label: "Promote: Tactics that get your message in front of customers and partners"
      },
      {
        value: "build_manage", 
        label: "Build & Manage: Tactics that create and manage the content, assets, and tools you use for promotion"
      },
      {
        value: "vendors",
        label: "Vendors: Tactics for vendors by Role Family and Role, as defined by Project Emporia"
      }
    ];

    this.eventTypeOptions = [
      {
        value: "single",
        title: "Single Event",
        description: "Create a new tactic for a standalone event."
      },
      {
        value: "multi",
        title: "Multi Event", 
        description: "Group several existing tactics under a single initiative."
      }
    ];

    this.singleEventYesNoOptions = [
      { value: "yes", label: "Yes" },
      { value: "no", label: "No" }
    ];
  }

  private setupFormListeners(): void {
    this.form.get('category')?.valueChanges.subscribe(category => {
      if (category) {
        // Set tactic type options based on category
        if (category === 'promote') {
          this.tacticTypeOptions = [
            { value: "partner_co_op", label: "Partner Co-op" },
            { value: "content_asset_promotion", label: "Content & Asset Promotion" },
            { value: "email_nurture", label: "Email Nurture" },
            { value: "direct_mail", label: "Direct Mail" },
            { value: "events_experiences", label: "Events & Experiences" },
            { value: "outbound_prospecting", label: "Outbound Prospecting" },
            { value: "brand_partnerships_sponsorships", label: "Brand Partnerships & Sponsorships" },
            { value: "partner_ppf_mdf", label: "Partner PPF/MDF" },
            { value: "referral_programs", label: "Referral Programs" }
          ];
        } else if (category === 'build_manage') {
          this.tacticTypeOptions = [
            { value: "analytics", label: "Analytics" },
            { value: "research", label: "Research" },
            { value: "contact_enrichment", label: "Contact Enrichment" },
            { value: "web_development", label: "Web Development" },
            { value: "free_trial_ti", label: "Free Trial TI (technical infra)" },
            { value: "marketing_technology", label: "Marketing Technology" },
            { value: "content_asset_development", label: "Content & Asset Development" },
            { value: "localization_translation", label: "Localization & Translation" },
            { value: "learning_development", label: "Learning & Development" },
            { value: "social_channel_management", label: "Social Channel Management" }
          ];
        } else if (category === 'vendors') {
          this.tacticTypeOptions = [
            { value: "data_analytics_insights", label: "Data, Analytics & Insights" },
            { value: "chief_of_staff", label: "Chief of Staff" },
            { value: "communications", label: "Communications" },
            { value: "creative", label: "Creative" },
            { value: "e_abp", label: "E/ABP" },
            { value: "event_management", label: "Event Management" },
            { value: "external_relationship_management", label: "External Relationship Management" },
            { value: "leadership", label: "Leadership" },
            { value: "marketing_activation", label: "Marketing Activation" },
            { value: "marketing_execution", label: "Marketing Execution" },
            { value: "production", label: "Production" }
          ];
        }
        this.form.get('tacticType')?.setValue(null);
      }
    });

    this.form.get('tacticType')?.valueChanges.subscribe(tacticType => {
      console.log('Tactic type changed:', tacticType);
    });

    this.form.get('eventType')?.valueChanges.subscribe(eventType => {
      console.log('Event type changed:', eventType);
    });
  }

  onSubmit(): void {
    if (this.form.valid) {
      console.log('Form submitted:', this.form.value);
    } else {
      console.log('Form is invalid');
    }
  }

  onBack(): void {
    console.log('Back clicked');
  }

  onContinue(): void {
    if (this.form.valid) {
      console.log('Form submitted:', this.form.value);
      // Navigate to basic details form
      this.router.navigate(['/basic-details']);
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
}
