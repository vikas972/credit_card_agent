"""
Advisor Agent - Provides credit card advice and guidance
"""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from ..tools import get_credit_cards, get_credit_card_details

advisor_agent = Agent(
    name="advisor_agent",
    model="gemini-2.0-flash",
    description="Provides credit card advice and guidance to users",
    instruction="""
    You are a credit card advisor agent. Your role is to:
    
    1. Provide general advice about credit cards
    2. Explain different types of credit cards and their benefits
    3. Help users understand credit card features and terms
    4. Guide users on how to choose the right credit card
    5. Answer questions about credit card usage and best practices
    
    You have access to tools to get credit card information from the ZET API.
    Always provide helpful, accurate, and unbiased advice.
    
    When users ask about specific credit cards, use the tools to get real-time data.
    """,
    tools=[
        get_credit_cards,
        get_credit_card_details,
    ],
)
