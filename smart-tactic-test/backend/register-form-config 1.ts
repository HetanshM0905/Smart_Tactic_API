import { StepConfig } from '../interfaces/form.interface';

export const registerFormConfig1: StepConfig = {
  form_mapping: {
    f1: 'basicInfo_eventName',
    f2: 'basicInfo_eventDescription',
    f3: 'basicInfo_priorityOwner_priority',
    f4: 'basicInfo_priorityOwner_owner',
    f5: 'basicInfo_eventDates_eventStartDate',
    f6: 'basicInfo_eventDates_eventEndDate',
    f7: 'basicInfo_eventDateCon&expPer_EventDateConfidence',
    f8: 'basicInfo_eventDateCon&expPer_leads',
    f9: 'basicInfo_eventDetail_eventRing',
    f10: 'basicInfo_eventDetail_eventParty',
    f11: 'basicInfo_eventDetail_eventCategory',
    f12: 'basicInfo_eventDetail_eventCategoryOwner',
    f13: 'basicInfo_eventDetail_eventSubCategory',
    f14: 'basicInfo_eventDetail_eventSubCategoryOwner',
  },
  sections: [
    {
      label: 'Basic Info',
      layout: {
        // type: 'flex', //grid/flex
        // columns: 2,
        // gap: '16px',
        type: 'flex',
        gap: '16px',
        flexWrap: 'wrap',
        flexDirection: 'column',
        //
      },
      fields: [
        {
          id: 'f1',
          name: 'eventName',
          fieldlabel: 'Event name*',
          fieldTitle: '',
          fieldSubTitle: '',
          placeholder: '',
          type: 'text',
          //validators: ['required'],
          class: '',
          layout: {
            //margin_bottom: '0px',
          },
        },
        {
          id: 'f2',
          name: 'eventDescription',
          fieldlabel: 'Event description',
          fieldTitle: 'Event description',
          fieldSubTitle:
            'Provide a brief overview of the event’s purpose, goals, and any relevant context',
          placeholder: 'Enter event description',
          type: 'textarea',
          //validators: ['required'],
          class: '',
          rows: 3,
          layout: {
            margin_bottom: '0px',
          },
          //layout: { colSpan: 1 },
        },
        {
          id: '',
          name: 'priorityOwner',
          layout: {
            type: 'flex',
            display: 'flex',
            gap: '16px',
            flexDirection: 'row',
            justifyContent: 'flex-start',
          },
          subFields: [
            {
              id: 'f3',
              name: 'priority',
              fieldlabel: 'Priority',
              fieldTitle: 'Priority',
              fieldSubTitle:
                'Select priority based on importance and budget impact',
              type: 'select',
              placeholder: 'Select priority',
              options: [
                { key: '1', value: 'High' },
                { key: '2', value: 'Medium' },
                { key: '3', value: 'Low' },
              ],
              //validators: ['required'],
              layout: {
                flex: '1',
                margin_bottom: '0px',
              },
            },
            {
              id: 'f4',
              name: 'owner',
              fieldlabel: 'Owner',
              fieldTitle: 'Owner',
              fieldSubTitle: 'Select the tactic’s responsible person',
              type: 'select',
              placeholder: 'Select owner',
              options: [
                { key: '1', value: 'a@gmail.com' },
                { key: '2', value: 'b@gmail.com' },
                { key: '3', value: 'c@gmail.com' },
              ],
              //validators: ['required'],
              layout: {
                flex: '1',
              },
            },
          ],
        },
        {
          id: '',
          name: 'eventDates',
          label: 'Let’s more about your event',
          layout: {
            type: 'flex',
            display: 'flex',
            gap: '16px',
            flexDirection: 'row',
            justifyContent: 'flex-start',
          },
          subFields: [
            {
              id: 'f5',
              name: 'eventStartDate',
              fieldTitle: '',
              fieldSubTitle: '',
              fieldlabel: 'Event start date',
              placeholder: 'Select start event date',
              type: 'date',
              //validators: ['required'],
              minDate: '2025-01-01',
              maxDate: '2025-12-31',
              startView: 'multi-year',
              touchUi: true,
              layout: {
                flex: '1',
                marginRight: '10px',
              },
            },
            {
              id: 'f6',
              name: 'eventEndDate',
              fieldTitle: '',
              fieldSubTitle: '',
              fieldlabel: 'Event end date',
              placeholder: 'Select end event date',
              type: 'date',
              //validators: ['required'],
              minDate: '2025-01-01',
              maxDate: '2025-12-31',
              startView: 'multi-year',
              touchUi: true,
              layout: {
                flex: '1',
                //marginRight: '10px',
              },
            },
          ],
        },
        {
          id: '',
          name: 'eventDateCon&expPer',
          layout: {
            type: 'flex',
            display: 'flex',
            gap: '16px',
            flexDirection: 'row',
            justifyContent: 'flex-start',
          },
          subFields: [
            {
              id: 'f7',
              name: 'EventDateConfidence',
              fieldlabel: 'Event date confidence*',
              fieldTitle:
                'Choose how confident you are about the provided dates',
              fieldSubTitle: '',
              type: 'select',
              placeholder: 'Select event date confidence',
              options: [
                { key: '1', value: 'High' },
                { key: '2', value: 'Medium' },
                { key: '3', value: 'Low' },
              ],
              //validators: ['required'],
              layout: {
                flex: '1',
                margin_bottom: '5px',
              },
            },
            {
              id: 'f8',
              name: 'expectedPerformance',
              fieldlabel: 'Will this tactic generate customer inquiries ?*',
              fieldTitle: 'Expected performance',
              fieldSubTitle: '',
              type: 'select',
              placeholder: 'Select expected performance',
              options: [
                { key: '1', value: 'Yes' },
                { key: '2', value: 'No' },
              ],
              //validators: ['required'],
              layout: {
                flex: '1',
                margin_bottom: '5px',
              },
            },
          ],
        },
        {
          id: '',
          label: 'Event categorization',
          subLabel:
            'Classify your tactic event by selecting the appropriate ring, type, category, and owner. These details help organize events for reporting, tracking, and team ownership.',
          type: 'grid',
          layout: {
            type: 'grid',
            columns: 1, // ✅ two columns
            gap: '16px',
          },
          gridFields: [
            // Row 1
            {
              id: 'f9',
              name: 'eventRing',
              fieldlabel: 'Event ring*',
              type: 'select',
              placeholder: 'Select owner',
              options: [
                { key: 'r1', value: 'Ring 1: Global 1st Party' },
                { key: 'r2', value: 'Ring 2: Global 3rd Party' },
                { key: 'r3', value: 'Ring 3: Global 1st Party Series' },
                { key: 'r4', value: 'Ring 4: Regional / Local' },
              ],
              layout: { gridColumn: '1', gridRow: '1' },
            },
            {
              id: 'f10',
              name: 'eventOwner',
              fieldlabel: 'Is the event 1st party or the 3rd party ?*',
              type: 'select',
              placeholder: 'Select owner',
              options: [], // will be filled later
              // disabled: true, // initially disabled
              dependsOn: 'f9', // 👈 dependent on "country"
              optionsMap: {
                r1: [{ key: 'p1', value: '1st party event' }],
                r2: [{ key: 'p2', value: '3rd Party Event' }],
                r3: [{ key: 'p3', value: 'Party C' }],
                r4: [{ key: 'p4', value: 'Party C' }],
                // Ring3: { api: '/api/parties?ring=Ring2' },
              },
              layout: { gridColumn: '2', gridRow: '1' },
            },

            // Row 2
            {
              id: 'f11',
              name: 'eventCategory',
              fieldlabel: 'Event category*',
              type: 'select',
              placeholder: 'Select owner',
              options: [],
              layout: { gridColumn: '1', gridRow: '2' },
              dependsOn: 'f9.f10',
              optionsMap: {
                'R1.P1': [{ key: 'C1', value: 'Category A' }],
                'R1.P2': [{ key: 'C2', value: 'Category B' }],
                'R2.P3': [{ key: 'C3', value: 'Category C' }],
              },
            },
            {
              id: 'f12',
              name: 'eventCategoryOwner',
              fieldlabel: 'Event category owner*',
              type: 'select',
              placeholder: 'Select owner',
              options: [],
              layout: { gridColumn: '2', gridRow: '2' },
              dependsOn: 'f9.f10.f11',
              optionsMap: {
                'R1.P1.C1': [{ key: 'CO1', value: 'Category owner A' }],
                'R1.P2.C2': [{ key: 'CO2', value: 'Category owner B' }],
                'R2.P3.C3': [{ key: 'CO3', value: 'Category owner C' }],
              },
            },

            // Row 3
            {
              id: 'f13',
              name: 'eventSubCategory',
              fieldlabel: 'Event sub category*',
              type: 'select',
              placeholder: 'Select owner',
              options: [
                { key: '1', value: 'a@gmail.com' },
                { key: '2', value: 'b@gmail.com' },
                { key: '3', value: 'c@gmail.com' },
              ],
              layout: { gridColumn: '1', gridRow: '3' },
            },
            {
              id: 'f14',
              name: 'eventSubCategoryOwner',
              fieldlabel: 'Event sub category owner*',
              type: 'select',
              placeholder: 'Select owner',
              options: [
                { key: '1', value: 'a@gmail.com' },
                { key: '2', value: 'b@gmail.com' },
                { key: '3', value: 'c@gmail.com' },
              ],
              layout: { gridColumn: '2', gridRow: '3' },
            },

            // Row 4
            {
              id: 'f15',
              name: 'eventOrganizer',
              fieldlabel: 'Event organizer*',
              type: 'select',
              placeholder: 'Select owner',
              options: [
                { key: '1', value: 'a@gmail.com' },
                { key: '2', value: 'b@gmail.com' },
                { key: '3', value: 'c@gmail.com' },
              ],
              layout: { gridColumn: '1', gridRow: '4' },
            },
            {
              id: 'f16',
              name: 'eventPointOfContact',
              fieldlabel: 'Event point of contact*',
              type: 'select',
              placeholder: 'Select owner',
              options: [
                { key: '1', value: 'a@gmail.com' },
                { key: '2', value: 'b@gmail.com' },
                { key: '3', value: 'c@gmail.com' },
              ],
              layout: { gridColumn: '2', gridRow: '4' },
            },

            // Row 5 → full width
            {
              id: 'f17',
              name: 'eventFundingStatus',
              fieldlabel: 'Funding status',
              type: 'select',
              placeholder: 'Select owner',
              options: [
                { key: '1', value: 'a@gmail.com' },
                { key: '2', value: 'b@gmail.com' },
                { key: '3', value: 'c@gmail.com' },
              ],
              layout: { gridColumn: '1 / span 2', gridRow: '5' },
            },
          ],
        },
        {
          id: 'f18',
          name: 'eventHost',
          fieldlabel: 'How is the event being hosted ?*',
          fieldTitle: 'Location details',
          fieldSubTitle:
            'Specify how the event will be conducted to help align planning, logistics, and audience engagement strategies',
          placeholder: 'Enter event description',
          type: 'select',
          options: [
            { key: '1', value: 'a@gmail.com' },
            { key: '2', value: 'b@gmail.com' },
            { key: '3', value: 'c@gmail.com' },
          ],
          //validators: ['required'],
          class: '',
          rows: 3,
          layout: {
            margin_bottom: '0px',
          },
          //layout: { colSpan: 1 },
        },
        {
          id: '',
          layout: {
            type: 'flex',
            display: 'flex',
            gap: '16px',
            flexDirection: 'row',
            justifyContent: 'flex-start',
          },
          subFields: [
            {
              id: 'f19',
              name: 'region',
              fieldlabel: 'Select region*',
              fieldTitle: '',
              fieldSubTitle: '',
              type: 'select',
              placeholder: 'Select region*',
              options: [
                { key: '1', value: 'High' },
                { key: '2', value: 'Medium' },
                { key: '3', value: 'Low' },
              ],
              //validators: ['required'],
              layout: {
                flex: '1',
                margin_bottom: '0px',
              },
            },
            {
              id: 'f20',
              name: 'country',
              fieldlabel: 'Select country*',
              type: 'multiselect',
              //required: true,
              options: [
                { key: 'CA', value: 'Canada' },
                { key: 'US', value: 'United States' },
                { key: 'MX', value: 'Mexico' },
                { key: 'PR', value: 'Puerto Rico' },
              ],
              layout: {
                flex: '2',
                margin_bottom: '0px',
              },
            },
          ],
        },
      ],
    },
    {
      label: 'Budget',
      subLabel:
        'A Cloud Marketing Cost Center must be used as the main cost center for the tactic. Additional cost centers, including non-GCM cost centers can be added by selecting ‘Split cost’ below.',
      layout: {
        type: 'flex',
        gap: '16px',
        flexWrap: 'wrap',
        flexDirection: 'column',
      },
      fields: [
        {
          id: '21',
          name: 'CloudMarketingCostCenter',
          fieldlabel: 'Cloud Marketing Cost Center*',
          fieldTitle: '',
          fieldSubTitle: '',
          type: 'select',
          options: [
            { key: '1', value: 'High' },
            { key: '2', value: 'Medium' },
            { key: '3', value: 'Low' },
          ],
          //validators: ['required'],
        },
        {
          id: 'f22',
          name: 'DoesThisTacticHaveSpend',
          fieldlabel: 'Does this tactic have spend ?*',
          fieldTitle: '',
          fieldSubTitle: '',
          type: 'select',
          options: [
            { key: 'y', value: 'Yes' },
            { key: 'n', value: 'No' },
          ],
          //validators: ['required'],
        },
        {
          id: 'f23',
          name: 'SplitCostCheckBox',
          fieldlabel:
            'Select if you’re sharing the budget of this tactic with another cost center. If selected, new rows will appear above and you must add the cost split.',
          fieldTitle: '',
          fieldSubTitle: 'Split cost (optional)',
          type: 'singlecheckbox',
          //validators: ['required'],
        },
        {
          id: 'f24',
          name: 'Owner',
          fieldlabel: 'Does this tactic have spend ?*',
          fieldTitle: 'Who are you sharing this tactic with ?*',
          fieldSubTitle:
            'If your tactic cost is shared with order cost center(s) . You will need to provide the ldap of the tactic POC. This tactic will appear on all applicable Team Plans.',
          type: 'select',
          options: [
            { key: 'email1', value: 'email@gmail.com' },
            { key: 'email2', value: 'email@gmail.com' },
          ],
          //validators: ['required'],
        },
      ],
    },
    {
      label: 'Initiative details',
      fields: [
        {
          id: 'f22',
          name: 'eventName',
          fieldlabel: 'Event Name',
          type: 'text',
          placeholder: 'Enter event name',
          //validators: ['required'],
        },
        {
          id: 'f23',
          name: 'eventDate',
          fieldlabel: 'Event Date',
          type: 'date',
          placeholder: 'Enter event date',
          //validators: ['required'],
        },
      ],
    },
    {
      label: 'Execution details',
      fields: [
        {
          id: 'f24',
          name: 'eventName',
          fieldlabel: 'Event Name',
          type: 'text',
          placeholder: 'Enter event name',
          //validators: ['required'],
        },
        {
          id: 'f25',
          name: 'eventDate',
          fieldlabel: 'Event Date',
          type: 'date',
          placeholder: 'Enter event date',
          //validators: ['required'],
        },
      ],
    },
    {
      label: 'Review & submit',
      fields: [
        {
          id: 'f26',
          name: 'eventName',
          fieldlabel: 'Event Name',
          type: 'text',
          placeholder: 'Enter event name',
          //validators: ['required'],
        },
        {
          id: 'f27',
          name: 'eventDate',
          fieldlabel: 'Event Date',
          type: 'date',
          placeholder: 'Enter event date',
          //validators: ['required'],
        },
      ],
    },
  ],
};
