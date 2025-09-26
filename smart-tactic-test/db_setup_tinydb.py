import json
from datetime import datetime
import os
from tinydb import TinyDB, Query

class SmartTacticTinyDB:
    def __init__(self, db_path="smart_tactic_tinydb.json"):
        """
        Initialize TinyDB database connection
        
        Args:
            db_path: Path to the TinyDB JSON file
        """
        try:
            self.db = TinyDB(db_path)
            self.db_path = db_path
            
            # Initialize tables (collections in TinyDB)
            self.tables = {
                'workflows': self.db.table('workflows'),
                'prompts': self.db.table('prompts'),
                'data': self.db.table('data'),
                'chat_history': self.db.table('chat_history'),
            }
            
            print(f"Connected to TinyDB: {db_path}")
            
        except Exception as e:
            print(f"Error connecting to TinyDB: {e}")
            raise
    
    def create_tables(self):
        """Create all necessary tables in TinyDB"""
        try:
            # TinyDB tables are created automatically when first accessed
            # We'll create a test document in each table to ensure they exist
            for table_name, table in self.tables.items():
                # Create a test document that we'll delete immediately
                test_doc = {
                    'created_at': datetime.now().isoformat(),
                    'test': True
                }
                doc_id = table.insert(test_doc)
                table.remove(doc_ids=[doc_id])  # Delete the test document
                print(f"Table '{table_name}' verified/created")
            
            print("All tables created successfully!")
            return True
            
        except Exception as e:
            print(f"Error creating tables: {e}")
            return False
    
    def insert_sample_data(self):
        """Insert sample data from mockdata.json"""
        try:
            # Load mock data
            # with open('mockdata.json', 'r') as f:
            #     mock_data = json.load(f)
            
            # # Insert a sample form using the template structure
            # template = mock_data['templates']['single_event_min']
            
            # # Create main form document
            # form_data = {
            #     'category': template['category'],
            #     'tactic_type': template['tactic_type'],
            #     'event_kind': template['event_kind'],
            #     'aligned_to_multi_event': template['aligned_to_multi_event'],
            #     'created_at': datetime.now().isoformat(),
            #     'updated_at': datetime.now().isoformat()
            # }
            
            # Add to forms table
            prompt = self.tables['prompts'].insert( { 
        "id":"prompt1", "text": "You are a Form assistant. You will suggest based on Data. You will have all context formschema and options.\nSo you will know fields and options. And also you will have chat history.\n{{FormObject}} {{chathistory}}\nSuggest based on this following Data {{data}}.\n\nInstructions to follow while suggesting.\n    1. You no need to give entire form information at once. If he asks for one field, give only that field information and suggestion.\n    2. If user gives different field value, update the form information and suggest next field to fill. No need to force this prefilled data.\n    3. When suggesting a value (e.g., event dates), always present confirmation and correction options as Markdown links:\n      [Yes, these dates are correct](action:confirm:eventName)\n      [No, change them](action:chat:eventName)\n      Only update the form if the user clicks the confirmation link.\n\n    4. Replace 'eventName' with the respective form field id from the form schema (e.g., 'eventName', 'eventStartDate').\n      Replace the link text (e.g., Yes, that's correct) as appropriate.\n      For confirmation links (e.g., 'Yes, that's correct'), use 'confirm' as ACTION_TYPE.\n      For all other links (e.g., 'No, I want to change it'), use 'chat' as ACTION_TYPE.\n\n    5. IMPORTANT: Your response MUST be a JSON object with three keys:\n      - 'response': the markdown string to display to the user (do not include button markdown links here)\n      - 'field_data': an object mapping field ids or button keys to the value that should be set if the user clicks a confirmation or other button\n      - 'suggested_buttons': an array of button objects, each with:\n          - 'title': the button text\n          - 'action': the action type (e.g., 'confirm', 'chat')\n          - 'id': the field id for suggestions, or a unique key like 'chat1' for other actions\n\n      Example response:\n      {\n        'response': 'I can help with that. Based on the information I have, the event is named 'Innovate AI Summit 2024'. Is that correct?',\n        'field_data': { 'f1': 'Innovate AI Summit 2024' },\n        'suggested_buttons': [\n          { 'title': 'Yes, that's correct', 'action': 'confirm', 'id': 'f1' },\n          { 'title': 'No, I want to change it', 'action': 'chat', 'id': 'chat1' }\n        ]\n      }\n\n    Only output valid JSON in this format. Do not include any other text or explanation outside the JSON object.\""
    })
            print(f"Sample data inserted successfully! Prompt ID: {prompt}")
            self.tables['data'].insert({"id": "data1", 
    "eventName": "Innovate AI Summit 2024",
    "eventDescription": "A premier event focusing on the latest advancements in Artificial Intelligence and Machine Learning.",
    "priority": "P0 - In budget",
    "owner": "user1@example.com",
    "startDate": "2024-10-15",
    "endDate": "2024-10-17",
    "eventDateConfidence": "High",
    "leads": "Yes",
    "numberOfInquiries": 450,
    "event_categorization": "e12",
    "eventOrganiser": "Tech Summits LLC",
    "eventPOC": "Alice Johnson",
    "fundingStatus": "Fully Funded",
    "eventHosting": "Hybrid Event",
    "city": "New York",
    "country": "USA",
    "venue": "Moscone Center",
    "registrationLink": "https://example.com/register/innovate-ai-2024",
    "salesKitLink": "https://example.com/sales/innovate-ai-2024",
    "cloudMarketingCostCenter": "CC1",
    "hasSpend": "Yes",
    "splitCostCenter": True,
    "inputCostCenterSplit": 50,
    "nonPrimaryOwners": "user2@example.com",
    "partnerRole": "Partner Involved",
    "partnerType": "Yes - Single Partner",
    "responsibilities": "Joint Messaging & Content Creation",
    "leadFollowUp": "Partner and Google together",
    "expectedRegistrations": 2500,
    "expectedAttendees": 1800,
    "campaignPrograms": [
      {
        "name": "AI - General",
        "percentage": 70
      },
      {
        "name": "AI - Build with AI",
        "percentage": 30
      }
    ],
    "adaptAdoptInvent": None,
    "accountSegmentAlignment": [
      {
        "name": "Enterprise",
        "percentage": 100
      }
    ],
    "accountSegmentType": [
      {
        "name": "Traditional",
        "percentage": 100
      }
    ],
    "buyerSegmentRollups": [
      {
        "name": "Executive",
        "percentage": 50
      },
      {
        "name": "Decision Maker",
        "percentage": 50
      }
    ],
    "industry": [
      "Financial Services",
      "Health Care"
    ],
    "productAlignment": [
      {
        "name": "GCP",
        "percentage": 100
      }
    ],
    "customerLifecycle": [
      {
        "name": "Greenfield",
        "percentage": 60
      },
      {
        "name": "Existing",
        "percentage": 40
      }
    ],
    "coreMessaging": [
      {
        "name": "AI",
        "percentage": 100
      }
    ],
    "event_details": {
      "event_ring": "Ring 2: Global 3rd Party",
      "event_party": "3rd Party Event",
      "event_category": "Developer",
      "event_category_owner": "Developer Owner",
      "event_subcategory": "3P Tentpole Developer Events",
      "event_subcategory_owner": "3P Tentpole Developer Events Owner"
    }}
     )
            self.tables['workflows'].insert({
                'id': 'workflow1', 
                "formSchema": {
                "layout": {
                    "type": "flex",
                    "gap": "16px",
                    "flexWrap": "wrap",
                    "flexDirection": "column"
               },
                "fields": [
                    {
                    "id": "f1",
                    "name": "eventName",
                    "fieldlabel": "Event name*",
                    "fieldTitle": "",
                    "fieldSubTitle": "",
                    "placeholder": "",
                    "type": "text",
                    "class": "",
                    "layout": {
                    }
                    },
                    {
                    "id": "f2",
                    "name": "eventDescription",
                    "fieldlabel": "Event description",
                    "fieldTitle": "Event description",
                    "fieldSubTitle":
                        "Provide a brief overview of the event’s purpose, goals, and any relevant context",
                    "placeholder": "Enter event description",
                    "type": "textarea",
                    "class": "",
                    "rows": 3,
                    "layout": {
                        "margin_bottom": "0px"
                    }
                    },
                    {
                    "id": "f7",
                    "name": "priorityOwner",
                    "layout": {
                        "type": "flex",
                        "display": "flex",
                        "gap": "16px",
                        "flexDirection": "row",
                        "justifyContent": "flex-start"
                    },
                    "subFields": [
                        {
                        "id": "f3",
                        "name": "priority",
                        "fieldlabel": "Priority",
                        "fieldTitle": "Priority",
                        "fieldSubTitle":
                            "Select priority based on importance and budget impact",
                        "type": "select",
                        "placeholder": "Select priority",
                        "options": [
                            { "key": "1", "value": "High" },
                            { "key": "2", "value": "Medium" },
                            { "key": "3", "value": "Low" }
                        ],
                        "layout": {
                            "flex": "1",
                            "margin_bottom": "0px"
                        }
                        },
                        {
                        "id": "f4",
                        "name": "owner",
                        "fieldlabel": "Owner",
                        "fieldTitle": "Owner",
                        "fieldSubTitle": "Select the tactic’s responsible person",
                        "type": "select",
                        "placeholder": "Select owner",
                        "options": [
                            { "key": "1", "value": "a@gmail.com" },
                            { "key": "2", "value": "b@gmail.com" },
                            { "key": "3", "value": "c@gmail.com" }
                        ],
                        "layout": {
                            "flex": "1"
                        }
                        }
                    ]
                    },
                    {
                    "id": "f9",
                    "name": "eventDates",
                    "label": "Let’s more about your event",
                    "layout": {
                        "type": "flex",
                        "display": "flex",
                        "gap": "16px",
                        "flexDirection": "row",
                        "justifyContent": "flex-start"
                    },
                    "subFields": [
                        {
                        "id": "f5",
                        "name": "eventStartDate",
                        "fieldTitle": "",
                        "fieldSubTitle": "",
                        "fieldlabel": "Event start date",
                        "placeholder": "Select start event date",
                        "type": "date",
                        "minDate": "2025-01-01",
                        "maxDate": "2025-12-31",
                        "startView": "multi-year",
                        "touchUi": True,
                        "layout": {
                            "flex": "1",
                            "marginRight": "10px"
                        }
                        },
                        {
                        "id": "f6",
                        "name": "eventEndDate",
                        "fieldTitle": "",
                        "fieldSubTitle": "",
                        "fieldlabel": "Event end date",
                        "placeholder": "Select end event date",
                        "type": "date",
                        "minDate": "2025-01-01",
                        "maxDate": "2025-12-31",
                        "startView": "multi-year",
                        "touchUi": True,
                        "layout": {
                            "flex": "1"
                        }
                        }
                    ]
                    },
                    {
                    "id": "",
                    "name": "eventDateCon&expPer",
                    "layout": {
                        "type": "flex",
                        "display": "flex",
                        "gap": "16px",
                        "flexDirection": "row",
                        "justifyContent": "flex-start"
                    },
                    "subFields": [
                        {
                        "id": "f7",
                        "name": "EventDateConfidence",
                        "fieldlabel": "Event date confidence*",
                        "fieldTitle":
                            "Choose how confident you are about the provided dates",
                        "fieldSubTitle": "",
                        "type": "select",
                        "placeholder": "Select event date confidence",
                        "options": [
                            { "key": "1", "value": "High" },
                            { "key": "2", "value": "Medium" },
                            { "key": "3", "value": "Low" }
                        ],
                        "layout": {
                            "flex": "1",
                            "margin_bottom": "5px"
                        }
                        },
                        {
                        "id": "f8",
                        "name": "expectedPerformance",
                        "fieldlabel": "Will this tactic generate customer inquiries ?*",
                        "fieldTitle": "Expected performance",
                        "fieldSubTitle": "",
                        "type": "select",
                        "placeholder": "Select expected performance",
                        "options": [
                            { "key": "1", "value": "Yes" },
                            { "key": "2", "value": "No" }
                        ],
                        "layout": {
                            "flex": "1",
                            "margin_bottom": "5px"
                        }
                        }
                    ]
                    },
                    {
                    "id": "",
                    "label": "Event categorization",
                    "subLabel":
                        "Classify your tactic event by selecting the appropriate ring, type, category, and owner. These details help organize events for reporting, tracking, and team ownership.",
                    "type": "grid",
                    "layout": {
                        "type": "grid",
                        "columns": 1,
                        "gap": "16px"
                    },
                    "gridFields": [
                        {
                        "id": "f9",
                        "name": "eventRing",
                        "fieldlabel": "Event ring*",
                        "type": "select",
                        "placeholder": "Select owner",
                        "options": [
                            { "key": "r1", "value": "Ring 1: Global 1st Party" },
                            { "key": "r2", "value": "Ring 2: Global 3rd Party" },
                            { "key": "r3", "value": "Ring 3: Global 1st Party Series" },
                            { "key": "r4", "value": "Ring 4: Regional / Local" }
                        ],
                        "layout": { "gridColumn": "1", "gridRow": "1" }
                        },
                        {
                        "id": "f10",
                        "name": "eventOwner",
                        "fieldlabel": "Is the event 1st party or the 3rd party ?*",
                        "type": "select",
                        "placeholder": "Select owner",
                        "options": [], 
                        "dependsOn": "f9",
                        "optionsMap": {
                            "r1": [{ "key": "p1", "value": "1st party event" }],
                            "r2": [{ "key": "p2", "value": "3rd Party Event" }],
                            "r3": [{ "key": "p3", "value": "Party C" }],
                            "r4": [{ "key": "p4", "value": "Party C" }]
                        },
                        "layout": { "gridColumn": "2", "gridRow": "1" }
                        },

                        {
                        "id": "f11",
                        "name": "eventCategory",
                        "fieldlabel": "Event category*",
                        "type": "select",
                        "placeholder": "Select owner",
                        "options": [],
                        "layout": { "gridColumn": "1", "gridRow": "2" },
                        "dependsOn": "f9.f10",
                        "optionsMap": {
                            "R1.P1": [{ "key": "C1", "value": "Category A" }],
                            "R1.P2": [{ "key": "C2", "value": "Category B" }],
                            "R2.P3": [{ "key": "C3", "value": "Category C" }]
                        }
                        },
                        {
                        "id": "f12",
                        "name": "eventCategoryOwner",
                        "fieldlabel": "Event category owner*",
                        "type": "select",
                        "placeholder": "Select owner",
                        "options": [],
                        "layout": { "gridColumn": "2", "gridRow": "2" },
                        "dependsOn": "f9.f10.f11",
                        "optionsMap": {
                            "R1.P1.C1": [{ "key": "CO1", "value": "Category owner A" }],
                            "R1.P2.C2": [{ "key": "CO2", "value": "Category owner B" }],
                            "R2.P3.C3": [{ "key": "CO3", "value": "Category owner C" }]
                        }
                        },

                        {
                        "id": "f13",
                        "name": "eventSubCategory",
                        "fieldlabel": "Event sub category*",
                        "type": "select",
                        "placeholder": "Select owner",
                        "options": [
                            { "key": "1", "value": "a@gmail.com" },
                            { "key": "2", "value": "b@gmail.com" },
                            { "key": "3", "value": "c@gmail.com" }
                        ],
                        "layout": { "gridColumn": "1", "gridRow": "3" }
                        },
                        {
                        "id": "f14",
                        "name": "eventSubCategoryOwner",
                        "fieldlabel": "Event sub category owner*",
                        "type": "select",
                        "placeholder": "Select owner",
                        "options": [
                            { "key": "1", "value": "a@gmail.com" },
                            { "key": "2", "value": "b@gmail.com" },
                            { "key": "3", "value": "c@gmail.com" }
                        ],
                        "layout": { "gridColumn": "2", "gridRow": "3" }
                        },

                        {
                        "id": "f15",
                        "name": "eventOrganizer",
                        "fieldlabel": "Event organizer*",
                        "type": "select",
                        "placeholder": "Select owner",
                        "options": [
                            { "key": "1", "value": "a@gmail.com" },
                            { "key": "2", "value": "b@gmail.com" },
                            { "key": "3", "value": "c@gmail.com" }
                        ],
                        "layout": { "gridColumn": "1", "gridRow": "4" }
                        },
                        {
                        "id": "f16",
                        "name": "eventPointOfContact",
                        "fieldlabel": "Event point of contact*",
                        "type": "select",
                        "placeholder": "Select owner",
                        "options": [
                            { "key": "1", "value": "a@gmail.com" },
                            { "key": "2", "value": "b@gmail.com" },
                            { "key": "3", "value": "c@gmail.com" }
                        ],
                        "layout": { "gridColumn": "2", "gridRow": "4" }
                        },

                        {
                        "id": "f17",
                        "name": "eventFundingStatus",
                        "fieldlabel": "Funding status",
                        "type": "select",
                        "placeholder": "Select owner",
                        "options": [
                            { "key": "1", "value": "a@gmail.com" },
                            { "key": "2", "value": "b@gmail.com" },
                            { "key": "3", "value": "c@gmail.com" }
                        ],
                        "layout": { "gridColumn": "1 / span 2", "gridRow": "5" }
                        }
                    ]
                    },
                    {
                    "id": "f18",
                    "name": "eventHost",
                    "fieldlabel": "How is the event being hosted ?*",
                    "fieldTitle": "Location details",
                    "fieldSubTitle":
                        "Specify how the event will be conducted to help align planning, logistics, and audience engagement strategies",
                    "placeholder": "Enter event description",
                    "type": "select",
                    "options": [
                        { "key": "1", "value": "a@gmail.com" },
                        { "key": "2", "value": "b@gmail.com" },
                        { "key": "3", "value": "c@gmail.com" }
                    ],
                    "class": "",
                    "rows": 3,
                    "layout": {
                        "margin_bottom": "0px"
                    }
                    },
                    {
                    "id": "",
                    "layout": {
                        "type": "flex",
                        "display": "flex",
                        "gap": "16px",
                        "flexDirection": "row",
                        "justifyContent": "flex-start"
                    },
                    "subFields": [
                        {
                        "id": "f19",
                        "name": "region",
                        "fieldlabel": "Select region*",
                        "fieldTitle": "",
                        "fieldSubTitle": "",
                        "type": "select",
                        "placeholder": "Select region*",
                        "options": [
                            { "key": "1", "value": "High" },
                            { "key": "2", "value": "Medium" },
                            { "key": "3", "value": "Low" }
                        ],
                        "layout": {
                            "flex": "1",
                            "margin_bottom": "0px"
                        }
                        },
                        {
                        "id": "f20",
                        "name": "country",
                        "fieldlabel": "Select country*",
                        "type": "multiselect",
                        "options": [
                            { "key": "CA", "value": "Canada" },
                            { "key": "US", "value": "United States" },
                            { "key": "MX", "value": "Mexico" },
                            { "key": "PR", "value": "Puerto Rico" }
                        ],
                        "layout": {
                            "flex": "2",
                            "margin_bottom": "0px"
                        }
                        }
                    ]
                    }
                ]
                },
                "options": {
                "priorityOptions": ["P0 - In budget", "P1 - Nice to have"],
                "dateConfidenceOptions": ["Low", "Medium", "High"],
                "fundingOptions": ["Fully Funded", "Partially Funded", "Not Funded", "Unsure"],
                "hostingOptions": ["Digital Event", "Physical Event", "Hybrid Event"],
                "yesNoOptions": ["Yes", "No"],
                "initiativeOptions": ["Enterprise", "Corporate", "SMB", "Startups (P1A)", "SDR", "Direct Touched", "PPF/MDF", "ISV", "Others", "Partner", "Named", "Self-Serve", "GCP", "GWS", "Global Partner Programs", "Demand Gen Global Campaign Build", "NEXT", "Summits", "Events Global Build", "Global Events", "Security Demand Generation", "Security Product Marketing", "Developer Advocacy", "GCP AI Perception", "GWS AI Consideration", "Brand Global Build", "Developer Perception", "Regional Brand Campaign", "Global Brand Campaigns", "Brand Partnerships", "GWS Product Marketing", "GCP Product Marketing", "GCP Analyst Relations", "Customer Reference", "Mindshare / Thought Leadership", "Activation", "Demand Ops", "Systems & Data", "Strategy, Planning & Ops", "Marketer Enablement", "One Google", "GCM Reserve - Acquire Revenue", "GCM Reserve - Improve Efficiency", "GCM Reserve - Lift Mindshare", "GCM Reserve - Source Demand", "GCM Reserve", "DEI & Culture"],
                "campaignPrograms": ["Tactic is not tied...", "AI - General", "AI - AI For Marketing", "AI - AI-powered Work", "AI - AI-powered Customer Experiences", "AI - Build with AI", "AI - Responsible AI", "AI - ROI of AI", "AI - AI Trends", "Data Cloud - General", "Data Cloud - Data Analytics and AI Platform", "Data Cloud - Database Modernization", "Data Cloud - Business Intelligence (Looker)", "Modern Infrastructure and Apps - General", "Modern Infrastructure and Apps - Dev Productivity with Gen AI", "Modern Infrastructure and Apps - Build Modern Apps", "Modern Infrastructure and Apps - AI Infra", "Modern Infrastructure and Apps - Infrastructure / Lift & Transform", "Security - General", "Security - Mandiant Expertise", "Security - Transform Security Operations", "Security - Cloud Security", "Security - Google Threat Intelligence", "Security - Fraud Protection Solutions", "Security - CEP", "Google Workspace - General", "Google Workspace - Transform Work with Google AI", "Google Workspace - Secure Alternative", "Google Workspace - Modernize IT"],
                "adaptOptions": ["Adapt", "Adopt", "Invent"],
                "accountSegmentOptions": ["Enterprise", "Corporate", "SMB", "Select", "Startups"],
                "accountSegmentTypeOptions": ["Digital Natives", "Traditional", "ISV & Saas"],
                "buyerSegmentOptions": ["Executive", "Decision Maker", "Practitioner", "Partner", "Line of Business Target Titles"],
                "industryOptions": ["Retail", "Health Care", "Financial Services", "Telco, Media & Gaming", "Manufacturing", "Public Sector"],
                "productOptions": ["GCP", "GWS"],
                "lifecycleOptions": ["Existing", "Greenfield"],
                "coreMessagingOptions": ["AI", "Core"],
                "userList": ["user1@example.com", "user2@example.com"],
                "cityList": ["New York", "London", "Bangalore"],
                "countryList": ["USA", "UK", "India"],
                "ccList": ["CC1", "CC2", "CC3"],
                "adaptAdoptInvent": {
                    "True": ["Adapt: Partial adaptation of Global Campaign asset - copy or content edits including translation for local re-use", "Adopt: Full adoption of Global Campaign asset - no content change, copy change, or localization"],
                    "false": ["Invent: Completely new asset - no use of Global Campaign asset"]
                },
                "multiPercentageOptions": {
                    "accountSegmentAlignmentOptions": ["Enterprise", "Corporate", "SMB", "Select", "Startups"],
                    "accountSegmentTypeOptions": ["Digital Natives", "Traditional", "ISV & Saas"],
                    "buyerSegmentRollupsOptions": ["Executive", "Decision Maker", "Practitioner", "Partner", "Line of Business Target Titles"],
                    "productAlignmentOptions": ["GCP", "GWS"],
                    "customerLifecycleOptions": ["Existing", "Greenfield"],
                    "coreMessagingOptions": ["AI", "Core"],
                    "initiativeSplitOptions": {
                    "Direct Touched": ["Direct Mail", "Email Marketing", "Telemarketing", "SMS/Text Marketing", "Direct-Response Advertising", "Door-to-Door Marketing"],
                    "Partner": ["Affiliate Marketing", "Co-Branding", "Content Partnerships", "Referral Programs", "Joint Ventures", "Influencer Partnerships", "Channel Partnerships"],
                    "Self-Serve": ["Self-Serve Advertising Platforms", "E-commerce", "Online Knowledge Bases/Help Centers", "Interactive Tools", "Webinars and Online Courses"]
                    }
                },
                "event_categorization": ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9", "e10", "e11", "e12", "e13", "e14", "e15", "e16", "e17", "e18", "e19", "e20", "e21", "e22", "e23", "e24", "e25", "e26", "e27", "e28", "e29", "e30", "e31", "e32", "e33", "e34", "e35", "e36", "e37", "e38", "e39", "e40", "e41", "e42", "e43", "e44", "e45", "e46", "e47", "e48", "e49", "e50", "e51", "e52", "e53", "e54", "e55", "e56", "e57", "e58", "e59", "e60", "e61", "e62", "e63", "e64", "e65", "e66", "e67", "e68", "e69", "e70", "e71", "e72", "e73", "e74", "e75", "e76", "e77", "e78", "e79", "e80", "e81", "e82", "e83", "e84", "e85", "e86", "e87", "e88", "e89", "e90", "e91", "e92", "e93", "e94", "e95", "e96", "e97", "e98", "e99", "e100", "e101", "e102", "e103", "e104", "e105", "e106", "e107", "e108", "e109", "e110", "e111", "e112", "e113", "e114"],
                "f8": ["Yes", "No"],
                "f51": ["Yes - Single Partner", "Yes - Multiple Partners", "No Partner Involvement"],
                "f52": ["Partner Generated Thought Leadership", "Joint Messaging & Content Creation", "Lead Nurture & Follow Up", "Speak at Event", "Host Event"],
                "f53": ["Partner Only", "Google Sales Only", "Partner and Google together"],
                "f50": ["Partner Host", "Partner Involved", "No Partner Involvement"]
                }
                })
            self.tables['chat_history'].insert({"id": '1234', "history": []})
            return True
            
        except Exception as e:
            print(f"Error inserting sample data: {e}")
            return False
    
    def show_tables(self):
        """Show all tables in the database"""
        try:
            print("\nTables in TinyDB database:")
            for table_name in self.tables.keys():
                count = len(self.tables[table_name])
                print(f"- {table_name} ({count} documents)")
            return list(self.tables.keys())
        except Exception as e:
            print(f"Error showing tables: {e}")
            return []
    
    def get_form_by_id(self, form_id):
        """Get a complete form by ID"""
        try:
            # Get main form
            form_docs = self.tables['forms'].search(Query().doc_id == form_id)
            if not form_docs:
                return None
            
            form_data = form_docs[0]
            form_data['id'] = form_id
            
            # Get all related data
            collections_to_fetch = [
                'form_basic', 'form_organization', 'form_logistics', 
                'form_finance', 'form_extras', 'form_partners', 
                'form_forecasts', 'form_campaign_program', 'form_review'
            ]
            
            for collection_name in collections_to_fetch:
                docs = self.tables[collection_name].search(Query().form_id == form_id)
                form_data[collection_name] = docs
            
            # Get arrays (countries, cost center splits, etc.)
            countries = self.tables['form_countries'].search(Query().form_id == form_id)
            form_data['countries'] = [doc['country'] for doc in countries]
            
            cost_splits = self.tables['form_cost_center_splits'].search(Query().form_id == form_id)
            form_data['cost_center_splits'] = cost_splits
            
            partner_resps = self.tables['form_partner_responsibilities'].search(Query().form_id == form_id)
            form_data['partner_responsibilities'] = [doc['responsibility'] for doc in partner_resps]
            
            program_splits = self.tables['form_program_splits'].search(Query().form_id == form_id)
            form_data['program_splits'] = program_splits
            
            return form_data
            
        except Exception as e:
            print(f"Error getting form by ID: {e}")
            return None
    
    def get_all_forms(self):
        """Get all forms"""
        try:
            forms = self.tables['forms'].all()
            for form in forms:
                form['id'] = form.doc_id
            return forms
        except Exception as e:
            print(f"Error getting all forms: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()
            print("TinyDB connection closed")

def main():
    """Main function to set up the TinyDB database"""
    try:
        db = SmartTacticTinyDB()
        print("Setting up SmartTactic TinyDB database...")
        
        # Create tables
        # if db.create_tables():
        #     print("Tables created successfully!")
            
        #     # Show tables
        #     db.show_tables()
            
        #     # Insert sample data
        #     print("\nInserting sample data...")
        #     db.insert_sample_data()
        #     db.show_tables()
            
        # else:
        #     print("Failed to create tables!")
        # db.tables['chat_history'].insert({"id": '1234', "history": []})
        db.tables['data'].insert(
            {"id": "1", 
            "eventName": "Innovate AI Summit 2024",
            "eventDescription": "A premier event focusing on the latest advancements in Artificial Intelligence and Machine Learning.",
            "priority": "P0 - In budget",
            "owner": "user1@example.com",
            "startDate": "2024-10-15",
    "endDate": "2024-10-17",
    "eventDateConfidence": "High",
    "leads": "Yes",
    "numberOfInquiries": 450,
    "event_categorization": "e12",
    "eventOrganiser": "Tech Summits LLC",
    "eventPOC": "Alice Johnson",
    "fundingStatus": "Fully Funded",
    "eventHosting": "Hybrid Event",
    "city": "New York",
    "country": "USA",
    "venue": "Moscone Center",
    "registrationLink": "https://example.com/register/innovate-ai-2024",
    "salesKitLink": "https://example.com/sales/innovate-ai-2024",
    "cloudMarketingCostCenter": "CC1",
    "hasSpend": "Yes",
    "splitCostCenter": True,
    "inputCostCenterSplit": 50,
    "nonPrimaryOwners": "user2@example.com",
    "partnerRole": "Partner Involved",
    "partnerType": "Yes - Single Partner",
    "responsibilities": "Joint Messaging & Content Creation",
    "leadFollowUp": "Partner and Google together",
    "expectedRegistrations": 2500,
    "expectedAttendees": 1800,
    "campaignPrograms": [
      {
        "name": "AI - General",
        "percentage": 70
      },
      {
        "name": "AI - Build with AI",
        "percentage": 30
      }
    ],
    "adaptAdoptInvent": None,
    "accountSegmentAlignment": [
      {
        "name": "Enterprise",
        "percentage": 100
      }
    ],
    "accountSegmentType": [
      {
        "name": "Traditional",
        "percentage": 100
      }
    ],
    "buyerSegmentRollups": [
      {
        "name": "Executive",
        "percentage": 50
      },
      {
        "name": "Decision Maker",
        "percentage": 50
      }
    ],
    "industry": [
      "Financial Services",
      "Health Care"
    ],
    "productAlignment": [
      {
        "name": "GCP",
        "percentage": 100
      }
    ],
    "customerLifecycle": [
      {
        "name": "Greenfield",
        "percentage": 60
      },
      {
        "name": "Existing",
        "percentage": 40
      }
    ],
    "coreMessaging": [
      {
        "name": "AI",
        "percentage": 100
      }
    ],
    "event_details": {
      "event_ring": "Ring 2: Global 3rd Party",
      "event_party": "3rd Party Event",
      "event_category": "Developer",
      "event_category_owner": "Developer Owner",
      "event_subcategory": "3P Tentpole Developer Events",
      "event_subcategory_owner": "3P Tentpole Developer Events Owner"
    }})
        db.show_tables()
        
        
        db.close()
    
    except Exception as e:
        print(f"Failed to initialize TinyDB database: {e}")
    
    print("\nTinyDB database setup completed!")

if __name__ == "__main__":
    main()
