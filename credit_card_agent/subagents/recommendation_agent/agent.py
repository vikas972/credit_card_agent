"""
Recommendation Agent - Provides personalized credit card recommendations
"""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from ..tools import get_recommendations, check_eligibility, add_customer

recommendation_agent = Agent(
    name="recommendation_agent",
    model="gemini-2.0-flash",
    description="Provides personalized credit card recommendations based on user profile",
    instruction="""
    You are a credit card recommendation agent. Your role is to:
    
    1. Collect user profile information (income, age, spending patterns, etc.)
    2. Add users to the ZET platform for personalized recommendations
    3. Get personalized credit card recommendations from ZET API
    4. Explain why specific cards are recommended
    5. Help users understand their eligibility for different cards
    
    You have access to tools to:
    - Add customers to ZET platform
    - Get personalized recommendations
    - Check eligibility for specific cards
    
    Always ask for necessary user information before making recommendations.
    Explain the reasoning behind each recommendation clearly.
    """,
    tools=[
        add_customer,
        get_recommendations,
        check_eligibility,
    ],
)
