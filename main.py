"""
Main entry point for the Credit Card Agent system
Demonstrates the multi-agent credit card recommendation workflow
"""

import os
import logging
from dotenv import load_dotenv

from credit_card_agent.agent import CreditCardAgent
from credit_card_agent.models import UserProfile, IntentType

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
    
    print("🚀 Credit Card Agent System - Multi-Agent Architecture")
    print("=" * 60)
    
    try:
        # Initialize the credit card agent
        agent = CreditCardAgent()
        
        # Check agent health
        health_status = agent.health_check()
        print(f"✅ Agent Status: {health_status['overall_status']}")
        
        # Example 1: Process a natural language query
        print("\n📝 Example 1: Natural Language Query")
        print("-" * 40)
        
        query = "I'm looking for a travel credit card with good rewards and lounge access"
        response = agent.process_query(query)
        
        if response.success:
            print(f"✅ Query processed successfully")
            print(f"📊 Found {len(response.data.get('recommendations', []))} recommendations")
            
            # Display top recommendation
            recommendations = response.data.get('recommendations', [])
            if recommendations:
                top_rec = recommendations[0]
                print(f"🏆 Top Recommendation: {top_rec['card_name']}")
                print(f"   Issuer: {top_rec['issuer']}")
                print(f"   Score: {top_rec['score']}/100")
                print(f"   Rationale: {top_rec['rationale']}")
        else:
            print(f"❌ Query failed: {response.error}")
        
        # Example 2: Get recommendations with user profile
        print("\n👤 Example 2: User Profile-Based Recommendations")
        print("-" * 50)
        
        user_profile = UserProfile(
            age=32,
            employment="salaried",
            net_monthly_income=80000,
            credit_score=780,
            city="Mumbai",
            monthly_spending={
                "groceries": 15000,
                "dining": 8000,
                "travel_flights_hotels": 5000,
                "fuel": 4000,
                "online_shopping_ecommerce": 20000,
                "utility_bills": 6000,
                "other_retail": 12000
            }
        )
        
        recommendations_response = agent.get_recommendations(
            user_profile, 
            intent=IntentType.FIND_TRAVEL_CARD
        )
        
        if recommendations_response.success:
            print(f"✅ Generated {len(recommendations_response.data.get('recommendations', []))} personalized recommendations")
            
            # Display all recommendations
            for i, rec in enumerate(recommendations_response.data.get('recommendations', []), 1):
                print(f"\n{i}. {rec['card_name']} ({rec['issuer']})")
                print(f"   Tier: {rec['tier']}")
                print(f"   Annual Fee: ₹{rec['annual_fee']:,}")
                print(f"   Score: {rec['score']}/100")
                print(f"   Why: {rec['rationale']}")
        else:
            print(f"❌ Recommendations failed: {recommendations_response.error}")
        
        # Example 3: Search cards with filters
        print("\n🔍 Example 3: Card Search with Filters")
        print("-" * 40)
        
        search_filters = {
            "issuer": "HDFC Bank",
            "tier": "Entry-Level"
        }
        
        search_response = agent.search_cards(search_filters)
        
        if search_response.success:
            cards = search_response.data.get('cards', [])
            print(f"✅ Found {len(cards)} cards matching filters")
            
            for card in cards[:3]:  # Show first 3 results
                general_info = card.get('general_info', {})
                print(f"   • {general_info.get('card_name', 'Unknown')} - {general_info.get('tier', 'Unknown')}")
        else:
            print(f"❌ Search failed: {search_response.error}")
        
        # Example 4: Get agent status
        print("\n📊 Example 4: Agent System Status")
        print("-" * 35)
        
        status = agent.get_agent_status()
        print(f"Main Agent: {status['main_agent']}")
        print("Sub-agents:")
        for agent_name, agent_status in status['sub_agents'].items():
            print(f"  • {agent_name}: {agent_status}")
        
        print("\n🎉 Credit Card Agent System Demo Completed!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        print(f"❌ Demo failed: {str(e)}")


def interactive_mode():
    """Interactive mode for testing the agent"""
    
    print("\n🎮 Interactive Mode - Credit Card Agent")
    print("Type 'quit' to exit, 'help' for commands")
    print("-" * 50)
    
    agent = CreditCardAgent()
    
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
            
            # Process the query
            response = agent.process_query(user_input)
            
            if response.success:
                print(f"\n✅ Response:")
                recommendations = response.data.get('recommendations', [])
                
                if recommendations:
                    for i, rec in enumerate(recommendations, 1):
                        print(f"\n{i}. {rec['card_name']} ({rec['issuer']})")
                        print(f"   Score: {rec['score']}/100")
                        print(f"   Annual Fee: ₹{rec['annual_fee']:,}")
                        print(f"   Why: {rec['rationale']}")
                else:
                    print("No recommendations found for your query.")
            else:
                print(f"❌ Error: {response.error}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def print_help():
    """Print help information"""
    print("\n📖 Available Commands:")
    print("  • Natural language queries (e.g., 'Find travel credit cards')")
    print("  • Specific requests (e.g., 'Show me HDFC credit cards')")
    print("  • Comparison requests (e.g., 'Compare premium cards')")
    print("  • 'help' - Show this help message")
    print("  • 'quit' - Exit the program")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()
