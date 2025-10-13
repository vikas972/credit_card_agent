"""
RecommendationAgent - Ranks and selects best-fit credit cards
Takes eligible cards and ranks them based on user profile and intent
"""

import logging
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.tools import BaseTool

from ...models import UserProfile, IntentType, CardRecommendation
from ...tools import RewardsCalculatorTool

logger = logging.getLogger(__name__)


class RecommendationAgent(Agent):
    """
    Recommendation agent that ranks eligible credit cards
    and selects the top 3-4 best-fit options for the user.
    """
    
    def __init__(self, **kwargs):
        name = kwargs.pop('name', 'recommendation')
        super().__init__(name=name, **kwargs)
        self.tools = [RewardsCalculatorTool()]
        self._ranking_weights = self._load_ranking_weights()
    
    def generate_recommendations(self, user_profile: UserProfile, eligible_cards: List[Dict[str, Any]], intent: Optional[IntentType] = None) -> List[CardRecommendation]:
        """
        Generate personalized recommendations from eligible cards
        
        Args:
            user_profile: User's profile data
            eligible_cards: List of eligible credit cards
            intent: User's intent (travel, cashback, etc.)
            
        Returns:
            List of ranked card recommendations
        """
        try:
            recommendations = []
            
            for card in eligible_cards:
                recommendation = self._create_card_recommendation(card, user_profile, intent)
                if recommendation:
                    recommendations.append(recommendation)
            
            # Sort by recommendation score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
            # Return top 3-4 recommendations
            top_recommendations = recommendations[:4]
            
            logger.info(f"Generated {len(top_recommendations)} recommendations from {len(eligible_cards)} eligible cards")
            
            return top_recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return []
    
    def _create_card_recommendation(self, card: Dict[str, Any], user_profile: UserProfile, intent: Optional[IntentType]) -> Optional[CardRecommendation]:
        """Create a recommendation for a single card"""
        try:
            # Calculate rewards value
            rewards_tool = RewardsCalculatorTool()
            rewards_result = rewards_tool.execute(card, user_profile.monthly_spending)
            
            if not rewards_result["success"]:
                logger.warning(f"Failed to calculate rewards for card {card.get('card_id')}")
                return None
            
            rewards_data = rewards_result["data"]
            
            # Calculate recommendation score
            score = self._calculate_recommendation_score(card, user_profile, rewards_data, intent)
            
            # Generate rationale
            rationale = self._generate_recommendation_rationale(card, user_profile, rewards_data, intent)
            
            # Create recommendation object
            recommendation = CardRecommendation(
                card=card,
                score=score,
                rationale=rationale
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Failed to create recommendation for card {card.get('card_id')}: {str(e)}")
            return None
    
    def _calculate_recommendation_score(self, card: Dict[str, Any], user_profile: UserProfile, rewards_data: Dict[str, Any], intent: Optional[IntentType]) -> float:
        """Calculate comprehensive recommendation score"""
        try:
            score = 0.0
            
            # Rewards value score (40% weight)
            annual_rewards_value = rewards_data.get("annual_cashback_value", 0)
            rewards_score = min(annual_rewards_value / 1000, 20)  # Cap at 20 points
            score += rewards_score * 0.4
            
            # Fee efficiency score (25% weight)
            annual_fee = card.get("fees", {}).get("annual_fee", {}).get("amount", 0)
            if annual_fee == 0:
                fee_score = 15  # No annual fee
            elif annual_rewards_value > annual_fee:
                fee_score = 10  # Rewards exceed fees
            else:
                fee_score = 5   # Fees exceed rewards
            score += fee_score * 0.25
            
            # Intent alignment score (20% weight)
            intent_score = self._calculate_intent_alignment_score(card, intent)
            score += intent_score * 0.20
            
            # User profile fit score (15% weight)
            profile_score = self._calculate_profile_fit_score(card, user_profile)
            score += profile_score * 0.15
            
            return min(score, 100)  # Cap at 100
            
        except Exception as e:
            logger.error(f"Score calculation failed: {str(e)}")
            return 0.0
    
    def _calculate_intent_alignment_score(self, card: Dict[str, Any], intent: Optional[IntentType]) -> float:
        """Calculate how well the card aligns with user intent"""
        try:
            if not intent:
                return 10  # Neutral score if no specific intent
            
            card_tier = card.get("general_info", {}).get("tier", "").lower()
            card_benefits = card.get("benefits", {})
            rewards = card.get("rewards", {})
            
            if intent == IntentType.FIND_TRAVEL_CARD:
                score = 0
                
                # Check for travel benefits
                if card_benefits.get("travel"):
                    score += 10
                    if card_benefits["travel"].get("lounge_access"):
                        score += 5
                    if card_benefits["travel"].get("travel_insurance"):
                        score += 3
                
                # Check for travel rewards
                earning_rates = rewards.get("earning_rates", [])
                for rate in earning_rates:
                    if "travel" in rate.get("category", "").lower():
                        score += 8
                        break
                
                # Premium cards often have better travel benefits
                if card_tier in ["premium", "super-premium"]:
                    score += 5
                
                return min(score, 20)
            
            elif intent == IntentType.FIND_CASHBACK_CARD:
                score = 0
                
                # Check for high cashback rates
                base_rate = rewards.get("base_rate", 0)
                if base_rate >= 2.0:
                    score += 10
                elif base_rate >= 1.5:
                    score += 7
                elif base_rate >= 1.0:
                    score += 5
                
                # Check for multiple earning categories
                earning_rates = rewards.get("earning_rates", [])
                if len(earning_rates) >= 3:
                    score += 5
                
                # Check for high-value categories
                for rate in earning_rates:
                    if rate.get("rate", 0) >= 3.0:
                        score += 3
                
                return min(score, 20)
            
            elif intent == IntentType.FIND_PREMIUM_CARD:
                score = 0
                
                # Premium tier cards
                if card_tier in ["premium", "super-premium"]:
                    score += 15
                elif card_tier == "mid-tier":
                    score += 8
                else:
                    score += 3
                
                # Check for premium benefits
                if card_benefits.get("lifestyle", {}).get("concierge_service"):
                    score += 5
                
                if card_benefits.get("travel", {}).get("lounge_access"):
                    score += 5
                
                return min(score, 20)
            
            else:
                return 10  # Neutral score for general comparison
            
        except Exception as e:
            logger.error(f"Intent alignment calculation failed: {str(e)}")
            return 5
    
    def _calculate_profile_fit_score(self, card: Dict[str, Any], user_profile: UserProfile) -> float:
        """Calculate how well the card fits the user's spending profile"""
        try:
            score = 0.0
            monthly_spending = user_profile.monthly_spending
            total_monthly_spend = sum(monthly_spending.values())
            
            if total_monthly_spend == 0:
                return 10  # Neutral score if no spending data
            
            # Analyze spending patterns
            spending_analysis = self._analyze_spending_patterns(monthly_spending)
            
            # Check card earning rates against spending patterns
            earning_rates = card.get("rewards", {}).get("earning_rates", [])
            
            for rate in earning_rates:
                category = rate.get("category", "")
                rate_value = rate.get("rate", 0)
                category_spend = monthly_spending.get(category, 0)
                
                if category_spend > 0:
                    # Higher rate for categories user spends more on
                    category_ratio = category_spend / total_monthly_spend
                    if category_ratio > 0.3:  # High spending category
                        score += rate_value * 2
                    elif category_ratio > 0.1:  # Medium spending category
                        score += rate_value * 1.5
                    else:  # Low spending category
                        score += rate_value
            
            # Bonus for cards that match user's primary spending categories
            primary_categories = spending_analysis.get("primary_categories", [])
            for category in primary_categories:
                for rate in earning_rates:
                    if category in rate.get("category", "").lower():
                        score += 5
                        break
            
            return min(score, 20)
            
        except Exception as e:
            logger.error(f"Profile fit calculation failed: {str(e)}")
            return 5
    
    def _analyze_spending_patterns(self, monthly_spending: Dict[str, int]) -> Dict[str, Any]:
        """Analyze user's spending patterns"""
        try:
            total_spend = sum(monthly_spending.values())
            if total_spend == 0:
                return {"primary_categories": [], "spending_distribution": {}}
            
            # Calculate spending distribution
            distribution = {}
            for category, amount in monthly_spending.items():
                if amount > 0:
                    distribution[category] = amount / total_spend
            
            # Identify primary spending categories (>20% of total spend)
            primary_categories = [
                category for category, ratio in distribution.items() 
                if ratio > 0.2
            ]
            
            # Identify secondary spending categories (10-20% of total spend)
            secondary_categories = [
                category for category, ratio in distribution.items() 
                if 0.1 <= ratio <= 0.2
            ]
            
            return {
                "primary_categories": primary_categories,
                "secondary_categories": secondary_categories,
                "spending_distribution": distribution,
                "total_monthly_spend": total_spend
            }
            
        except Exception as e:
            logger.error(f"Spending pattern analysis failed: {str(e)}")
            return {"primary_categories": [], "spending_distribution": {}}
    
    def _generate_recommendation_rationale(self, card: Dict[str, Any], user_profile: UserProfile, rewards_data: Dict[str, Any], intent: Optional[IntentType]) -> str:
        """Generate human-readable rationale for the recommendation"""
        try:
            card_name = card.get("general_info", {}).get("card_name", "This card")
            annual_rewards = rewards_data.get("annual_cashback_value", 0)
            annual_fee = card.get("fees", {}).get("annual_fee", {}).get("amount", 0)
            net_value = annual_rewards - annual_fee
            
            rationale_parts = []
            
            # Rewards rationale
            if annual_rewards > 0:
                if net_value > 0:
                    rationale_parts.append(f"offers excellent value with ₹{annual_rewards:.0f} annual rewards")
                else:
                    rationale_parts.append(f"provides ₹{annual_rewards:.0f} in annual rewards")
            
            # Fee rationale
            if annual_fee == 0:
                rationale_parts.append("has no annual fee")
            elif net_value > 0:
                rationale_parts.append(f"annual fee of ₹{annual_fee} is offset by rewards")
            
            # Intent-specific rationale
            if intent == IntentType.FIND_TRAVEL_CARD:
                if card.get("benefits", {}).get("travel", {}).get("lounge_access"):
                    rationale_parts.append("includes complimentary lounge access")
                if any("travel" in rate.get("category", "").lower() for rate in card.get("rewards", {}).get("earning_rates", [])):
                    rationale_parts.append("earns bonus rewards on travel spending")
            
            elif intent == IntentType.FIND_CASHBACK_CARD:
                base_rate = card.get("rewards", {}).get("base_rate", 0)
                if base_rate > 1.0:
                    rationale_parts.append(f"provides {base_rate}% cashback on all purchases")
            
            # Spending pattern rationale
            spending_analysis = self._analyze_spending_patterns(user_profile.monthly_spending)
            primary_categories = spending_analysis.get("primary_categories", [])
            
            if primary_categories:
                earning_rates = card.get("rewards", {}).get("earning_rates", [])
                for category in primary_categories:
                    for rate in earning_rates:
                        if category in rate.get("category", "").lower():
                            rate_value = rate.get("rate", 0)
                            rationale_parts.append(f"earns {rate_value}% on your high {category} spending")
                            break
            
            # Fallback rationale
            if not rationale_parts:
                rationale_parts.append("matches your financial profile well")
            
            return f"{card_name} " + ", ".join(rationale_parts) + "."
            
        except Exception as e:
            logger.error(f"Rationale generation failed: {str(e)}")
            return f"{card.get('general_info', {}).get('card_name', 'This card')} is recommended based on your profile."
    
    def _load_ranking_weights(self) -> Dict[str, float]:
        """Load ranking weights configuration"""
        try:
            return {
                "rewards_value": 0.40,
                "fee_efficiency": 0.25,
                "intent_alignment": 0.20,
                "profile_fit": 0.15
            }
        except Exception as e:
            logger.error(f"Failed to load ranking weights: {str(e)}")
            return {
                "rewards_value": 0.40,
                "fee_efficiency": 0.25,
                "intent_alignment": 0.20,
                "profile_fit": 0.15
            }
    
    def get_recommendation_explanation(self, recommendation: CardRecommendation, user_profile: UserProfile) -> Dict[str, Any]:
        """Get detailed explanation for a specific recommendation"""
        try:
            card = recommendation.card
            rewards_tool = RewardsCalculatorTool()
            rewards_result = rewards_tool.execute(card, user_profile.monthly_spending)
            
            if not rewards_result["success"]:
                return {"error": "Failed to calculate rewards"}
            
            rewards_data = rewards_result["data"]
            
            explanation = {
                "card_name": card.get("general_info", {}).get("card_name"),
                "score_breakdown": {
                    "total_score": recommendation.score,
                    "rewards_value": rewards_data.get("annual_cashback_value", 0),
                    "annual_fee": card.get("fees", {}).get("annual_fee", {}).get("amount", 0),
                    "net_value": rewards_data.get("annual_cashback_value", 0) - card.get("fees", {}).get("annual_fee", {}).get("amount", 0)
                },
                "spending_analysis": rewards_data.get("category_breakdown", {}),
                "key_benefits": self._extract_key_benefits(card),
                "rationale": recommendation.rationale
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Recommendation explanation failed: {str(e)}")
            return {"error": str(e)}
    
    def _extract_key_benefits(self, card: Dict[str, Any]) -> List[str]:
        """Extract key benefits from card data"""
        try:
            benefits = []
            
            # Rewards benefits
            rewards = card.get("rewards", {})
            if rewards.get("welcome_bonus"):
                welcome = rewards["welcome_bonus"]
                benefits.append(f"Welcome bonus: {welcome.get('points', 0)} points worth ₹{welcome.get('value', 0)}")
            
            # Travel benefits
            travel_benefits = card.get("benefits", {}).get("travel", {})
            if travel_benefits.get("lounge_access"):
                lounge = travel_benefits["lounge_access"]
                benefits.append(f"Lounge access: {lounge.get('domestic_visits_per_quarter', 0)} domestic visits per quarter")
            
            # Lifestyle benefits
            lifestyle_benefits = card.get("benefits", {}).get("lifestyle", {})
            if lifestyle_benefits.get("concierge_service"):
                benefits.append("24/7 Concierge service")
            
            return benefits
            
        except Exception as e:
            logger.error(f"Key benefits extraction failed: {str(e)}")
            return []
