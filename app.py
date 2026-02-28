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


def load_auth_config():
    """
    Load authentication configuration from environment variables.
    
    Returns:
        Configuration string for role-based authentication
    
    Expected format: "username:password:role,username2:password2:role2"
    Example: "admin:admin123:admin,user:user123:user"
    """
    # Load from environment variable (new format with roles)
    auth_config = os.getenv("GRADIO_AUTH_USERS", "")
    
    if not auth_config:
        print("⚠️  No GRADIO_AUTH_USERS found in environment.")
        print("⚠️  Default user will be created:")
        print("      - admin / admin123 (Admin role - full access)")
        print("⚠️  NOT for production! Set GRADIO_AUTH_USERS in .env")
        # Return empty string to use defaults from InMemoryAuthRepository
        return ""
    
    return auth_config
# port_env = int(os.environ.get("PORT", 8080))
port = int(os.environ.get("PORT", 8080))

def main():
    """Main application entry point."""
# DEBUG: Logs al inicio
    print("="*60, file=sys.stderr, flush=True)
    print("🚀 STARTING RAG AI ASSISTANT", file=sys.stderr, flush=True)
    print(f"Python: {sys.version}", file=sys.stderr, flush=True)
    print(f"PORT env: {os.environ.get('PORT', 'NOT SET')}", file=sys.stderr, flush=True)
    print(f"Working dir: {os.getcwd()}", file=sys.stderr, flush=True)
    print("="*60, file=sys.stderr, flush=True)
    sys.stderr.flush()

    parser = argparse.ArgumentParser(description="RAG AI Assistant Integration")
    parser.add_argument("--host", default="localhost", help="Host to run the interface on")
    parser.add_argument("--port", default=port, type=int, help="Port to run the interface on")
    parser.add_argument("--model", default="gemini-2.5-flash", help="Model to use (Ollama or Google Gemini)")
    parser.add_argument("--temperature", default=0.7, type=float, help="Temperature for the model")
    parser.add_argument("--use-google", default=True, action="store_true", help="Use Google Gemini instead of Ollama")
    parser.add_argument("--share", default=False, help="Create a public Gradio link")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--no-auth", action="store_true", help="Disable authentication (for local development)")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_environment()
    
    # Load authentication configuration
    auth_config = None if args.no_auth else load_auth_config()
    
    print("🚀 Starting RAG AI Assistant...")
    print(f"📍 Host: {args.host}:{args.port}")
    print(f"🤖 Model: {args.model}")
    # print(f"🔷 Provider: {'Google Gemini' if args.use_google else 'Ollama'}")
    print(f"🔷 Provider: {'Google Gemini' }")
    print(f"🌡️  Temperature: {args.temperature}")
    print(f"🔒 Authentication: {'Disabled' if args.no_auth else 'Enabled (with role-based access)'}")
   
   
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
            memory_window=10,
            auth_users_config=auth_config,
            enable_authentication=not args.no_auth
        )
        
        # Create the chat interface with injected services
        print("🎨 Creating chat interface...")
        chat_interface = ChatInterface(
            document_service=container.document_service,
            rag_service=container.rag_service,
            chat_service=container.chat_service,
            authentication_service=container.authentication_service,
            title="🤖 RAG AI Assistant with DDD Architecture",
            auth_users=None  # Deprecated, using authentication_service now
        )
        
        print("✅ Interface created successfully!")
        
        # Launch the interface
        print("\n" + "="*60)
        print("🎉 RAG AI Assistant is ready!")
        print("="*60)
        print(f"🌐 Access the interface at: http://{args.host}:{args.port}")
        
        if not args.no_auth:
            print("\n🔐 Role-based Authentication enabled:")
            print("   👑 Admin role: Full access (chat + document management)")
            print("   👤 User role: Limited access (chat only)")
            print("   Please login to access the application")
            if not auth_config:
                print("\n   Default credentials (development only):")
                print("      admin / admin123 (Admin)")
        
        print("\n💡 Tips:")
        print("- Upload documents in the 'Document Management' tab (Admin only)")
        print("- Search documents to test RAG retrieval")
        print("- Start chatting with AI that uses your documents")
        print("- Use Ctrl+C to stop the application")
        print("="*60)
        
        # Launch the Gradio interface
        chat_interface.launch(
            server_name="0.0.0.0",
            server_port=port,
            share=False,
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
