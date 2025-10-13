"""
ComparisonAnalysisAgent - Performs detailed card comparisons using LLM
Core analytical engine for sophisticated card comparisons
"""

import logging
import json
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.models import LlmRequest

from ...models import UserProfile, CreditCard, ComparisonResult
from ...tools import RewardsCalculatorTool

logger = logging.getLogger(__name__)


class ComparisonAnalysisAgent(Agent):
    """
    Comparison analysis agent that performs sophisticated
    quantitative and qualitative analysis of credit cards.
    """
    
    def __init__(self, **kwargs):
        name = kwargs.pop('name', 'comparison_analysis')
        # Set a default model for ADK compatibility
        if 'model' not in kwargs:
            kwargs['model'] = 'gemini-pro'
        super().__init__(name=name, **kwargs)
        self.tools = [RewardsCalculatorTool()]
        self._master_comparison_prompt = self._load_master_prompt()
    
    def compare_cards(self, card_a: Dict[str, Any], card_b: Dict[str, Any], user_profile: UserProfile) -> ComparisonResult:
        """
        Perform detailed comparison between two credit cards
        
        Args:
            card_a: First credit card data
            card_b: Second credit card data
            user_profile: User's profile data
            
        Returns:
            Detailed comparison result
        """
        try:
            # Calculate rewards for both cards
            rewards_tool = RewardsCalculatorTool()
            
            rewards_a = rewards_tool.execute(card_a, user_profile.monthly_spending)
            rewards_b = rewards_tool.execute(card_b, user_profile.monthly_spending)
            
            if not rewards_a["success"] or not rewards_b["success"]:
                raise Exception("Failed to calculate rewards for comparison")
            
            # Calculate net costs
            net_cost_a = self._calculate_net_annual_cost(card_a, rewards_a["data"])
            net_cost_b = self._calculate_net_annual_cost(card_b, rewards_b["data"])
            
            # Calculate net values
            net_value_a = rewards_a["data"]["annual_cashback_value"] - net_cost_a
            net_value_b = rewards_b["data"]["annual_cashback_value"] - net_cost_b
            
            # Generate LLM analysis
            llm_analysis = self._generate_llm_analysis(card_a, card_b, user_profile, rewards_a["data"], rewards_b["data"])
            
            # Create comparison result
            comparison = ComparisonResult(
                card_a=card_a,
                card_b=card_b,
                net_annual_cost_a=net_cost_a,
                net_annual_cost_b=net_cost_b,
                annual_rewards_value_a=rewards_a["data"]["annual_cashback_value"],
                annual_rewards_value_b=rewards_b["data"]["annual_cashback_value"],
                net_annual_value_a=net_value_a,
                net_annual_value_b=net_value_b,
                primary_benefit_a=llm_analysis.get("primary_benefit_a", "Standard benefits"),
                primary_benefit_b=llm_analysis.get("primary_benefit_b", "Standard benefits"),
                key_drawback_a=llm_analysis.get("key_drawback_a", "None identified"),
                key_drawback_b=llm_analysis.get("key_drawback_b", "None identified"),
                recommendation=llm_analysis.get("recommendation", "Both cards have merits"),
                justification=llm_analysis.get("justification", "Based on your profile analysis")
            )
            
            logger.info(f"Comparison completed: {card_a.get('general_info', {}).get('card_name')} vs {card_b.get('general_info', {}).get('card_name')}")
            
            return comparison
            
        except Exception as e:
            logger.error(f"Card comparison failed: {str(e)}")
            # Return a basic comparison result
            return self._create_fallback_comparison(card_a, card_b, user_profile)
    
    def _calculate_net_annual_cost(self, card: Dict[str, Any], rewards_data: Dict[str, Any]) -> int:
        """Calculate net annual cost after considering fee waivers"""
        try:
            annual_fee = card.get("fees", {}).get("annual_fee", {}).get("amount", 0)
            waiver_condition = card.get("fees", {}).get("annual_fee", {}).get("waiver_condition")
            
            if not waiver_condition:
                return annual_fee
            
            # Check if user meets waiver condition
            annual_spend = sum(rewards_data.get("category_breakdown", {}).values()) * 12
            spend_threshold = waiver_condition.get("spend_threshold", 0)
            
            if annual_spend >= spend_threshold:
                return 0  # Fee waived
            else:
                return annual_fee
                
        except Exception as e:
            logger.error(f"Net cost calculation failed: {str(e)}")
            return card.get("fees", {}).get("annual_fee", {}).get("amount", 0)
    
    def _generate_llm_analysis(self, card_a: Dict[str, Any], card_b: Dict[str, Any], user_profile: UserProfile, rewards_a: Dict[str, Any], rewards_b: Dict[str, Any]) -> Dict[str, Any]:
        """Generate LLM-powered analysis using the master comparison prompt"""
        try:
            # Prepare user profile JSON
            user_profile_json = {
                "age": user_profile.age,
                "employment": user_profile.employment,
                "netMonthlyIncome": user_profile.net_monthly_income,
                "creditScore": user_profile.credit_score,
                "city": user_profile.city,
                "monthlySpending": user_profile.monthly_spending
            }
            
            # Create the master comparison prompt
            prompt = self._build_comparison_prompt(card_a, card_b, user_profile_json, rewards_a, rewards_b)
            
            # Call LLM
            request = LlmRequest(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            response = self.llm_client.generate(request)
            analysis_text = response.choices[0].message.content
            
            # Parse LLM response
            return self._parse_llm_response(analysis_text)
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            return self._create_fallback_analysis(card_a, card_b)
    
    def _build_comparison_prompt(self, card_a: Dict[str, Any], card_b: Dict[str, Any], user_profile: Dict[str, Any], rewards_a: Dict[str, Any], rewards_b: Dict[str, Any]) -> str:
        """Build the master comparison prompt"""
        try:
            prompt = f"""
You are an expert, impartial credit card analyst. Your function is to provide a detailed, objective comparison of two credit cards based on the provided user profile and structured card data. Your analysis must be quantitative where possible, qualitative where necessary, and conclude with a clear, justified recommendation for the specified user. Adhere strictly to the provided output structure. Do not discuss any financial products other than credit cards. Do not mention any competitor services.

User Profile:
{json.dumps(user_profile, indent=2)}

Card A Data:
{json.dumps(card_a, indent=2)}

Card B Data:
{json.dumps(card_b, indent=2)}

Rewards Analysis for Card A:
{json.dumps(rewards_a, indent=2)}

Rewards Analysis for Card B:
{json.dumps(rewards_b, indent=2)}

[Analysis Instructions]
1. *Fee Analysis:*
   - For each card, state the Annual Fee.
   - Based on the user's total annual spending, determine if the spend-based waiver condition is met.
   - Calculate and state the "Net Annual Cost" for each card (Annual Fee minus waived amount).

2. *Rewards Analysis (Quantitative):*
   - For each card, calculate the total estimated annual rewards value in INR.
   - You must show your calculations step-by-step, mapping the user's monthly spending categories to the card's earning rates.
   - Multiply monthly rewards by 12 to get the annual total.
   - Convert reward points to INR using the card's redemption.cashbackValuePerPoint.

3. *Benefit Analysis (Qualitative):*
   - Evaluate the primary non-monetary benefits of each card specifically for this user.
   - Assess the value of Travel Benefits (Lounge Access, etc.). Given the user's monthly travel spend, state whether this is a high, medium, or low-value benefit for them.
   - Assess the value of Lifestyle Benefits (Dining, Movies, etc.) based on their spending profile.

4. *Comparative Summary:*
   - Generate a Markdown table with the following rows: "Net Annual Cost", "Estimated Annual Rewards Value", "Net Annual Value (Rewards - Cost)", "Primary Benefit for this User", "Key Drawback for this User".

5. *Final Recommendation:*
   - Based on the highest "Net Annual Value" and the qualitative benefit analysis, provide a definitive recommendation.
   - Justify your recommendation in 2-3 sentences, explaining why one card is a better fit for this user's specific financial habits.

Please respond with a JSON object containing:
{{
    "fee_analysis": {{
        "card_a": {{"annual_fee": 0, "net_cost": 0, "waiver_met": false}},
        "card_b": {{"annual_fee": 0, "net_cost": 0, "waiver_met": false}}
    }},
    "rewards_analysis": {{
        "card_a": {{"annual_value": 0, "calculation_steps": []}},
        "card_b": {{"annual_value": 0, "calculation_steps": []}}
    }},
    "benefit_analysis": {{
        "card_a": {{"travel_value": "high/medium/low", "lifestyle_value": "high/medium/low", "primary_benefit": ""}},
        "card_b": {{"travel_value": "high/medium/low", "lifestyle_value": "high/medium/low", "primary_benefit": ""}}
    }},
    "comparative_summary": {{
        "net_annual_cost_a": 0,
        "net_annual_cost_b": 0,
        "annual_rewards_value_a": 0,
        "annual_rewards_value_b": 0,
        "net_annual_value_a": 0,
        "net_annual_value_b": 0,
        "primary_benefit_a": "",
        "primary_benefit_b": "",
        "key_drawback_a": "",
        "key_drawback_b": ""
    }},
    "recommendation": "",
    "justification": ""
}}
"""
            return prompt
            
        except Exception as e:
            logger.error(f"Prompt building failed: {str(e)}")
            return "Please provide a basic comparison of the two credit cards."
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response and extract structured data"""
        try:
            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                # Fallback to text parsing
                return self._parse_text_response(response_text)
            
            analysis = json.loads(json_text)
            
            # Extract key information
            return {
                "primary_benefit_a": analysis.get("benefit_analysis", {}).get("card_a", {}).get("primary_benefit", ""),
                "primary_benefit_b": analysis.get("benefit_analysis", {}).get("card_b", {}).get("primary_benefit", ""),
                "key_drawback_a": analysis.get("comparative_summary", {}).get("key_drawback_a", ""),
                "key_drawback_b": analysis.get("comparative_summary", {}).get("key_drawback_b", ""),
                "recommendation": analysis.get("recommendation", ""),
                "justification": analysis.get("justification", ""),
                "full_analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"LLM response parsing failed: {str(e)}")
            return self._parse_text_response(response_text)
    
    def _parse_text_response(self, response_text: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails"""
        try:
            # Simple text parsing as fallback
            lines = response_text.split('\n')
            
            analysis = {
                "primary_benefit_a": "Standard benefits",
                "primary_benefit_b": "Standard benefits",
                "key_drawback_a": "None identified",
                "key_drawback_b": "None identified",
                "recommendation": "Both cards have merits",
                "justification": "Based on your profile analysis"
            }
            
            # Look for recommendation keywords
            for line in lines:
                if "recommend" in line.lower() and "card" in line.lower():
                    analysis["recommendation"] = line.strip()
                elif "because" in line.lower() or "due to" in line.lower():
                    analysis["justification"] = line.strip()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Text response parsing failed: {str(e)}")
            return {
                "primary_benefit_a": "Standard benefits",
                "primary_benefit_b": "Standard benefits",
                "key_drawback_a": "None identified",
                "key_drawback_b": "None identified",
                "recommendation": "Both cards have merits",
                "justification": "Based on your profile analysis"
            }
    
    def _create_fallback_analysis(self, card_a: Dict[str, Any], card_b: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback analysis when LLM fails"""
        try:
            card_a_name = card_a.get("general_info", {}).get("card_name", "Card A")
            card_b_name = card_b.get("general_info", {}).get("card_name", "Card B")
            
            return {
                "primary_benefit_a": f"{card_a_name} offers competitive rewards",
                "primary_benefit_b": f"{card_b_name} provides good value",
                "key_drawback_a": "Higher annual fee",
                "key_drawback_b": "Lower reward rates",
                "recommendation": f"Consider {card_a_name} for better rewards",
                "justification": "Based on standard comparison criteria"
            }
            
        except Exception as e:
            logger.error(f"Fallback analysis creation failed: {str(e)}")
            return {
                "primary_benefit_a": "Standard benefits",
                "primary_benefit_b": "Standard benefits",
                "key_drawback_a": "None identified",
                "key_drawback_b": "None identified",
                "recommendation": "Both cards have merits",
                "justification": "Based on your profile analysis"
            }
    
    def _create_fallback_comparison(self, card_a: Dict[str, Any], card_b: Dict[str, Any], user_profile: UserProfile) -> ComparisonResult:
        """Create fallback comparison when analysis fails"""
        try:
            return ComparisonResult(
                card_a=card_a,
                card_b=card_b,
                net_annual_cost_a=card_a.get("fees", {}).get("annual_fee", {}).get("amount", 0),
                net_annual_cost_b=card_b.get("fees", {}).get("annual_fee", {}).get("amount", 0),
                annual_rewards_value_a=0,
                annual_rewards_value_b=0,
                net_annual_value_a=0,
                net_annual_value_b=0,
                primary_benefit_a="Standard benefits",
                primary_benefit_b="Standard benefits",
                key_drawback_a="None identified",
                key_drawback_b="None identified",
                recommendation="Both cards have merits",
                justification="Based on your profile analysis"
            )
            
        except Exception as e:
            logger.error(f"Fallback comparison creation failed: {str(e)}")
            # Return minimal comparison
            return ComparisonResult(
                card_a=card_a,
                card_b=card_b,
                net_annual_cost_a=0,
                net_annual_cost_b=0,
                annual_rewards_value_a=0,
                annual_rewards_value_b=0,
                net_annual_value_a=0,
                net_annual_value_b=0,
                primary_benefit_a="",
                primary_benefit_b="",
                key_drawback_a="",
                key_drawback_b="",
                recommendation="",
                justification=""
            )
    
    def _load_master_prompt(self) -> str:
        """Load the master comparison prompt template"""
        try:
            # In a real implementation, this would load from a file or database
            return """
You are an expert, impartial credit card analyst. Your function is to provide a detailed, objective comparison of two credit cards based on the provided user profile and structured card data. Your analysis must be quantitative where possible, qualitative where necessary, and conclude with a clear, justified recommendation for the specified user. Adhere strictly to the provided output structure. Do not discuss any financial products other than credit cards. Do not mention any competitor services.
"""
        except Exception as e:
            logger.error(f"Failed to load master prompt: {str(e)}")
            return "Please provide a detailed comparison of the two credit cards."
    
    def analyze_card_features(self, card: Dict[str, Any], user_profile: UserProfile) -> Dict[str, Any]:
        """Analyze features of a single card for the user"""
        try:
            rewards_tool = RewardsCalculatorTool()
            rewards_result = rewards_tool.execute(card, user_profile.monthly_spending)
            
            if not rewards_result["success"]:
                return {"error": "Failed to analyze card features"}
            
            rewards_data = rewards_result["data"]
            
            analysis = {
                "card_name": card.get("general_info", {}).get("card_name"),
                "annual_fee": card.get("fees", {}).get("annual_fee", {}).get("amount", 0),
                "annual_rewards_value": rewards_data.get("annual_cashback_value", 0),
                "net_value": rewards_data.get("annual_cashback_value", 0) - card.get("fees", {}).get("annual_fee", {}).get("amount", 0),
                "key_features": self._extract_key_features(card),
                "spending_analysis": rewards_data.get("category_breakdown", {}),
                "recommendation_score": self._calculate_single_card_score(card, rewards_data, user_profile)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Card feature analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def _extract_key_features(self, card: Dict[str, Any]) -> List[str]:
        """Extract key features from card data"""
        try:
            features = []
            
            # Rewards features
            rewards = card.get("rewards", {})
            if rewards.get("welcome_bonus"):
                welcome = rewards["welcome_bonus"]
                features.append(f"Welcome bonus: {welcome.get('points', 0)} points")
            
            # Travel features
            travel_benefits = card.get("benefits", {}).get("travel", {})
            if travel_benefits.get("lounge_access"):
                features.append("Airport lounge access")
            if travel_benefits.get("travel_insurance"):
                features.append("Travel insurance")
            
            # Lifestyle features
            lifestyle_benefits = card.get("benefits", {}).get("lifestyle", {})
            if lifestyle_benefits.get("concierge_service"):
                features.append("24/7 Concierge service")
            if lifestyle_benefits.get("dining_discounts"):
                features.append("Dining discounts")
            
            return features
            
        except Exception as e:
            logger.error(f"Key features extraction failed: {str(e)}")
            return []
    
    def _calculate_single_card_score(self, card: Dict[str, Any], rewards_data: Dict[str, Any], user_profile: UserProfile) -> float:
        """Calculate recommendation score for a single card"""
        try:
            score = 0.0
            
            # Rewards value score
            annual_rewards = rewards_data.get("annual_cashback_value", 0)
            score += min(annual_rewards / 100, 50)  # Cap at 50 points
            
            # Fee efficiency score
            annual_fee = card.get("fees", {}).get("annual_fee", {}).get("amount", 0)
            if annual_fee == 0:
                score += 20
            elif annual_rewards > annual_fee:
                score += 15
            else:
                score += 5
            
            # Feature richness score
            features = self._extract_key_features(card)
            score += min(len(features) * 2, 20)  # Cap at 20 points
            
            # Tier bonus
            tier = card.get("general_info", {}).get("tier", "").lower()
            if tier == "premium":
                score += 10
            elif tier == "super-premium":
                score += 15
            
            return min(score, 100)  # Cap at 100
            
        except Exception as e:
            logger.error(f"Single card score calculation failed: {str(e)}")
            return 0.0
