from flask import Blueprint, request, jsonify
from .chat_service.tinydb_service import TinyDBService

chatbot_api = Blueprint('chatbot_api', __name__)
db_service = TinyDBService()

@chatbot_api.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    data = request.get_json()
    session_id = data.get('sessionId', 'default')
    user_question = data.get('question', '')

    # Get chat history and form object from tinydb
    chat_history, form_object = db_service.get_chat_history(session_id)

    # Compose prompt for LLM (simulate for now)
    prompt = f"chat history: {chat_history}\nform object: {form_object}\nUser: {user_question}"

    # Simulate LLM response (replace with actual LLM call)
    llm_response = db_service.generate_llm_response(prompt, user_question, session_id)

    # Save user message and LLM response to history
    db_service.save_message(session_id, 'user', user_question)
    db_service.save_message(session_id, 'assistant', llm_response['response'])

    return jsonify({
        'response': llm_response['response'],
        'field_data': llm_response['field_data'],
        'suggested_buttons': llm_response['suggested_buttons'],
        'session_id': session_id
    })
