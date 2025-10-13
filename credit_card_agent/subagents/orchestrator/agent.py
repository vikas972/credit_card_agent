"""
OrchestratorAgent - Central coordinator for the credit card agent system
Manages workflow, state, and inter-agent communication
"""

import logging
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.models import LlmRequest
from google.adk.tools import BaseTool

from ...models import UserQuery, UserProfile, CreditCard, AgentResponse, IntentType
from ...tools import (
    CreditScoreCheckTool, 
    CardDataIngestionTool, 
    EligibilityRuleEngineTool,
    ComplianceGuardrailTool,
    RewardsCalculatorTool
)

logger = logging.getLogger(__name__)


class OrchestratorAgent(Agent):
    """
    Central orchestrator that manages the credit card recommendation workflow.
    Coordinates between all specialized agents to deliver personalized recommendations.
    """
    
    def __init__(self, **kwargs):
        name = kwargs.pop('name', 'orchestrator')
        super().__init__(name=name, **kwargs)
        self.tools = [
            CreditScoreCheckTool(),
            CardDataIngestionTool(),
            EligibilityRuleEngineTool(),
            ComplianceGuardrailTool(),
            RewardsCalculatorTool()
        ]
    
    def process_user_query(self, query: UserQuery) -> AgentResponse:
        """
        Main entry point for processing user queries
        
        Args:
            query: User's query with profile and intent
            
        Returns:
            AgentResponse with recommendations or error
        """
        try:
            trace_id = f"trace_{hash(query.query_text) % 1000000}"
            logger.info(f"Processing query with trace_id: {trace_id}")
            
            # Step 1: Get user profile (if not provided)
            if not query.user_profile:
                user_profile = self._get_user_profile(query)
            else:
                user_profile = query.user_profile
            
            # Step 2: Ingest credit card data
            cards_data = self._ingest_card_data()
            if not cards_data["success"]:
                return AgentResponse(
                    success=False,
                    error="Failed to load credit card data",
                    trace_id=self.trace_id
                )
            
            # Step 3: Filter eligible cards
            eligible_cards = self._filter_eligible_cards(user_profile, cards_data["data"])
            if not eligible_cards["success"]:
                return AgentResponse(
                    success=False,
                    error="Failed to filter eligible cards",
                    trace_id=self.trace_id
                )
            
            # Step 4: Generate recommendations
            recommendations = self._generate_recommendations(
                user_profile, 
                eligible_cards["data"], 
                query.intent
            )
            
            # Step 5: Format response
            response_data = self._format_response(recommendations, user_profile)
            
            return AgentResponse(
                success=True,
                data=response_data,
                trace_id=trace_id
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return AgentResponse(
                success=False,
                error=f"Internal error: {str(e)}",
                trace_id="unknown"
            )
    
    def _get_user_profile(self, query: UserQuery) -> UserProfile:
        """Extract or create user profile from query"""
        # In a real implementation, this would extract profile from query
        # or prompt user for missing information
        return UserProfile(
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
    
    def _ingest_card_data(self) -> Dict[str, Any]:
        """Ingest credit card data from external sources"""
        try:
            ingestion_tool = CardDataIngestionTool()
            result = ingestion_tool.execute(source="zetapp")
            return result
        except Exception as e:
            logger.error(f"Card data ingestion failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _filter_eligible_cards(self, user_profile: UserProfile, cards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Filter cards based on user eligibility"""
        try:
            eligibility_tool = EligibilityRuleEngineTool()
            user_profile_dict = user_profile.dict()
            result = eligibility_tool.execute(user_profile_dict, cards)
            return result
        except Exception as e:
            logger.error(f"Eligibility filtering failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_recommendations(self, user_profile: UserProfile, eligible_cards: List[Dict[str, Any]], intent: Optional[IntentType]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        try:
            recommendations = []
            
            for card_data in eligible_cards[:5]:  # Limit to top 5 for now
                # Calculate rewards value
                rewards_tool = RewardsCalculatorTool()
                rewards_result = rewards_tool.execute(card_data, user_profile.monthly_spending)
                
                if rewards_result["success"]:
                    recommendation = {
                        "card": card_data,
                        "rewards_analysis": rewards_result["data"],
                        "recommendation_score": self._calculate_recommendation_score(
                            card_data, 
                            user_profile, 
                            rewards_result["data"],
                            intent
                        ),
                        "rationale": self._generate_rationale(card_data, user_profile, intent)
                    }
                    recommendations.append(recommendation)
            
            # Sort by recommendation score
            recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
            return recommendations[:3]  # Return top 3
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return []
    
    def _calculate_recommendation_score(self, card: Dict[str, Any], user_profile: UserProfile, rewards_data: Dict[str, Any], intent: Optional[IntentType]) -> float:
        """Calculate recommendation score based on multiple factors"""
        try:
            score = 0.0
            
            # Base score from rewards value
            annual_rewards_value = rewards_data.get("annual_cashback_value", 0)
            score += min(annual_rewards_value / 1000, 10)  # Cap at 10 points
            
            # Intent-based scoring
            if intent == IntentType.FIND_TRAVEL_CARD:
                if "travel" in card.get("benefits", {}):
                    score += 5
            elif intent == IntentType.FIND_CASHBACK_CARD:
                if card.get("rewards", {}).get("base_rate", 0) > 1.0:
                    score += 3
            
            # Fee consideration
            annual_fee = card.get("fees", {}).get("annual_fee", {}).get("amount", 0)
            if annual_fee == 0:
                score += 2
            elif annual_rewards_value > annual_fee:
                score += 1
            
            return min(score, 20)  # Cap total score at 20
            
        except Exception as e:
            logger.error(f"Score calculation failed: {str(e)}")
            return 0.0
    
    def _generate_rationale(self, card: Dict[str, Any], user_profile: UserProfile, intent: Optional[IntentType]) -> str:
        """Generate rationale for why this card is recommended"""
        try:
            card_name = card.get("general_info", {}).get("card_name", "This card")
            annual_rewards = card.get("rewards", {}).get("redemption", {}).get("cashback_value_per_point", 0.5)
            
            rationale_parts = []
            
            # Rewards rationale
            if annual_rewards > 0.5:
                rationale_parts.append(f"{card_name} offers excellent rewards value")
            
            # Intent-based rationale
            if intent == IntentType.FIND_TRAVEL_CARD:
                if "lounge_access" in str(card.get("benefits", {})):
                    rationale_parts.append("perfect for frequent travelers with lounge access")
            elif intent == IntentType.FIND_CASHBACK_CARD:
                base_rate = card.get("rewards", {}).get("base_rate", 0)
                if base_rate > 1.0:
                    rationale_parts.append(f"provides {base_rate}% cashback on all purchases")
            
            # Spending pattern rationale
            if user_profile.monthly_spending.get("online_shopping_ecommerce", 0) > 10000:
                rationale_parts.append("great for your high online shopping spend")
            
            return ". ".join(rationale_parts) + "." if rationale_parts else f"{card_name} matches your profile well."
            
        except Exception as e:
            logger.error(f"Rationale generation failed: {str(e)}")
            return "This card is recommended based on your profile."
    
    def _format_response(self, recommendations: List[Dict[str, Any]], user_profile: UserProfile) -> Dict[str, Any]:
        """Format the final response for the user"""
        try:
            formatted_recommendations = []
            
            for i, rec in enumerate(recommendations, 1):
                card = rec["card"]
                rewards = rec["rewards_analysis"]
                
                formatted_rec = {
                    "rank": i,
                    "card_name": card.get("general_info", {}).get("card_name"),
                    "issuer": card.get("general_info", {}).get("issuer"),
                    "tier": card.get("general_info", {}).get("tier"),
                    "annual_fee": card.get("fees", {}).get("annual_fee", {}).get("amount", 0),
                    "annual_rewards_value": round(rewards.get("annual_cashback_value", 0), 2),
                    "net_value": round(rewards.get("annual_cashback_value", 0) - card.get("fees", {}).get("annual_fee", {}).get("amount", 0), 2),
                    "rationale": rec["rationale"],
                    "apply_link": card.get("application_details", {}).get("deep_link_url"),
                    "score": round(rec["recommendation_score"], 2)
                }
                formatted_recommendations.append(formatted_rec)
            
            return {
                "user_profile": {
                    "age": user_profile.age,
                    "employment": user_profile.employment,
                    "monthly_income": user_profile.net_monthly_income,
                    "credit_score": user_profile.credit_score,
                    "city": user_profile.city
                },
                "recommendations": formatted_recommendations,
                "total_eligible_cards": len(recommendations),
                "analysis_timestamp": "2024-01-15T10:30:00Z"
            }
            
        except Exception as e:
            logger.error(f"Response formatting failed: {str(e)}")
            return {"error": "Failed to format response"}
    
    def compare_cards(self, card_a_id: str, card_b_id: str, user_profile: UserProfile) -> AgentResponse:
        """
        Compare two specific credit cards
        
        Args:
            card_a_id: ID of first card to compare
            card_b_id: ID of second card to compare
            user_profile: User's profile data
            
        Returns:
            AgentResponse with detailed comparison
        """
        try:
            # This would be implemented to fetch specific cards and perform detailed comparison
            # For now, return a placeholder response
            return AgentResponse(
                success=True,
                data={"message": "Card comparison feature coming soon"},
                trace_id=self.trace_id or "unknown"
            )
        except Exception as e:
            logger.error(f"Card comparison failed: {str(e)}")
            return AgentResponse(
                success=False,
                error=f"Comparison failed: {str(e)}",
                trace_id=self.trace_id or "unknown"
            )
