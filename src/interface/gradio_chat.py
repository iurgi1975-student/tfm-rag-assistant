"""
Gradio interface for the ChatGPT-like AI agent.
"""
import os
from typing import List, Tuple, Dict
import gradio as gr

from ..agent import RAGAgent
from ..rag import DocumentProcessor


class ChatInterface:
    """Gradio-based chat interface for the RAG agent."""
    
    def __init__(self, agent: RAGAgent, title: str = "AI Assistant with RAG"):
        self.agent = agent
        self.title = title
        self.doc_processor = DocumentProcessor()
        
    def process_uploaded_files(self, files: List[str]) -> str:
        """Process uploaded files and add them to the knowledge base."""
        if not files:
            return "No files uploaded."
        
        total_docs = 0
        processed_files = []
        
        for file_path in files:
            try:
                # Process the document
                documents = self.doc_processor.load_document(file_path)
                
                # Add to knowledge base
                self.agent.add_documents_from_processor(documents)
                
                total_docs += len(documents)
                processed_files.append(os.path.basename(file_path))
                
            except Exception as e:
                return f"Error processing {os.path.basename(file_path)}: {str(e)}"
        
        files_list = ", ".join(processed_files)
        return f"Successfully processed {len(processed_files)} file(s): {files_list}. Added {total_docs} document chunks to knowledge base."
    
    def add_text_to_knowledge_base(self, text: str) -> str:
        """Add text directly to the knowledge base."""
        if not text.strip():
            return "No text provided."
        
        try:
            documents = self.doc_processor.process_text_input(text, "manual_input")
            self.agent.add_documents_from_processor(documents)
            return f"Added text to knowledge base ({len(documents)} chunks)."
        except Exception as e:
            return f"Error adding text: {str(e)}"
    
    def clear_knowledge_base(self) -> str:
        """Clear the knowledge base."""
        self.agent.clear_knowledge_base()
        return "Knowledge base cleared."
    
    def clear_chat_history(self) -> Tuple[List[dict], str]:
        """Clear the chat history."""
        self.agent.clear_conversation_history()
        return [], "Chat history cleared."
    
    def get_knowledge_base_status(self) -> str:
        """Get the current status of the knowledge base."""
        info = self.agent.get_knowledge_base_info()
        return f"Documents in knowledge base: {info['document_count']}"
    
    def chat_response(self, message: str, history: List[dict]) -> Tuple[List[dict], str]:
        """Generate chat response."""
        if not message.strip():
            return history, ""
        
        try:
            # Get response from agent (ensuring we get a string, not a generator)
            response = self.agent.chat(message, stream=False)
            
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
            results = self.agent.search_documents(query, k=3)
            
            if not results:
                return "No relevant documents found."
            
            output = f"Found {len(results)} relevant document(s):\n\n"
            
            for i, result in enumerate(results, 1):
                metadata = result["metadata"]
                source = metadata.get("source", "Unknown")
                output += f"**Result {i}** (Source: {os.path.basename(source)})\n"
                output += f"{result['preview']}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error searching documents: {str(e)}"
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
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
        """
        
        with gr.Blocks(title=self.title, css=custom_css) as interface:
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
                            label="Upload Files (PDF, TXT, DOCX)",
                            file_count="multiple",
                            file_types=[".pdf", ".txt", ".docx"],
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
        
        return interface
    
    def launch(self, **kwargs):
        """Launch the Gradio interface."""
        interface = self.create_interface()
        return interface.launch(**kwargs)
