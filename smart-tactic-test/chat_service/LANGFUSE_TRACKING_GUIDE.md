# Comprehensive Langfuse Tracking Guide

## Overview
This guide shows how to track **state**, **prompt**, **chat history**, and **workflow** data in Langfuse for each request in your Smart Tactic API.

## Enhanced LangfuseService Methods

### 1. Create Request Trace with Full Context
```python
# Create comprehensive trace for each chat request
trace_id = langfuse_service.create_request_trace(
    session_id="user_session_123",
    user_question="Can you help me with this form",
    workflow_data=workflow.dict(),  # Complete workflow schema
    current_state={"f1": "AI Summit", "f2": ""},  # Current form state
    chat_history=chat_history_list  # Full conversation history
)
```

### 2. Log LLM Generation with Context
```python
# Log LLM call with full prompt context
response = langfuse_service.log_llm_generation_with_context(
    trace_id=trace_id,
    name="chat_completion",
    model="gemini-1.5-pro",
    input_prompt=built_prompt,
    prompt_template=raw_template,  # Original template
    prompt_variables={  # All variables used
        'state': current_state,
        'FormObject': workflow_data,
        'chathistory': chat_history,
        'user_question': user_question,
        'data': sample_data
    },
    llm_service=llm_service,
    form_schema=workflow.schema
)
```

### 3. Track State Updates
```python
# Log when form fields are updated
langfuse_service.log_state_update(
    trace_id=trace_id,
    field_updates={"f1": "New Event Name", "f2": "Description"},
    session_id=session_id
)
```

### 4. Track Validation Errors
```python
# Log field validation failures
langfuse_service.log_validation_error(
    trace_id=trace_id,
    field_id="f3",
    error_message="Priority must be selected",
    field_value=None
)
```

## What Gets Tracked

### 🔄 **State Tracking**
- **Current form state**: All filled fields and values
- **Completion percentage**: How much of the form is complete
- **Next empty fields**: What fields need to be filled next
- **Field analysis**: Types, counts, and validation status

### 📝 **Prompt Tracking**
- **Template**: Original prompt template with placeholders
- **Variables**: All data injected into the template
- **Final prompt**: Complete prompt sent to LLM
- **Model config**: Temperature, max tokens, etc.

### 💬 **Chat History Tracking**
- **Conversation flow**: Complete message history
- **Message analysis**: User vs assistant message counts
- **Content metrics**: Message lengths, button interactions
- **Timestamps**: When each interaction occurred

### ⚙️ **Workflow Tracking**
- **Schema definition**: Complete form structure
- **Field metadata**: Types, options, validation rules
- **Workflow context**: Name, ID, configuration
- **Available options**: All dropdown/select options

## Integration Example

Here's how to integrate comprehensive tracking into your chat service:

```python
def process_chat_with_tracking(self, request: ChatRequest) -> ChatResponse:
    try:
        # 1. Gather all context data
        workflow = self.workflow_repo.get_by_id(request.workflow_id)
        current_state = self.state_service.get_state(request.session_id)
        chat_history = self._get_chat_history(request.session_id)
        prompt_template = self._get_prompt_template()
        
        # 2. Create comprehensive trace
        trace_id = self.langfuse_service.create_request_trace(
            session_id=request.session_id,
            user_question=request.question,
            workflow_data=workflow.dict(),
            current_state=current_state,
            chat_history=chat_history
        )
        
        # 3. Build prompt with variables
        prompt_variables = {
            'state': current_state,
            'FormObject': workflow.dict(),
            'chathistory': chat_history,
            'user_question': request.question,
            'data': self._get_suggested_data()
        }
        
        built_prompt = self._build_prompt(prompt_template, **prompt_variables)
        
        # 4. Get LLM response with full tracking
        llm_response = self.langfuse_service.log_llm_generation_with_context(
            trace_id=trace_id,
            name="form_assistant_completion",
            model=self.llm_service.model_name,
            input_prompt=built_prompt,
            prompt_template=prompt_template,
            prompt_variables=prompt_variables,
            llm_service=self.llm_service,
            form_schema=workflow.schema
        )
        
        # 5. Track state updates if any
        if llm_response.field_data:
            self.langfuse_service.log_state_update(
                trace_id=trace_id,
                field_updates=llm_response.field_data,
                session_id=request.session_id
            )
        
        return llm_response
        
    except Exception as e:
        # Track errors too
        if trace_id:
            self.langfuse_service.log_validation_error(
                trace_id=trace_id,
                field_id="system",
                error_message=str(e),
                field_value=None
            )
        raise
```

## Langfuse Dashboard Views

### 📊 **Traces View**
- Each request creates a trace with complete context
- View user journey through form completion
- See state progression over time
- Track completion rates and drop-off points

### 🔍 **Spans View**
- **workflow_context**: Complete workflow schema and metadata
- **form_state**: Current state with completion analysis
- **chat_history**: Conversation context and metrics
- **LLM generations**: Prompt, response, and performance data

### 📈 **Analytics**
- **Form completion rates**: Track which fields cause issues
- **Response times**: Monitor LLM performance
- **User patterns**: See common interaction flows
- **Error tracking**: Identify validation and system issues

## Advanced Features

### 🎯 **Session Analytics**
```python
# Track complete user sessions
metadata = {
    'session_duration': session_end - session_start,
    'total_interactions': len(chat_history),
    'form_completion_rate': completion_percentage,
    'fields_completed': list(filled_fields.keys()),
    'user_satisfaction': feedback_score
}
```

### 🔄 **Real-time Monitoring**
- Monitor active form sessions
- Track completion bottlenecks
- Identify problematic form fields
- Monitor LLM response quality

### 📊 **Custom Metrics**
- Field completion rates
- Average session duration
- User satisfaction scores
- Error frequency by field type

## Usage in Your Application

To use this comprehensive tracking, update your chat service to call:

1. `create_request_trace()` at the start of each request
2. `log_llm_generation_with_context()` for LLM calls
3. `log_state_update()` when form fields change
4. `log_validation_error()` for any validation issues

This provides complete visibility into user interactions, form completion patterns, and system performance in Langfuse.
