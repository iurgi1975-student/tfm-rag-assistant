"""
Gradio interface for the ChatGPT-like AI agent with authentication.
"""
import os
from typing import List, Tuple, Dict, Optional
import gradio as gr

from ..application.services.document_service import DocumentService
from ..application.services.rag_service import RAGService
from ..application.services.chat_service import ChatService


class ChatInterface:
    """Gradio-based chat interface for the RAG agent with login system."""
    
    def __init__(
        self, 
        document_service: DocumentService,
        rag_service: RAGService,
        chat_service: ChatService,
        title: str = "AI Assistant with RAG",
        auth_users: Optional[Dict[str, str]] = None
    ):
        self.document_service = document_service
        self.rag_service = rag_service
        self.chat_service = chat_service
        self.title = title
        self.auth_users = auth_users
    def process_uploaded_files(self, files: List[str]) -> str:
        """Process uploaded files and add them to the knowledge base."""
        if not files:
            return "No files uploaded."
        
        total_docs = 0
        processed_files = []
        
        for file_path in files:
            try:
                count = self.document_service.ingest_document(file_path)
                total_docs += count
                processed_files.append(os.path.basename(file_path))
            except Exception as e:
                return f"Error processing {os.path.basename(file_path)}: {str(e)}"
        
        files_list = ", ".join(processed_files)
        return f"Successfully processed {len(processed_files)} file(s): {files_list}. Added {total_docs} document(s) to knowledge base."
    
    def add_text_to_knowledge_base(self, text: str) -> str:
        """Add text directly to the knowledge base."""
        if not text.strip():
            return "No text provided."
        
        try:
            count = self.document_service.ingest_text(text, "manual_input")
            return f"Added text to knowledge base ({count} document)."
        except Exception as e:
            return f"Error adding text: {str(e)}"
    
    def clear_knowledge_base(self) -> str:
        """Clear the knowledge base."""
        self.document_service.clear_knowledge_base()
        return "Knowledge base cleared."
    
    def clear_chat_history(self) -> Tuple[List[dict], str]:
        """Clear the chat history."""
        self.chat_service.clear_history()
        return [], "Chat history cleared."
    
    def get_knowledge_base_status(self) -> str:
        """Get the current status of the knowledge base."""
        stats = self.document_service.get_document_stats()
        return f"Documents in knowledge base: {stats['total_documents']}"
    
    def chat_response(self, message: str, history: List[dict]) -> Tuple[List[dict], str]:
        """Generate chat response."""
        if not message.strip():
            return history, ""
        
        try:
            # Get response from chat service
            response = self.chat_service.chat(message, stream=False, use_rag=True)
            
            # Ensure response is a string
            if not isinstance(response, str):
                response = str(response)
            
            # Update history with proper message format for gradio messages type
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response})
            
            return history, ""
            
        except Exception as e:
            error_response = f"Error: {str(e)}"
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": error_response})
            return history, ""
    
    def search_documents(self, query: str) -> str:
        """Search documents in the knowledge base."""
        if not query.strip():
            return "Please enter a search query."
        
        try:
            # Use RAGService instead of agent
            results = self.rag_service.search(query, k=3)
            
            if not results:
                return "No relevant documents found."
            
            output = f"Found {len(results)} relevant document(s):\n\n"
            
            for i, result in enumerate(results, 1):
                source = result.chunk.metadata.get("source", "Unknown")
                preview = result.chunk.content[:200] + "..." if len(result.chunk.content) > 200 else result.chunk.content
                output += f"**Result {i}** (Score: {result.similarity_score:.2f}, Source: {os.path.basename(source)})\n"
                output += f"{preview}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error searching documents: {str(e)}"
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface with optional login."""
        custom_css = """
        .chat-container {
            height: 500px;
        }
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        .login-container {
            max-width: 400px;
            margin: 50px auto;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        """
        
        with gr.Blocks(title=self.title, css=custom_css) as interface:
            # If authentication is enabled, create login screen
            if self.auth_users:
                with gr.Column(visible=True, elem_classes=["login-container"]) as login_screen:
                    gr.Markdown(f"# 🔐 Login - {self.title}")
                    gr.Markdown("Please enter your credentials to access the application")
                    
                    username_input = gr.Textbox(
                        label="Username",
                        placeholder="Enter your username",
                        type="text"
                    )
                    password_input = gr.Textbox(
                        label="Password",
                        placeholder="Enter your password",
                        type="password"
                    )
                    login_btn = gr.Button("🔓 Login", variant="primary", size="lg")
                    login_status = gr.Markdown("", visible=True)
                
                with gr.Column(visible=False) as main_app:
                    logout_btn = gr.Button("🚪 Logout", variant="secondary", size="sm")
                    self._create_main_interface()
                
                def handle_login(username, password):
                    if username in self.auth_users and self.auth_users[username] == password:
                        return {
                            login_screen: gr.Column(visible=False),
                            main_app: gr.Column(visible=True),
                            login_status: gr.Markdown(""),
                            username_input: "",
                            password_input: ""
                        }
                    else:
                        return {
                            login_screen: gr.Column(visible=True),
                            main_app: gr.Column(visible=False),
                            login_status: gr.Markdown("❌ Invalid credentials. Please try again."),
                            username_input: username,
                            password_input: ""
                        }
                
                def handle_logout():
                    return {
                        login_screen: gr.Column(visible=True),
                        main_app: gr.Column(visible=False),
                        login_status: gr.Markdown("✅ Logged out successfully. Please login again."),
                        username_input: "",
                        password_input: ""
                    }
                
                login_btn.click(
                    handle_login,
                    inputs=[username_input, password_input],
                    outputs=[login_screen, main_app, login_status, username_input, password_input]
                )
                
                password_input.submit(
                    handle_login,
                    inputs=[username_input, password_input],
                    outputs=[login_screen, main_app, login_status, username_input, password_input]
                )
                
                logout_btn.click(
                    handle_logout,
                    outputs=[login_screen, main_app, login_status, username_input, password_input]
                )
            else:
                # No authentication, show main interface directly
                self._create_main_interface()
        
        return interface
    
    def _create_main_interface(self):
        """Create the main application interface."""
        gr.Markdown(f"# {self.title}")
        gr.Markdown("Upload documents to enhance the AI's knowledge, then chat with your intelligent assistant!")
        
        with gr.Tab("💬 Chat"):
            with gr.Row():
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(
                        type="messages",
                        label="Conversation",
                        height=500,
                        elem_classes=["chat-container"]
                    )
                    
                    with gr.Row():
                        msg = gr.Textbox(
                            placeholder="Type your message here...",
                            label="Message",
                            scale=4
                        )
                        submit_btn = gr.Button("Send", variant="primary", scale=1)
                    
                    clear_btn = gr.Button("Clear Chat History", variant="secondary")
                
                with gr.Column(scale=1):
                    status_display = gr.Textbox(
                        label="Knowledge Base Status",
                        value=self.get_knowledge_base_status(),
                        interactive=False
                    )
                    
                    refresh_status_btn = gr.Button("Refresh Status")
        
        with gr.Tab("📄 Document Management"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Upload Documents")
                    file_upload = gr.File(
                        label="Upload Files (PDF)",
                        file_count="multiple",
                        file_types=[".pdf"],
                        elem_classes=["upload-area"]
                    )
                    upload_btn = gr.Button("Process Files", variant="primary")
                    upload_status = gr.Textbox(label="Upload Status", interactive=False)
                    
                    gr.Markdown("### Add Text Directly")
                    text_input = gr.Textbox(
                        label="Text to Add",
                        placeholder="Paste text content here...",
                        lines=5
                    )
                    add_text_btn = gr.Button("Add Text to Knowledge Base", variant="primary")
                    text_status = gr.Textbox(label="Text Addition Status", interactive=False)
                
                with gr.Column():
                    gr.Markdown("### Search Documents")
                    search_query = gr.Textbox(
                        label="Search Query",
                        placeholder="Enter search terms..."
                    )
                    search_btn = gr.Button("Search Documents", variant="primary")
                    search_results = gr.Textbox(
                        label="Search Results",
                        lines=10,
                        interactive=False
                    )
                    
                    gr.Markdown("### Knowledge Base Management")
                    clear_kb_btn = gr.Button("Clear Knowledge Base", variant="stop")
                    clear_kb_status = gr.Textbox(label="Clear Status", interactive=False)
        
        # Event handlers
        def submit_message(message, history):
            return self.chat_response(message, history)
        
        submit_btn.click(
            submit_message,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg]
        )
        
        msg.submit(
            submit_message,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg]
        )
        
        clear_btn.click(
            self.clear_chat_history,
            outputs=[chatbot, clear_btn]
        )
        
        upload_btn.click(
            self.process_uploaded_files,
            inputs=[file_upload],
            outputs=[upload_status]
        )
        
        add_text_btn.click(
            self.add_text_to_knowledge_base,
            inputs=[text_input],
            outputs=[text_status]
        )
        
        search_btn.click(
            self.search_documents,
            inputs=[search_query],
            outputs=[search_results]
        )
        
        clear_kb_btn.click(
            self.clear_knowledge_base,
            outputs=[clear_kb_status]
        )
        
        refresh_status_btn.click(
            self.get_knowledge_base_status,
            outputs=[status_display]
        )
        
        # Update status after file upload
        upload_btn.click(
            self.get_knowledge_base_status,
            outputs=[status_display]
        )
        
        add_text_btn.click(
            self.get_knowledge_base_status,
            outputs=[status_display]
        )
        
        clear_kb_btn.click(
            self.get_knowledge_base_status,
            outputs=[status_display]
        )
    
    def launch(self, **kwargs):
        """Launch the Gradio interface."""
        interface = self.create_interface()
        return interface.launch(**kwargs)
