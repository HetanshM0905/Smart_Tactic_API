from tinydb import TinyDB, Query
from typing import Any, Dict, List, Optional
import os
from datetime import datetime

from repositories.base import ChatRepository, WorkflowRepository, PromptRepository, DataRepository, StateRepository
from models.schemas import ChatHistory, WorkflowSchema, PromptTemplate, ChatMessage, State  
from exceptions import DatabaseException
from utils.logger import logger
from config import config


class TinyDBChatRepository(ChatRepository):
    """TinyDB implementation of chat repository"""
    
    def __init__(self, db: TinyDB):
        self.db = db
        self.table = db.table('chat_history')
    
    def get_by_id(self, id: str) -> Optional[ChatHistory]:
        return self.get_chat_history(id)
    
    def create(self, entity: ChatHistory) -> ChatHistory:
        try:
            data = entity.dict()
            self.table.insert(data)
            logger.info(f"Created chat history for session: {entity.session_id}")
            return entity
        except Exception as e:
            logger.error(f"Failed to create chat history: {e}")
            raise DatabaseException(f"Failed to create chat history: {e}")
    
    def update(self, id: str, entity: ChatHistory) -> Optional[ChatHistory]:
        try:
            Chat = Query()
            data = entity.dict()
            self.table.upsert(data, Chat.session_id == id)
            logger.info(f"Updated chat history for session: {id}")
            return entity
        except Exception as e:
            logger.error(f"Failed to update chat history: {e}")
            raise DatabaseException(f"Failed to update chat history: {e}")
    
    def delete(self, id: str) -> bool:
        try:
            Chat = Query()
            result = self.table.remove(Chat.session_id == id)
            success = len(result) > 0
            if success:
                logger.info(f"Deleted chat history for session: {id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete chat history: {e}")
            raise DatabaseException(f"Failed to delete chat history: {e}")
    
    def list_all(self) -> List[ChatHistory]:
        try:
            records = self.table.all()
            return [ChatHistory(**record) for record in records]
        except Exception as e:
            logger.error(f"Failed to list chat histories: {e}")
            raise DatabaseException(f"Failed to list chat histories: {e}")
    
    def get_chat_history(self, session_id: str) -> Optional[ChatHistory]:
        try:
            Chat = Query()
            record = self.table.get(Chat.session_id == session_id)
            if record:
                return ChatHistory(**record)
            return None
        except Exception as e:
            logger.error(f"Failed to get chat history for session {session_id}: {e}")
            raise DatabaseException(f"Failed to get chat history: {e}")
    
    def save_message(self, session_id: str, role: str, content: str) -> None:
        try:
            Chat = Query()
            chat_entry = self.table.get(Chat.session_id == session_id)
            
            message = ChatMessage(
                role=role,
                content=content,
                timestamp=datetime.now().isoformat()
            )
            
            if not chat_entry:
                chat_history = ChatHistory(
                    session_id=session_id,
                    history=[message],
                    form_object={}
                )
                self.create(chat_history)
            else:
                chat_history = ChatHistory(**chat_entry)
                chat_history.history.append(message)
                self.update(session_id, chat_history)
                
            logger.info(f"Saved message for session {session_id}: {role}")
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            raise DatabaseException(f"Failed to save message: {e}")
    
    def save_form_object(self, session_id: str, form_object: Dict[str, Any]) -> None:
        try:
            Chat = Query()
            chat_entry = self.table.get(Chat.session_id == session_id)
            
            if not chat_entry:
                chat_history = ChatHistory(
                    session_id=session_id,
                    history=[],
                    form_object=form_object
                )
                self.create(chat_history)
            else:
                chat_history = ChatHistory(**chat_entry)
                chat_history.form_object = form_object
                self.update(session_id, chat_history)
                
            logger.info(f"Saved form object for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to save form object: {e}")
            raise DatabaseException(f"Failed to save form object: {e}")


