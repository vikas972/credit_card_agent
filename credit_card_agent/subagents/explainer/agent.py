"""
ExplainerAgent - Generates rationale for card recommendations
Builds user trust through transparent explanations
"""

import logging
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.models import LlmRequest

from ...models import UserProfile, CardRecommendation, CreditCard

logger = logging.getLogger(__name__)


class ExplainerAgent(Agent):
    """
    Explainer agent that generates clear, human-readable
    rationale for credit card recommendations.
    """
    
    def __init__(self, **kwargs):
        name = kwargs.pop('name', 'explainer')
        # Set a default model for ADK compatibility
        if 'model' not in kwargs:
            kwargs['model'] = 'gemini-pro'
        super().__init__(name=name, **kwargs)
        self._explanation_templates = self._load_explanation_templates()
    
    def generate_rationale(self, recommendation: CardRecommendation, user_profile: UserProfile) -> str:
        """
        Generate detailed rationale for a card recommendation
        
        Args:
            recommendation: Card recommendation object
            user_profile: User's profile data
            
        Returns:
            Human-readable rationale
        """
        try:
            card = recommendation.card
            card_name = card.get("general_info", {}).get("card_name", "This card")
            
            # Generate different types of explanations
            explanations = []
            
            # Rewards explanation
            rewards_explanation = self._explain_rewards_value(card, user_profile)
            if rewards_explanation:
                explanations.append(rewards_explanation)
            
            # Fee explanation
            fee_explanation = self._explain_fee_structure(card, user_profile)
            if fee_explanation:
                explanations.append(fee_explanation)
            
            # Benefits explanation
            benefits_explanation = self._explain_benefits(card, user_profile)
            if benefits_explanation:
                explanations.append(benefits_explanation)
            
            # Spending pattern explanation
            spending_explanation = self._explain_spending_alignment(card, user_profile)
            if spending_explanation:
                explanations.append(spending_explanation)
            
            # Combine explanations
            if explanations:
                rationale = f"{card_name} is recommended because " + ". ".join(explanations) + "."
            else:
                rationale = f"{card_name} is recommended based on your financial profile and spending patterns."
            
            return rationale
            
        except Exception as e:
            logger.error(f"Rationale generation failed: {str(e)}")
            return f"{recommendation.card.get('general_info', {}).get('card_name', 'This card')} is recommended based on your profile."
    
    def generate_comparison_rationale(self, card_a: Dict[str, Any], card_b: Dict[str, Any], user_profile: UserProfile, comparison_data: Dict[str, Any]) -> str:
        """
        Generate rationale for card comparison
        
        Args:
            card_a: First card data
            card_b: Second card data
            user_profile: User's profile data
            comparison_data: Comparison analysis data
            
        Returns:
            Comparison rationale
        """
        try:
            card_a_name = card_a.get("general_info", {}).get("card_name", "Card A")
            card_b_name = card_b.get("general_info", {}).get("card_name", "Card B")
            
            # Determine which card is better
            net_value_a = comparison_data.get("net_annual_value_a", 0)
            net_value_b = comparison_data.get("net_annual_value_b", 0)
            
            if net_value_a > net_value_b:
                better_card = card_a_name
                worse_card = card_b_name
                value_difference = net_value_a - net_value_b
            else:
                better_card = card_b_name
                worse_card = card_a_name
                value_difference = net_value_b - net_value_a
            
            rationale = f"Between {card_a_name} and {card_b_name}, {better_card} offers better value with ₹{value_difference:.0f} more annual value. "
            
            # Add specific reasons
            reasons = []
            
            if comparison_data.get("annual_rewards_value_a", 0) > comparison_data.get("annual_rewards_value_b", 0):
                reasons.append(f"{card_a_name} provides higher rewards")
            else:
                reasons.append(f"{card_b_name} provides higher rewards")
            
            if comparison_data.get("net_annual_cost_a", 0) < comparison_data.get("net_annual_cost_b", 0):
                reasons.append(f"{card_a_name} has lower costs")
            else:
                reasons.append(f"{card_b_name} has lower costs")
            
            if reasons:
                rationale += "This is because " + " and ".join(reasons) + "."
            
            return rationale
            
        except Exception as e:
            logger.error(f"Comparison rationale generation failed: {str(e)}")
            return f"Both {card_a.get('general_info', {}).get('card_name', 'Card A')} and {card_b.get('general_info', {}).get('card_name', 'Card B')} have their merits based on your profile."
    
    def _explain_rewards_value(self, card: Dict[str, Any], user_profile: UserProfile) -> str:
        """Explain the rewards value proposition"""
        try:
            rewards = card.get("rewards", {})
            earning_rates = rewards.get("earning_rates", [])
            base_rate = rewards.get("base_rate", 0)
            
            # Find highest earning rate
            max_rate = base_rate
            max_category = "all purchases"
            
            for rate in earning_rates:
                if rate.get("rate", 0) > max_rate:
                    max_rate = rate.get("rate", 0)
                    max_category = rate.get("category", "purchases")
            
            # Calculate potential annual value
            total_monthly_spend = sum(user_profile.monthly_spending.values())
            annual_spend = total_monthly_spend * 12
            potential_annual_value = annual_spend * (max_rate / 100)
            
            if max_rate > base_rate:
                explanation = f"it offers {max_rate}% rewards on {max_category}, potentially earning you ₹{potential_annual_value:.0f} annually"
            else:
                explanation = f"it provides {base_rate}% rewards on all purchases, potentially earning you ₹{potential_annual_value:.0f} annually"
            
            return explanation
            
        except Exception as e:
            logger.error(f"Rewards explanation failed: {str(e)}")
            return "it offers competitive rewards"
    
    def _explain_fee_structure(self, card: Dict[str, Any], user_profile: UserProfile) -> str:
        """Explain the fee structure and waiver conditions"""
        try:
            fees = card.get("fees", {})
            annual_fee = fees.get("annual_fee", {})
            fee_amount = annual_fee.get("amount", 0)
            waiver_condition = annual_fee.get("waiver_condition")
            
            if fee_amount == 0:
                return "it has no annual fee"
            
            if waiver_condition:
                spend_threshold = waiver_condition.get("spend_threshold", 0)
                total_annual_spend = sum(user_profile.monthly_spending.values()) * 12
                
                if total_annual_spend >= spend_threshold:
                    return f"the ₹{fee_amount} annual fee is waived based on your spending level"
                else:
                    return f"it has a ₹{fee_amount} annual fee, but this can be waived with ₹{spend_threshold:,} annual spending"
            else:
                return f"it has a ₹{fee_amount} annual fee"
            
        except Exception as e:
            logger.error(f"Fee explanation failed: {str(e)}")
            return "it has competitive fees"
    
    def _explain_benefits(self, card: Dict[str, Any], user_profile: UserProfile) -> str:
        """Explain key benefits relevant to the user"""
        try:
            benefits = card.get("benefits", {})
            relevant_benefits = []
            
            # Travel benefits
            travel_benefits = benefits.get("travel", {})
            if travel_benefits.get("lounge_access"):
                lounge = travel_benefits["lounge_access"]
                domestic_visits = lounge.get("domestic_visits_per_quarter", 0)
                if domestic_visits > 0:
                    relevant_benefits.append(f"airport lounge access ({domestic_visits} domestic visits per quarter)")
            
            if travel_benefits.get("travel_insurance"):
                relevant_benefits.append("travel insurance coverage")
            
            # Lifestyle benefits
            lifestyle_benefits = benefits.get("lifestyle", {})
            if lifestyle_benefits.get("concierge_service"):
                relevant_benefits.append("24/7 concierge service")
            
            if lifestyle_benefits.get("dining_discounts"):
                relevant_benefits.append("dining discounts")
            
            if lifestyle_benefits.get("movie_offers"):
                relevant_benefits.append("movie ticket offers")
            
            # Insurance benefits
            insurance_benefits = benefits.get("insurance", {})
            if insurance_benefits.get("fraud_liability_cover"):
                relevant_benefits.append("fraud protection")
            
            if relevant_benefits:
                if len(relevant_benefits) == 1:
                    return f"it includes {relevant_benefits[0]}"
                else:
                    return f"it offers additional benefits like {', '.join(relevant_benefits[:2])}"
            
            return ""
            
        except Exception as e:
            logger.error(f"Benefits explanation failed: {str(e)}")
            return ""
    
    def _explain_spending_alignment(self, card: Dict[str, Any], user_profile: UserProfile) -> str:
        """Explain how the card aligns with user's spending patterns"""
        try:
            monthly_spending = user_profile.monthly_spending
            total_spend = sum(monthly_spending.values())
            
            if total_spend == 0:
                return ""
            
            # Find user's top spending categories
            spending_ratios = {cat: amount/total_spend for cat, amount in monthly_spending.items() if amount > 0}
            top_categories = sorted(spending_ratios.items(), key=lambda x: x[1], reverse=True)[:2]
            
            # Check card's earning rates for these categories
            earning_rates = card.get("rewards", {}).get("earning_rates", [])
            aligned_categories = []
            
            for category, ratio in top_categories:
                if ratio > 0.1:  # More than 10% of spending
                    for rate in earning_rates:
                        if category in rate.get("category", "").lower():
                            rate_value = rate.get("rate", 0)
                            if rate_value > 1.0:  # Higher than base rate
                                aligned_categories.append(f"{rate_value}% on {category}")
                            break
            
            if aligned_categories:
                return f"it offers bonus rewards on your high spending categories: {', '.join(aligned_categories)}"
            
            return ""
            
        except Exception as e:
            logger.error(f"Spending alignment explanation failed: {str(e)}")
            return ""
    
    def generate_llm_explanation(self, recommendation: CardRecommendation, user_profile: UserProfile) -> str:
        """Generate explanation using LLM for more nuanced reasoning"""
        try:
            card = recommendation.card
            card_name = card.get("general_info", {}).get("card_name", "This card")
            
            prompt = f"""
            Explain why {card_name} is recommended for this user profile:
            
            User Profile:
            - Age: {user_profile.age}
            - Employment: {user_profile.employment}
            - Monthly Income: ₹{user_profile.net_monthly_income:,}
            - Credit Score: {user_profile.credit_score}
            - City: {user_profile.city}
            - Monthly Spending: {user_profile.monthly_spending}
            
            Card Details:
            - Annual Fee: ₹{card.get('fees', {}).get('annual_fee', {}).get('amount', 0):,}
            - Base Reward Rate: {card.get('rewards', {}).get('base_rate', 0)}%
            - Earning Rates: {card.get('rewards', {}).get('earning_rates', [])}
            - Key Benefits: {self._extract_benefit_summary(card)}
            
            Provide a clear, concise explanation (2-3 sentences) of why this card is recommended for this specific user.
            Focus on the most relevant benefits and how they align with the user's spending patterns.
            """
            
            request = LlmRequest(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            response = self.llm_client.generate(request)
            explanation = response.choices[0].message.content.strip()
            
            return explanation
            
        except Exception as e:
            logger.error(f"LLM explanation generation failed: {str(e)}")
            # Fallback to template-based explanation
            return self.generate_rationale(recommendation, user_profile)
    
    def _extract_benefit_summary(self, card: Dict[str, Any]) -> List[str]:
        """Extract key benefits for LLM prompt"""
        try:
            benefits = []
            
            # Travel benefits
            travel = card.get("benefits", {}).get("travel", {})
            if travel.get("lounge_access"):
                benefits.append("airport lounge access")
            if travel.get("travel_insurance"):
                benefits.append("travel insurance")
            
            # Lifestyle benefits
            lifestyle = card.get("benefits", {}).get("lifestyle", {})
            if lifestyle.get("concierge_service"):
                benefits.append("concierge service")
            if lifestyle.get("dining_discounts"):
                benefits.append("dining discounts")
            
            return benefits
            
        except Exception as e:
            logger.error(f"Benefit summary extraction failed: {str(e)}")
            return []
    
    def generate_why_not_explanation(self, card: Dict[str, Any], user_profile: UserProfile, rejection_reasons: List[str]) -> str:
        """Generate explanation for why a card is not recommended"""
        try:
            card_name = card.get("general_info", {}).get("card_name", "This card")
            
            if not rejection_reasons:
                return f"{card_name} may not be the best fit for your current profile."
            
            # Categorize rejection reasons
            if any("income" in reason.lower() for reason in rejection_reasons):
                return f"{card_name} requires higher income than your current level."
            elif any("credit score" in reason.lower() for reason in rejection_reasons):
                return f"{card_name} requires a higher credit score than your current {user_profile.credit_score}."
            elif any("age" in reason.lower() for reason in rejection_reasons):
                return f"{card_name} has age restrictions that don't match your profile."
            else:
                return f"{card_name} doesn't meet your eligibility requirements."
            
        except Exception as e:
            logger.error(f"Why not explanation generation failed: {str(e)}")
            return f"This card may not be suitable for your profile."
    
    def generate_improvement_suggestions(self, user_profile: UserProfile, ineligible_cards: List[Dict[str, Any]]) -> List[str]:
        """Generate suggestions to improve eligibility"""
        try:
            suggestions = []
            
            # Analyze rejection patterns
            rejection_analysis = self._analyze_rejection_patterns(ineligible_cards)
            
            if rejection_analysis.get("income_issues", 0) > 0:
                suggestions.append("Consider cards with lower income requirements or wait for income growth")
            
            if rejection_analysis.get("credit_score_issues", 0) > 0:
                suggestions.append("Work on improving your credit score by paying bills on time and reducing debt")
                suggestions.append("Consider secured credit cards to build credit history")
            
            if rejection_analysis.get("age_issues", 0) > 0:
                if user_profile.age < 21:
                    suggestions.append("Wait until you turn 21 for most credit cards")
                else:
                    suggestions.append("Look for cards with higher age limits")
            
            if not suggestions:
                suggestions.append("Consider applying for secured credit cards")
                suggestions.append("Look for cards with more flexible eligibility criteria")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Improvement suggestions generation failed: {str(e)}")
            return ["Please contact customer support for personalized guidance"]
    
    def _analyze_rejection_patterns(self, ineligible_cards: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze patterns in card rejections"""
        try:
            patterns = {
                "income_issues": 0,
                "credit_score_issues": 0,
                "age_issues": 0,
                "location_issues": 0
            }
            
            for card_data in ineligible_cards:
                if "rejection_reasons" in card_data:
                    for reason in card_data["rejection_reasons"]:
                        reason_lower = reason.lower()
                        if "income" in reason_lower:
                            patterns["income_issues"] += 1
                        elif "credit score" in reason_lower:
                            patterns["credit_score_issues"] += 1
                        elif "age" in reason_lower:
                            patterns["age_issues"] += 1
                        elif "location" in reason_lower:
                            patterns["location_issues"] += 1
            
            return patterns
            
        except Exception as e:
            logger.error(f"Rejection pattern analysis failed: {str(e)}")
            return {}
    
    def _load_explanation_templates(self) -> Dict[str, str]:
        """Load explanation templates"""
        try:
            return {
                "rewards_template": "it offers {rate}% rewards on {category}, potentially earning you ₹{value:.0f} annually",
                "fee_template": "it has a ₹{fee:,} annual fee{waiver_text}",
                "benefits_template": "it includes {benefits}",
                "spending_template": "it offers bonus rewards on your high spending categories: {categories}"
            }
        except Exception as e:
            logger.error(f"Failed to load explanation templates: {str(e)}")
            return {}
