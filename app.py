"""
Main application entry point for the RAG AI Assistant.
"""
import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

import argparse
from dotenv import load_dotenv

from src.application.container import AppContainer
from src.interface import ChatInterface

def load_environment():
    """Load environment variables."""
    # Load .env file if it exists
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Load .env.example and remind user to create .env
        example_env_path = Path(__file__).parent / ".env.example"
        if example_env_path.exists():
            load_dotenv(example_env_path)
            print("⚠️  Using .env.example - please copy it to .env and add your API keys!")
        else:
            print("⚠️  No .env file found. Please create one with your API keys.")


def load_auth_users():
    """Load authentication users from environment variables."""
    auth_dict = {}
    
    # Load from environment variable (format: "user1:pass1,user2:pass2")
    auth_string = os.getenv("GRADIO_AUTH_USERS", "")
    
    if auth_string:
        for user_pass in auth_string.split(","):
            if ":" in user_pass:
                username, password = user_pass.strip().split(":", 1)
                auth_dict[username] = password
    
    # If no users found in env, use default (for development only)
    if not auth_dict:
        print("⚠️  No GRADIO_AUTH_USERS found in environment. Using default credentials.")
        print("⚠️  Default: admin / admin123 (NOT for production!)")
        auth_dict = {"admin": "admin123"}
    
    return auth_dict


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="RAG AI Assistant Integration")
    parser.add_argument("--host", default="localhost", help="Host to run the interface on")
    parser.add_argument("--port", default=int(os.getenv("PORT", 7860)), type=int, help="Port to run the interface on")
    parser.add_argument("--model", default="llama3.2:3b", help="Model to use (Ollama or Google Gemini)")
    parser.add_argument("--temperature", default=0.7, type=float, help="Temperature for the model")
    parser.add_argument("--use-google", action="store_true", help="Use Google Gemini instead of Ollama")
    parser.add_argument("--share", action="store_true", help="Create a public Gradio link")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--no-auth", action="store_true", help="Disable authentication (for local development)")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_environment()
    
    # Load authentication users
    auth_users = None if args.no_auth else load_auth_users()
    
    print("🚀 Starting RAG AI Assistant...")
    print(f"📍 Host: {args.host}:{args.port}")
    print(f"🤖 Model: {args.model}")
    print(f"🔷 Provider: {'Google Gemini' if args.use_google else 'Ollama'}")
    print(f"🌡️  Temperature: {args.temperature}")
    print(f"🔒 Authentication: {'Disabled' if args.no_auth else 'Enabled'}")
   
   
    try:
        # Get Google API key if using Google
        google_api_key = os.getenv("GOOGLE_API_KEY") if args.use_google else None
        
        if args.use_google and not google_api_key:
            raise ValueError("❌ GOOGLE_API_KEY not found in environment variables. Please add it to your .env file.")
        
        # Get Ollama URL from environment or use default
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        
        # Create dependency injection container
        container = AppContainer(
            model_name=args.model,
            temperature=args.temperature,
            chroma_dir="./chroma_db",
            ollama_url=ollama_url,
            google_api_key=google_api_key,
            use_google=args.use_google,
            chunk_size=1000,
            chunk_overlap=200,
            rag_top_k=4,
            rag_min_score=0.0,
            memory_window=10
        )
        
        # Create the chat interface with injected services
        print("🎨 Creating chat interface...")
        chat_interface = ChatInterface(
            document_service=container.document_service,
            rag_service=container.rag_service,
            chat_service=container.chat_service,
            title="🤖 RAG AI Assistant with DDD Architecture",
            auth_users=auth_users
        )
        
        print("✅ Interface created successfully!")
        
        # Launch the interface
        print("\n" + "="*60)
        print("🎉 RAG AI Assistant is ready!")
        print("="*60)
        print(f"🌐 Access the interface at: http://{args.host}:{args.port}")
        
        if auth_users:
            print("\n🔐 Authentication enabled:")
            print(f"   Users configured: {len(auth_users)}")
            print("   Please login to access the application")
        
        print("\n💡 Tips:")
        print("- Upload documents in the 'Document Management' tab")
        print("- Search documents to test RAG retrieval")
        print("- Start chatting with AI that uses your documents")
        print("- Use Ctrl+C to stop the application")
        print("="*60)
        
        # Launch the Gradio interface
        chat_interface.launch(
            server_name=args.host,
            server_port=args.port,
            share=args.share,
            debug=args.debug
        )
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down RAG AI Assistant...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
