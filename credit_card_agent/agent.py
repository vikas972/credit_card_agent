"""
Main Credit Card Agent - Orchestrates the multi-agent system
Entry point for the credit card recommendation system
"""

import logging
from typing import Dict, Any, Optional
from google.adk.agents import Agent

from .subagents.orchestrator.agent import OrchestratorAgent
from .subagents.intent.agent import IntentAgent
from .subagents.data_ingestion.agent import DataIngestionAgent
from .subagents.eligibility_check.agent import EligibilityCheckAgent
from .subagents.recommendation.agent import RecommendationAgent
from .subagents.comparison_analysis.agent import ComparisonAnalysisAgent
from .subagents.explainer.agent import ExplainerAgent
from .subagents.response_generation.agent import ResponseGenerationAgent
from .models import UserQuery, UserProfile, AgentResponse, IntentType

logger = logging.getLogger(__name__)

# ADK requires this to be available as root_agent
root_agent = None


class CreditCardAgent(Agent):
    """
    Main credit card agent that orchestrates the multi-agent system
    for intelligent credit card recommendations and comparisons.
    """
    
    def __init__(self, **kwargs):
        # Extract name from kwargs if present
        name = kwargs.pop('name', 'credit_card_agent')
        # Set a default model for ADK compatibility
        if 'model' not in kwargs:
            kwargs['model'] = 'gemini-2.0-flash'
        super().__init__(name=name, **kwargs)
        
        # Initialize sub-agents as private attributes
        self._orchestrator = OrchestratorAgent(**kwargs)
        self._intent_agent = IntentAgent(**kwargs)
        self._data_ingestion_agent = DataIngestionAgent(**kwargs)
        self._eligibility_agent = EligibilityCheckAgent(**kwargs)
        self._recommendation_agent = RecommendationAgent(**kwargs)
        self._comparison_agent = ComparisonAnalysisAgent(**kwargs)
        self._explainer_agent = ExplainerAgent(**kwargs)
        self._response_agent = ResponseGenerationAgent(**kwargs)
        
        logger.info("Credit Card Agent initialized with all sub-agents")
    
    def process_query(self, query_text: str, user_profile: Optional[UserProfile] = None) -> AgentResponse:
        """
        Process user query and return recommendations
        
        Args:
            query_text: User's natural language query
            user_profile: Optional user profile data
            
        Returns:
            AgentResponse with recommendations or error
        """
        try:
            logger.info(f"Processing query: {query_text[:100]}...")
            
            # Step 1: Classify intent
            user_query = UserQuery(
                query_text=query_text,
                user_profile=user_profile
            )
            
            classified_query = self._intent_agent.process_query(user_query)
            logger.info(f"Classified intent: {classified_query.intent}")
            
            # Step 2: Process through orchestrator
            response = self._orchestrator.process_user_query(classified_query)
            
            if response.success:
                logger.info("Query processed successfully")
            else:
                logger.error(f"Query processing failed: {response.error}")
            
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return AgentResponse(
                success=False,
                error=f"Internal error: {str(e)}",
                trace_id="error"
            )
    
    def get_recommendations(self, user_profile: UserProfile, intent: Optional[IntentType] = None) -> AgentResponse:
        """
        Get credit card recommendations for a user profile
        
        Args:
            user_profile: User's profile data
            intent: Optional specific intent (travel, cashback, etc.)
            
        Returns:
            AgentResponse with recommendations
        """
        try:
            logger.info(f"Getting recommendations for user profile")
            
            # Create query from profile
            query = UserQuery(
                query_text=f"Find credit cards for {user_profile.employment} user with ₹{user_profile.net_monthly_income:,} monthly income",
                user_profile=user_profile,
                intent=intent
            )
            
            return self.process_query(query.query_text, user_profile)
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return AgentResponse(
                success=False,
                error=f"Failed to generate recommendations: {str(e)}",
                trace_id="error"
            )
    
    def compare_cards(self, card_a_id: str, card_b_id: str, user_profile: UserProfile) -> AgentResponse:
        """
        Compare two specific credit cards
        
        Args:
            card_a_id: ID of first card
            card_b_id: ID of second card
            user_profile: User's profile data
            
        Returns:
            AgentResponse with comparison
        """
        try:
            logger.info(f"Comparing cards: {card_a_id} vs {card_b_id}")
            
            # Get card data
            card_a = self._data_ingestion_agent.get_card_by_id(card_a_id)
            card_b = self._data_ingestion_agent.get_card_by_id(card_b_id)
            
            if not card_a or not card_b:
                return AgentResponse(
                    success=False,
                    error="One or both cards not found",
                    trace_id="error"
                )
            
            # Perform comparison
            comparison = self._comparison_agent.compare_cards(card_a, card_b, user_profile)
            
            # Generate response
            response = self._response_agent.generate_comparison_response(
                comparison, user_profile, "comparison_trace"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Card comparison failed: {str(e)}")
            return AgentResponse(
                success=False,
                error=f"Comparison failed: {str(e)}",
                trace_id="error"
            )
    
    def get_card_details(self, card_id: str) -> AgentResponse:
        """
        Get detailed information about a specific card
        
        Args:
            card_id: ID of the card
            
        Returns:
            AgentResponse with card details
        """
        try:
            logger.info(f"Getting details for card: {card_id}")
            
            card = self._data_ingestion_agent.get_card_by_id(card_id)
            
            if not card:
                return AgentResponse(
                    success=False,
                    error="Card not found",
                    trace_id="error"
                )
            
            return AgentResponse(
                success=True,
                data=card,
                trace_id="card_details"
            )
            
        except Exception as e:
            logger.error(f"Card details retrieval failed: {str(e)}")
            return AgentResponse(
                success=False,
                error=f"Failed to get card details: {str(e)}",
                trace_id="error"
            )
    
    def search_cards(self, filters: Dict[str, Any]) -> AgentResponse:
        """
        Search cards based on filters
        
        Args:
            filters: Search filters (issuer, tier, etc.)
            
        Returns:
            AgentResponse with matching cards
        """
        try:
            logger.info(f"Searching cards with filters: {filters}")
            
            cards = self._data_ingestion_agent.search_cards(filters)
            
            return AgentResponse(
                success=True,
                data={
                    "cards": cards,
                    "count": len(cards),
                    "filters_applied": filters
                },
                trace_id="search"
            )
            
        except Exception as e:
            logger.error(f"Card search failed: {str(e)}")
            return AgentResponse(
                success=False,
                error=f"Search failed: {str(e)}",
                trace_id="error"
            )
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all sub-agents
        
        Returns:
            Dictionary with agent status information
        """
        try:
            status = {
                "main_agent": "active",
                "sub_agents": {
                    "orchestrator": "active",
                    "intent": "active",
                    "data_ingestion": "active",
                    "eligibility_check": "active",
                    "recommendation": "active",
                    "comparison_analysis": "active",
                    "explainer": "active",
                    "response_generation": "active"
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the agent system
        
        Returns:
            Health status information
        """
        try:
            # Test data ingestion
            data_status = self._data_ingestion_agent.get_cached_data()
            
            # Test intent classification
            test_query = UserQuery(query_text="Find travel credit cards")
            intent_result = self._intent_agent.process_query(test_query)
            
            health_status = {
                "overall_status": "healthy",
                "data_ingestion": "healthy" if data_status["success"] else "degraded",
                "intent_classification": "healthy" if intent_result.intent else "degraded",
                "timestamp": "2024-01-15T10:30:00Z"
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": "2024-01-15T10:30:00Z"
            }


# Set the root_agent for ADK - ADK expects an instance, not a class
root_agent = CreditCardAgent()
