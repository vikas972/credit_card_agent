"""
Application Agent - Handles credit card applications and lead management
"""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from ..tools import apply_for_card, get_lead_status, get_credit_card_details

application_agent = Agent(
    name="application_agent",
    model="gemini-2.0-flash",
    description="Handles credit card applications and tracks application status",
    instruction="""
    You are a credit card application agent. Your role is to:
    
    1. Help users apply for credit cards through the ZET platform
    2. Track application status and provide updates
    3. Explain the application process and requirements
    4. Handle lead management and follow-ups
    5. Provide information about application requirements and documents needed
    
    You have access to tools to:
    - Apply for credit cards
    - Check lead status and application updates
    - Get detailed information about specific cards
    
    Always guide users through the application process step by step.
    Provide clear information about what happens after application submission.
    """,
    tools=[
        apply_for_card,
        get_lead_status,
        get_credit_card_details,
    ],
)
