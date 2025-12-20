"""
AI Agent implementation using LangChain with RAG capabilities.
"""
import os
from typing import List, Optional, Dict, Any, Union, Generator
from datetime import datetime

from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..rag import InMemoryVectorStore, RAGRetriever, DocumentProcessor


class RAGAgent:
    """AI Agent with RAG capabilities for document-aware conversations."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gpt-5",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        memory_window: int = 10
    ):
        """Initialize the RAG Agent."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=SecretStr(self.api_key),
            model=model_name,
            temperature=temperature,
            max_completion_tokens=max_tokens
        )
        
        # Initialize RAG components
        self.vector_store = InMemoryVectorStore(api_key=self.api_key)
        self.retriever = RAGRetriever(self.vector_store)
        self.doc_processor = DocumentProcessor()
        
        # Initialize conversation history storage
        self.chat_history: List[Union[HumanMessage, AIMessage]] = []
        self.memory_window = memory_window
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return """You are a helpful AI assistant with access to a knowledge base of documents. 
        You can answer questions using both your general knowledge and information from the provided documents.
        
        When answering questions:
        1. If relevant information is available in the provided context, prioritize it
        2. Clearly indicate when you're using information from the documents vs. your general knowledge
        3. Be concise but thorough in your responses
        4. If you cannot find relevant information in the documents, say so and provide what help you can from your general knowledge
        5. Always be helpful, accurate, and honest about the limitations of your knowledge
        
        Context from documents:
        {context}
        
        Current time: {current_time}"""
    
    def add_documents_from_processor(self, documents: List) -> int:
        """Add documents to the knowledge base."""
        if not documents:
            return 0
        
        self.vector_store.add_documents(documents)
        return len(documents)
    
    def clear_knowledge_base(self) -> None:
        """Clear all documents from the knowledge base."""
        self.vector_store.clear()
    
    def get_knowledge_base_info(self) -> Dict[str, Any]:
        """Get information about the current knowledge base."""
        return {
            "document_count": self.vector_store.get_document_count(),
            "has_documents": len(self.vector_store) > 0
        }
    
    def _get_relevant_context(self, query: str) -> str:
        """Get relevant context from the knowledge base."""
        if len(self.vector_store) == 0:
            return "No documents available in the knowledge base."
        
        return self.retriever.get_context(query, max_tokens=1500)
    
    def _get_trimmed_history(self) -> List[Union[HumanMessage, AIMessage]]:
        """Get conversation history trimmed to the memory window."""
        return trim_messages(
            self.chat_history,
            token_counter=len,  # Count messages, not tokens
            max_tokens=self.memory_window,
            strategy="last",
            start_on="human",
            include_system=False,  # System message is handled separately
            allow_partial=False
        )
    
    def chat(self, message: str, stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """Chat with the agent."""
        # Get relevant context from documents
        context = self._get_relevant_context(message)
        
        # Format the system prompt with context
        formatted_system_prompt = self._get_system_prompt().format(
            context=context,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Create the prompt with current context
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=formatted_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # Get chat history
        chat_history = self._get_trimmed_history()
        
        # Create the chain
        chain = prompt | self.llm
        
        # Get response
        if stream:
            def generator():
                response_stream = chain.stream({
                    "input": message,
                    "chat_history": chat_history
                })
                
                # Collect streaming response
                response_text = ""
                for chunk in response_stream:
                    content = str(chunk.content) if chunk.content else ""
                    if content:
                        response_text += content
                        yield content
                
                # Save to memory
                self.chat_history.append(HumanMessage(content=message))
                self.chat_history.append(AIMessage(content=response_text))
            
            return generator()
            
        else:
            response = chain.invoke({
                "input": message,
                "chat_history": chat_history
            })
            
            response_text = str(response.content) if response.content else ""
            
            # Save to memory
            self.chat_history.append(HumanMessage(content=message))
            self.chat_history.append(AIMessage(content=response_text))
            
            return response_text
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self.chat_history.clear()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history in a readable format."""
        messages = self.chat_history
        history = []
        
        for message in messages:
            if isinstance(message, HumanMessage):
                history.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                history.append({"role": "assistant", "content": message.content})
        
        return history
    
    def search_documents(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant documents."""
        if len(self.vector_store) == 0:
            return []
        
        docs = self.vector_store.similarity_search(query, k=k)
        
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })
        
        return results