class TinyDBWorkflowRepository(WorkflowRepository):
    """TinyDB implementation of workflow repository"""
    
    def __init__(self, db: TinyDB):
        self.db = db
        self.table = db.table('workflows')
    
    def get_by_id(self, id: str) -> Optional[WorkflowSchema]:
        return self.get_form_options(id)
    
    def create(self, entity: WorkflowSchema) -> WorkflowSchema:
        try:
            data = entity.dict()
            self.table.insert(data)
            logger.info(f"Created workflow: {entity.id}")
            return entity
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise DatabaseException(f"Failed to create workflow: {e}")
    
    def update(self, id: str, entity: WorkflowSchema) -> Optional[WorkflowSchema]:
        try:
            Workflow = Query()
            data = entity.dict()
            self.table.upsert(data, Workflow.id == id)
            logger.info(f"Updated workflow: {id}")
            return entity
        except Exception as e:
            logger.error(f"Failed to update workflow: {e}")
            raise DatabaseException(f"Failed to update workflow: {e}")
    
    def delete(self, id: str) -> bool:
        try:
            Workflow = Query()
            result = self.table.remove(Workflow.id == id)
            success = len(result) > 0
            if success:
                logger.info(f"Deleted workflow: {id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete workflow: {e}")
            raise DatabaseException(f"Failed to delete workflow: {e}")
    
    def list_all(self) -> List[WorkflowSchema]:
        try:
            records = self.table.all()
            return [WorkflowSchema(**record) for record in records]
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            raise DatabaseException(f"Failed to list workflows: {e}")
    
    def get_form_options(self, workflow_id: str) -> Optional[WorkflowSchema]:
        try:
            Workflow = Query()
            record = self.table.get(Workflow.id == workflow_id)
            if record:
                return WorkflowSchema(**record)
            return None
        except Exception as e:
            logger.error(f"Failed to get workflow {workflow_id}: {e}")
            raise DatabaseException(f"Failed to get workflow: {e}")


class TinyDBPromptRepository(PromptRepository):
    """TinyDB implementation of prompt repository"""
    
    def __init__(self, db: TinyDB):
        self.db = db
        self.table = db.table('prompts')
    
    def get_by_id(self, id: str) -> Optional[PromptTemplate]:
        return self.get_prompt(id)
    
    def create(self, entity: PromptTemplate) -> PromptTemplate:
        try:
            data = entity.dict()
            self.table.insert(data)
            logger.info(f"Created prompt: {entity.id}")
            return entity
        except Exception as e:
            logger.error(f"Failed to create prompt: {e}")
            raise DatabaseException(f"Failed to create prompt: {e}")
    
    def update(self, id: str, entity: PromptTemplate) -> Optional[PromptTemplate]:
        try:
            Prompt = Query()
            data = entity.dict()
            self.table.upsert(data, Prompt.id == id)
            logger.info(f"Updated prompt: {id}")
            return entity
        except Exception as e:
            logger.error(f"Failed to update prompt: {e}")
            raise DatabaseException(f"Failed to update prompt: {e}")
    
    def delete(self, id: str) -> bool:
        try:
            Prompt = Query()
            result = self.table.remove(Prompt.id == id)
            success = len(result) > 0
            if success:
                logger.info(f"Deleted prompt: {id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete prompt: {e}")
            raise DatabaseException(f"Failed to delete prompt: {e}")
    
    def list_all(self) -> List[PromptTemplate]:
        try:
            records = self.table.all()
            return [PromptTemplate(**record) for record in records]
        except Exception as e:
            logger.error(f"Failed to list prompts: {e}")
            raise DatabaseException(f"Failed to list prompts: {e}")
    
    def get_prompt(self, prompt_id: str) -> Optional[PromptTemplate]:
        try:
            Prompt = Query()
            record = self.table.get(Prompt.id == prompt_id)
            if record:
                return PromptTemplate(**record)
            return None
        except Exception as e:
            logger.error(f"Failed to get prompt {prompt_id}: {e}")
            raise DatabaseException(f"Failed to get prompt: {e}")


