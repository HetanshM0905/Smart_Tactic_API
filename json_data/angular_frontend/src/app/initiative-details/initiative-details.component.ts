import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-initiative-details',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './initiative-details.component.html',
  styleUrls: ['./initiative-details.component.scss']
})
export class InitiativeDetailsComponent implements OnInit {
  form: FormGroup;
  currentStep = 5;
  totalSteps = 6;
  
  // Initiative options from the JSON
  initiativeOptions = [
    { value: 'enterprise_incl_select', label: 'Enterprise (incl. Select)' },
    { value: 'corporate', label: 'Corporate' },
    { value: 'smb', label: 'SMB' },
    { value: 'startups_p1a', label: 'Startups (P1A)' },
    { value: 'sdr', label: 'SDR' },
    { value: 'direct_touched', label: 'Direct Touched - $sum(enterprise_incl_select,corporate,smb,startups_p1a,sdr)' },
    { value: 'ppf_mdf', label: 'PPF/MDF' },
    { value: 'isv', label: 'ISV' },
    { value: 'others_gsi_affiliates', label: 'Others (GSI, affiliates, etc.)' },
    { value: 'partner_after_direct_touched', label: 'Partner - $sum(ppf_mdf,isv,others_gsi_affiliates)' },
    { value: 'named', label: 'Named' },
    { value: 'smb_after_partner', label: 'SMB' },
    { value: 'startups_p1a_after_partner', label: 'Startups (P1A)' },
    { value: 'self_serve_after_partner', label: 'Self-Serve - $sum(named,smb_after_partner,startups_p1a_after_partner)' },
    { value: 'gcp', label: 'GCP - $sum(direct_touched,partner_after_direct_touched,self_serve_after_partner)' },
    { value: 'enterprise_incl_select_after_gcp', label: 'Enterprise (incl. Select)' },
    { value: 'corporate_after_gcp', label: 'Corporate' },
    { value: 'smb_after_gcp', label: 'SMB' },
    { value: 'sdr_after_gcp', label: 'SDR' },
    { value: 'sales_assisted', label: 'Sales-Assisted - $sum(enterprise_incl_select_after_gcp,corporate_after_gcp,smb_after_gcp,sdr_after_gcp)' },
    { value: 'ppf_mdf_after_sales_assisted', label: 'PPF/MDF' },
    { value: 'isv_after_sales_assisted', label: 'ISV' },
    { value: 'others_gsi_affiliates_after_sales_assisted', label: 'Others (GSI, affiliates, etc.)' },
    { value: 'partner_after_sales_assisted', label: 'Partner - $sum(ppf_mdf_after_sales_assisted,isv_after_sales_assisted,others_gsi_affiliates_after_sales_assisted)' },
    { value: 'named_after_partner', label: 'Named' },
    { value: 'smb_after_partner_sales_assisted', label: 'SMB' },
    { value: 'self_serve_after_partner_sales_assisted', label: 'Self-Serve - $sum(named_after_partner,smb_after_partner_sales_assisted,self_serve_after_partner_sales_assisted)' },
    { value: 'gws', label: 'GWS - $sum(sales_assisted,partner_after_sales_assisted,self_serve_after_partner_sales_assisted)' },
    { value: 'global_partner_programs', label: 'Global Partner Programs' },
    { value: 'demand_gen_global_campaign_build', label: 'Demand Gen Global Campaign Build' },
    { value: 'next', label: 'NEXT' },
    { value: 'summits', label: 'Summits' },
    { value: 'events_global_build', label: 'Events Global Build' },
    { value: 'global_events', label: 'Global Events - $sum(global_partner_programs,demand_gen_global_campaign_build,next,summits,events_global_build)' },
    { value: 'security_demand_generation', label: 'Security Demand Generation' },
    { value: 'security_product_marketing', label: 'Security Product Marketing' },
    { value: 'security', label: 'Security - $sum(security_demand_generation,security_product_marketing,security)' },
    { value: 'developer_advocacy', label: 'Developer Advocacy' },
    { value: 'gcp_ai_perception', label: 'GCP AI Perception' },
    { value: 'gws_ai_consideration', label: 'GWS AI Consideration' },
    { value: 'brand_global_build', label: 'Brand Global Build' },
    { value: 'developer_perception', label: 'Developer Perception' },
    { value: 'regional_brand_campaign', label: 'Regional Brand Campaign' },
    { value: 'global_brand_campaigns', label: 'Global Brand Campaigns - $sum(developer_advocacy,gcp_ai_perception,gws_ai_consideration,brand_global_build,developer_perception,regional_brand_campaign)' },
    { value: 'brand_partnerships', label: 'Brand Partnerships' },
    { value: 'gws_product_marketing', label: 'GWS Product Marketing' },
    { value: 'gcp_product_marketing', label: 'GCP Product Marketing' },
    { value: 'gcp_analyst_relations', label: 'GCP Analyst Relations' },
    { value: 'customer_reference', label: 'Customer Reference' },
    { value: 'mindshare_thought_leadership', label: 'Mindshare / Thought Leadership - $sum(brand_partnerships,gws_product_marketing,gcp_product_marketing,gcp_analyst_relations,customer_reference)' },
    { value: 'activation', label: 'Activation' },
    { value: 'demand_ops', label: 'Demand Ops' },
    { value: 'ai_optimization', label: 'AI Optimization' },
    { value: 'systems_data', label: 'Systems & Data' },
    { value: 'strategy_planning_ops', label: 'Strategy, Planning & Ops' },
    { value: 'marketer_enablement', label: 'Marketer Enablement - $sum(activation,demand_ops,ai_optimization,systems_data,strategy_planning_ops)' },
    { value: 'one_google', label: 'One Google' },
    { value: 'gcm_reserve_acquire_revenue', label: 'GCM Reserve - Acquire Revenue' },
    { value: 'gcm_reserve_improve_efficiency', label: 'GCM Reserve - Improve Efficiency' },
    { value: 'gcm_reserve_lift_mindshare', label: 'GCM Reserve - Lift Mindshare' },
    { value: 'gcm_reserve_source_demand', label: 'GCM Reserve - Source Demand' },
    { value: 'gcm_reserve', label: 'GCM Reserve - $sum(one_google,gcm_reserve_acquire_revenue,gcm_reserve_improve_efficiency,gcm_reserve_lift_mindshare,gcm_reserve_source_demand)' },
    { value: 'dei_culture', label: 'DEI & Culture' }
  ];

  constructor(private fb: FormBuilder, private router: Router) {
    this.form = this.fb.group({
      initiativeDetails: [null, Validators.required]
    });
  }

  ngOnInit(): void {
    // No special setup needed for this simple form
  }

  onBack(): void {
    console.log('Back clicked');
    this.router.navigate(['/budget-details']);
  }

  onContinue(): void {
    if (this.form.valid) {
      console.log('Form submitted:', this.form.value);
      // Navigate to Execution Details
      this.router.navigate(['/execution-details']);
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
      initiativeDetails: 'All Initiatives'
    };
    return labels[fieldName] || fieldName;
  }
}
