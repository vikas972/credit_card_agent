"""
Main entry point for the Credit Card Agent system
Simplified credit card recommendation system with ZET API integration
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to demonstrate the credit card agent system"""
    
    print("🚀 Credit Card Agent System - ZET API Integration")
    print("=" * 60)
    
    # Check if ZET API is configured
    zet_api_key = os.getenv("ZET_API_KEY")
    if not zet_api_key:
        print("⚠️  ZET_API_KEY not found in environment variables")
        print("Please set ZET_API_KEY in your .env file to use the full functionality")
        print("For demo purposes, some features may be limited")
        print()
    
    try:
        from credit_card_agent.agent import root_agent
        
        print("✅ Credit Card Agent initialized successfully")
        print("\n📋 Available Features:")
        print("  • Credit card advice and guidance")
        print("  • Personalized recommendations")
        print("  • Eligibility checking")
        print("  • Application support")
        print("  • Lead status tracking")
        
        print("\n🎯 Customer Journey:")
        print("  1. Initial consultation and advice")
        print("  2. Profile creation and data collection")
        print("  3. Personalized recommendations")
        print("  4. Eligibility verification")
        print("  5. Application process")
        print("  6. Status tracking and updates")
        
        print("\n💡 Example Queries:")
        print("  • 'I need advice on choosing a credit card'")
        print("  • 'Find me travel credit cards for my profile'")
        print("  • 'Check my eligibility for HDFC credit cards'")
        print("  • 'Help me apply for a credit card'")
        print("  • 'What's the status of my application?'")
        
        print("\n🎉 Credit Card Agent System Ready!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}")
        print(f"❌ Initialization failed: {str(e)}")

def interactive_mode():
    """Interactive mode for testing the agent"""
    
    print("\n🎮 Interactive Mode - Credit Card Agent")
    print("Type 'quit' to exit, 'help' for commands")
    print("-" * 50)
    
    try:
        from credit_card_agent.agent import root_agent
        
        while True:
            try:
                user_input = input("\n💬 Enter your query: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    print_help()
                    continue
                
                if not user_input:
                    continue
                
                # Process the query using the agent
                # Note: In a real implementation, you would call the agent's process method
                print(f"\n🤖 Processing: {user_input}")
                print("(In a real implementation, this would call the agent)")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                
    except ImportError as e:
        print(f"❌ Failed to import agent: {str(e)}")

def print_help():
    """Print help information"""
    print("\n📖 Available Commands:")
    print("  • 'I need advice on credit cards' - Get general advice")
    print("  • 'Find me travel credit cards' - Get recommendations")
    print("  • 'Check my eligibility for [card]' - Check eligibility")
    print("  • 'Help me apply for a credit card' - Application support")
    print("  • 'What's my application status?' - Check status")
    print("  • 'help' - Show this help message")
    print("  • 'quit' - Exit the program")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()