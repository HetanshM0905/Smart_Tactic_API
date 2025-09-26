from tinydb import TinyDB, Query
import os
import uuid

class TinyDBService:
    def __init__(self):
        db_path = os.path.join(os.path.dirname(__file__), '../smart_tactic_tinydb.json')
        self.db = TinyDB(db_path)
        self.chat_table = self.db.table('chat_history')
        self.workflows_table = self.db.table('workflows')
        self.prompt_table = self.db.table('prompts')
        self.data_table = self.db.table('data')

    def get_chat_history(self, session_id):
        Chat = Query()
        chat_entry = self.chat_table.get(Chat.session_id == session_id)
        return chat_entry

    def save_message(self, session_id, role, content):
        Chat = Query()
        chat_entry = self.chat_table.get(Chat.session_id == session_id)
        if not chat_entry:
            chat_entry = {'session_id': session_id, 'history': [], 'formObject': {}}
        chat_entry['history'].append({'role': role, 'content': content})
        self.chat_table.upsert(chat_entry, Chat.session_id == session_id)

    def save_form_object(self, session_id, form_object):
        Chat = Query()
        chat_entry = self.chat_table.get(Chat.session_id == session_id)
        if not chat_entry:
            chat_entry = {'session_id': session_id, 'history': [], 'formObject': {}}
        chat_entry['formObject'] = form_object
        self.chat_table.upsert(chat_entry, Chat.session_id == session_id)

    def get_prompt(self, prompt_id='prompt1'):
        # Return the latest prompt (simulate for now)
        Prompt = Query()
        result = self.prompt_table.get(Prompt.id == prompt_id)
        return result

    def get_form_options(self, workflow_id='workflow1'):
        # Return the latest form schema (simulate for now)
        Workflow = Query()
        workflow = self.workflows_table.get(Workflow.id == workflow_id)
        return workflow

    def get_suggested_data(self, id=1):
        Record = Query()
        record = self.data_table.get(Record.id == id)
        return record

    def generate_llm_response(self, prompt, user_question, session_id):
        # Simulate LLM response as per your Angular interceptor logic
        # In production, call Gemini or other LLM here
        # For now, return a static JSON as per your format
        response = {
            "response": f"I can help with that. Based on the information I have, the event is named 'Innovate AI Summit 2024'. Is that correct?",
            "field_data": {"f1": "Innovate AI Summit 2024"},
            "suggested_buttons": [
                {"title": "Yes, that's correct", "action": "confirm", "id": "f1"},
                {"title": "No, I want to change it", "action": "chat", "id": "chat1"}
            ]
        }
        return response
