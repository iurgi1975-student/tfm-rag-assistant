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

from src.agent import RAGAgent
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


def create_agent(api_key=None, model_name="gpt-5", temperature=0.7):
    """Create and configure the RAG agent."""
    try:
        agent = RAGAgent(
            api_key=api_key,
            model_name=model_name,
            temperature=temperature,
            max_tokens=4000,
            memory_window=10
        )
        return agent
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        print("Make sure you have set your OPENAI_API_KEY in the .env file")
        sys.exit(1)


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="RAG AI Assistant Integration")
    parser.add_argument("--host", default="0.0.0.0", help="Host to run the interface on")
    parser.add_argument("--port", default=int(os.getenv("PORT", 7860)), type=int, help="Port to run the interface on")
    parser.add_argument("--model", default="gpt-5", help="OpenAI model to use")
    parser.add_argument("--temperature", default=0.7, type=float, help="Temperature for the model")
    parser.add_argument("--share", action="store_true", help="Create a public Gradio link")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_environment()
    
    print("🚀 Starting RAG AI Assistant...")
    print(f"📍 Host: {args.host}:{args.port}")
    print(f"🤖 Model: {args.model}")
    print(f"🌡️  Temperature: {args.temperature}")
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables!")
        print("Please set your OpenAI API key in the .env file")
        sys.exit(1)
    
    # Create the RAG agent
    print("🧠 Initializing RAG Agent...")
    agent = create_agent(
        api_key=api_key,
        model_name=args.model,
        temperature=args.temperature
    )
    
    print("✅ RAG Agent initialized successfully!")
    
    # Create the chat interface
    print("🎨 Creating chat interface...")
    chat_interface = ChatInterface(
        agent=agent,
        title="🤖 RAG AI Assistant with LangChain + Langflow"
    )
    
    print("✅ Interface created successfully!")
    
    # Launch the interface
    print("\n" + "="*60)
    print("🎉 RAG AI Assistant is ready!")
    print("="*60)
    print(f"🌐 Access the interface at: http://{args.host}:{args.port}")
    
    print("\n💡 Tips:")
    print("- Upload documents in the 'Document Management' tab")
    print("- Start chatting in the 'Chat' tab")
    print("- The AI will use your documents to provide better answers")
    print("- Use Ctrl+C to stop the application")
    print("="*60)
    
    try:
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
        print(f"❌ Error launching interface: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
