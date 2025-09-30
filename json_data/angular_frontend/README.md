# SmartTactic Frontend

This is an Angular frontend application that reads form configuration from `modified_layout.json` to create a dynamic form interface.

## Features

- Dynamic form generation based on JSON configuration
- Responsive design matching the SmartTactic UI
- Form validation and field visibility logic
- Category-based tactic type filtering
- Event type selection with cards interface

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Angular CLI (v17 or higher)

### Installation

1. Navigate to the project directory:
```bash
cd json_data/angular_frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open your browser and navigate to `http://localhost:4200`

## Project Structure

```
src/
├── app/
│   ├── create-tactic/
│   │   ├── create-tactic.component.ts
│   │   ├── create-tactic.component.html
│   │   └── create-tactic.component.scss
│   ├── models/
│   │   └── form-field.model.ts
│   ├── services/
│   │   └── form-data.service.ts
│   ├── app.component.ts
│   └── app.routes.ts
├── assets/
│   └── modified_layout.json
└── styles.scss
```

## Key Components

- **CreateTacticComponent**: Main form component that renders the dynamic form
- **FormDataService**: Service for loading and managing form configuration data
- **FormField Model**: TypeScript interfaces for form field definitions

## Form Configuration

The form is configured through the `modified_layout.json` file which contains:
- Page definitions with fields
- Lookup options for dropdowns
- Validation rules
- Field visibility logic

## Styling

The application uses SCSS for styling with a clean, modern design that matches the SmartTactic brand guidelines.
