export interface FormField {
  id: string;
  fieldLabel: string;
  fieldTitle: string;
  fieldSubtitle: string;
  type: string;
  optionsLookup?: string;
  value: any;
  isVisible: boolean;
  readOnly?: boolean;
  style?: any;
  validators?: Validator[];
  ui?: {
    className?: string;
  };
  dependsOn?: string;
  min?: number;
  guidanceText?: string;
}

export interface Validator {
  required?: boolean;
  min?: string;
  max?: string;
  pattern?: string;
  message?: string;
}

export interface Page {
  workflowName: string;
  pageId: number;
  pageLabel: string;
  pageSubLabel: string;
  layout: any;
  fields: FormField[];
}

export interface LookupOption {
  value: string;
  label?: string;
  title?: string;
  description?: string;
  optionsLookup?: string;
  pageId?: number;
}

export interface FormData {
  pages: Page[];
  lookups: { [key: string]: LookupOption[] };
  rules: any[];
}