class TinyDBDataRepository(DataRepository):
    """TinyDB implementation of data repository"""
    
    def __init__(self, db: TinyDB):
        self.db = db
        self.table = db.table('data')
    
    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        return self.get_suggested_data(id)
    
    def create(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.table.insert(entity)
            logger.info(f"Created data record: {entity.get('id', 'unknown')}")
            return entity
        except Exception as e:
            logger.error(f"Failed to create data record: {e}")
            raise DatabaseException(f"Failed to create data record: {e}")
    
    def update(self, id: str, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            Record = Query()
            self.table.upsert(entity, Record.id == id)
            logger.info(f"Updated data record: {id}")
            return entity
        except Exception as e:
            logger.error(f"Failed to update data record: {e}")
            raise DatabaseException(f"Failed to update data record: {e}")
    
    def delete(self, id: str) -> bool:
        try:
            Record = Query()
            result = self.table.remove(Record.id == id)
            success = len(result) > 0
            if success:
                logger.info(f"Deleted data record: {id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete data record: {e}")
            raise DatabaseException(f"Failed to delete data record: {e}")
    
    def list_all(self) -> List[Dict[str, Any]]:
        try:
            return self.table.all()
        except Exception as e:
            logger.error(f"Failed to list data records: {e}")
            raise DatabaseException(f"Failed to list data records: {e}")
    
    def get_suggested_data(self, id: str) -> Optional[Dict[str, Any]]:
        try:
            Record = Query()
            record = self.table.get(Record.id == id)
            return record
        except Exception as e:
            logger.error(f"Failed to get data record {id}: {e}")
            raise DatabaseException(f"Failed to get data record: {e}")


class TinyDBStateRepository(StateRepository):
    """TinyDB implementation of state repository"""
    
    def __init__(self, db: TinyDB):
        self.db = db
        self.table = db.table('state_management')
    
    def get_by_id(self, id: str) -> Optional[State]:
        return self.get_state(id)
    
    def create(self, entity: State) -> State:
        try:
            data = entity.dict()
            self.table.insert(data)
            logger.info(f"Created state: {entity.id}")
            return entity
        except Exception as e:
            logger.error(f"Failed to create state: {e}")
            raise DatabaseException(f"Failed to create state: {e}")
    
    def update(self, id: str, entity: Dict[str, Any]) -> Optional[State]:
        try:
            State = Query()
            self.table.upsert(entity, State.id == id)
            logger.info(f"Updated state: {id}")
            return entity
        except Exception as e:
            logger.error(f"Failed to update state: {e}")
            raise DatabaseException(f"Failed to update state: {e}")
    
    def delete(self, id: str) -> bool:
        try:
            State = Query()
            result = self.table.remove(State.id == id)
            success = len(result) > 0
            if success:
                logger.info(f"Deleted state: {id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete state: {e}")
            raise DatabaseException(f"Failed to delete state: {e}")
    
    def list_all(self) -> List[State]:
        try:
            records = self.table.all()
            return [State(**record) for record in records]
        except Exception as e:
            logger.error(f"Failed to list states: {e}")
            raise DatabaseException(f"Failed to list states: {e}")
    
    def get_state(self, state_id: str) -> Optional[State]:
        try:
            StateQuery = Query()
            record = self.table.get(StateQuery.id == state_id)
            if record:
                return State(**record)
            return None
        except Exception as e:
            logger.error(f"Failed to get state {state_id}: {e}")
            raise DatabaseException(f"Failed to get state: {e}")


class DatabaseManager:
    """Database manager that provides repository instances"""
    
    def __init__(self):
        db_path = os.path.join(os.path.dirname(__file__), '..', config.database.db_path)
        self.db = TinyDB(db_path)
        
        # Initialize repositories
        self.chat_repo = TinyDBChatRepository(self.db)
        self.workflow_repo = TinyDBWorkflowRepository(self.db)
        self.prompt_repo = TinyDBPromptRepository(self.db)
        self.data_repo = TinyDBDataRepository(self.db)
        self.state_repo = TinyDBStateRepository(self.db)
        
        logger.info(f"Database initialized at: {db_path}")
    
    def close(self):
        """Close database connection"""
        self.db.close()
        logger.info("Database connection closed")
