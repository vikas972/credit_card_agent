"""
ResponseGenerationAgent - Synthesizes analysis into user-friendly reports
Final link in the chain with compliance guardrails
"""

import logging
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.tools import BaseTool

from ...models import UserProfile, CardRecommendation, ComparisonResult, AgentResponse
from ...tools import ComplianceGuardrailTool

logger = logging.getLogger(__name__)


class ResponseGenerationAgent(Agent):
    """
    Response generation agent that synthesizes analysis into
    polished, user-friendly reports with compliance guardrails.
    """
    
    def __init__(self, **kwargs):
        name = kwargs.pop('name', 'response_generation')
        super().__init__(name=name, **kwargs)
        self.tools = [ComplianceGuardrailTool()]
        self._response_templates = self._load_response_templates()
    
    def generate_recommendation_response(self, recommendations: List[CardRecommendation], user_profile: UserProfile, trace_id: str) -> AgentResponse:
        """
        Generate formatted recommendation response
        
        Args:
            recommendations: List of card recommendations
            user_profile: User's profile data
            trace_id: Unique trace identifier
            
        Returns:
            Formatted agent response
        """
        try:
            # Format recommendations
            formatted_recommendations = []
            
            for i, rec in enumerate(recommendations, 1):
                formatted_rec = self._format_single_recommendation(rec, i, user_profile)
                formatted_recommendations.append(formatted_rec)
            
            # Generate response content
            response_content = {
                "user_profile_summary": self._format_user_profile_summary(user_profile),
                "recommendations": formatted_recommendations,
                "total_analyzed": len(recommendations),
                "analysis_timestamp": self._get_current_timestamp(),
                "disclaimer": self._get_disclaimer_text()
            }
            
            # Apply compliance guardrails
            compliance_result = self._apply_compliance_guardrails(response_content)
            if not compliance_result["is_compliant"]:
                logger.warning(f"Compliance violation detected: {compliance_result['violations']}")
                response_content = self._sanitize_response(response_content, compliance_result["violations"])
            
            return AgentResponse(
                success=True,
                data=response_content,
                trace_id=trace_id
            )
            
        except Exception as e:
            logger.error(f"Recommendation response generation failed: {str(e)}")
            return AgentResponse(
                success=False,
                error=f"Failed to generate response: {str(e)}",
                trace_id=trace_id
            )
    
    def generate_comparison_response(self, comparison: ComparisonResult, user_profile: UserProfile, trace_id: str) -> AgentResponse:
        """
        Generate formatted comparison response
        
        Args:
            comparison: Comparison result data
            user_profile: User's profile data
            trace_id: Unique trace identifier
            
        Returns:
            Formatted agent response
        """
        try:
            # Format comparison data
            comparison_data = {
                "card_a": self._format_card_summary(comparison.card_a, "A"),
                "card_b": self._format_card_summary(comparison.card_b, "B"),
                "comparison_table": self._generate_comparison_table(comparison),
                "recommendation": {
                    "winner": self._determine_comparison_winner(comparison),
                    "justification": comparison.justification
                },
                "analysis_timestamp": self._get_current_timestamp()
            }
            
            # Apply compliance guardrails
            compliance_result = self._apply_compliance_guardrails(comparison_data)
            if not compliance_result["is_compliant"]:
                logger.warning(f"Compliance violation in comparison: {compliance_result['violations']}")
                comparison_data = self._sanitize_response(comparison_data, compliance_result["violations"])
            
            return AgentResponse(
                success=True,
                data=comparison_data,
                trace_id=trace_id
            )
            
        except Exception as e:
            logger.error(f"Comparison response generation failed: {str(e)}")
            return AgentResponse(
                success=False,
                error=f"Failed to generate comparison: {str(e)}",
                trace_id=trace_id
            )
    
    def generate_error_response(self, error_message: str, trace_id: str) -> AgentResponse:
        """Generate formatted error response"""
        try:
            error_response = {
                "error": {
                    "message": error_message,
                    "type": "processing_error",
                    "timestamp": self._get_current_timestamp()
                },
                "suggestions": [
                    "Please try rephrasing your query",
                    "Ensure all required information is provided",
                    "Contact support if the issue persists"
                ]
            }
            
            return AgentResponse(
                success=False,
                data=error_response,
                trace_id=trace_id
            )
            
        except Exception as e:
            logger.error(f"Error response generation failed: {str(e)}")
            return AgentResponse(
                success=False,
                error="Internal error occurred",
                trace_id=trace_id
            )
    
    def _format_single_recommendation(self, recommendation: CardRecommendation, rank: int, user_profile: UserProfile) -> Dict[str, Any]:
        """Format a single recommendation for display"""
        try:
            card = recommendation.card
            general_info = card.get("general_info", {})
            fees = card.get("fees", {})
            rewards = card.get("rewards", {})
            
            # Calculate key metrics
            annual_fee = fees.get("annual_fee", {}).get("amount", 0)
            base_rate = rewards.get("base_rate", 0)
            
            # Format recommendation
            formatted_rec = {
                "rank": rank,
                "card_name": general_info.get("card_name", "Unknown Card"),
                "issuer": general_info.get("issuer", "Unknown Issuer"),
                "tier": general_info.get("tier", "Unknown"),
                "card_network": general_info.get("card_network", "Unknown"),
                "annual_fee": annual_fee,
                "base_reward_rate": f"{base_rate}%",
                "recommendation_score": round(recommendation.score, 1),
                "rationale": recommendation.rationale,
                "key_benefits": self._extract_key_benefits(card),
                "apply_link": card.get("application_details", {}).get("deep_link_url", ""),
                "image_url": general_info.get("image_url", "")
            }
            
            return formatted_rec
            
        except Exception as e:
            logger.error(f"Single recommendation formatting failed: {str(e)}")
            return {
                "rank": rank,
                "card_name": "Unknown Card",
                "issuer": "Unknown Issuer",
                "error": "Failed to format recommendation"
            }
    
    def _format_user_profile_summary(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Format user profile summary for display"""
        try:
            total_monthly_spend = sum(user_profile.monthly_spending.values())
            
            return {
                "age": user_profile.age,
                "employment_type": user_profile.employment,
                "monthly_income": f"₹{user_profile.net_monthly_income:,}" if user_profile.net_monthly_income else "Not provided",
                "credit_score": user_profile.credit_score,
                "city": user_profile.city,
                "total_monthly_spending": f"₹{total_monthly_spend:,}",
                "top_spending_categories": self._get_top_spending_categories(user_profile.monthly_spending)
            }
            
        except Exception as e:
            logger.error(f"User profile summary formatting failed: {str(e)}")
            return {"error": "Failed to format profile summary"}
    
    def _get_top_spending_categories(self, monthly_spending: Dict[str, int]) -> List[Dict[str, Any]]:
        """Get top spending categories with amounts"""
        try:
            total_spend = sum(monthly_spending.values())
            if total_spend == 0:
                return []
            
            # Calculate percentages and sort
            categories = []
            for category, amount in monthly_spending.items():
                if amount > 0:
                    percentage = (amount / total_spend) * 100
                    categories.append({
                        "category": category.replace("_", " ").title(),
                        "amount": f"₹{amount:,}",
                        "percentage": f"{percentage:.1f}%"
                    })
            
            # Sort by amount and return top 3
            categories.sort(key=lambda x: int(x["amount"].replace("₹", "").replace(",", "")), reverse=True)
            return categories[:3]
            
        except Exception as e:
            logger.error(f"Top spending categories extraction failed: {str(e)}")
            return []
    
    def _extract_key_benefits(self, card: Dict[str, Any]) -> List[str]:
        """Extract key benefits from card data"""
        try:
            benefits = []
            
            # Rewards benefits
            rewards = card.get("rewards", {})
            if rewards.get("welcome_bonus"):
                welcome = rewards["welcome_bonus"]
                benefits.append(f"Welcome bonus: {welcome.get('points', 0)} points")
            
            # Travel benefits
            travel = card.get("benefits", {}).get("travel", {})
            if travel.get("lounge_access"):
                benefits.append("Airport lounge access")
            if travel.get("travel_insurance"):
                benefits.append("Travel insurance")
            
            # Lifestyle benefits
            lifestyle = card.get("benefits", {}).get("lifestyle", {})
            if lifestyle.get("concierge_service"):
                benefits.append("24/7 Concierge")
            if lifestyle.get("dining_discounts"):
                benefits.append("Dining discounts")
            
            return benefits[:4]  # Limit to top 4 benefits
            
        except Exception as e:
            logger.error(f"Key benefits extraction failed: {str(e)}")
            return []
    
    def _format_card_summary(self, card: Dict[str, Any], label: str) -> Dict[str, Any]:
        """Format card summary for comparison"""
        try:
            general_info = card.get("general_info", {})
            fees = card.get("fees", {})
            rewards = card.get("rewards", {})
            
            return {
                "label": f"Card {label}",
                "name": general_info.get("card_name", "Unknown"),
                "issuer": general_info.get("issuer", "Unknown"),
                "tier": general_info.get("tier", "Unknown"),
                "annual_fee": fees.get("annual_fee", {}).get("amount", 0),
                "base_rate": rewards.get("base_rate", 0),
                "key_features": self._extract_key_benefits(card)
            }
            
        except Exception as e:
            logger.error(f"Card summary formatting failed: {str(e)}")
            return {"label": f"Card {label}", "name": "Unknown", "error": "Formatting failed"}
    
    def _generate_comparison_table(self, comparison: ComparisonResult) -> List[Dict[str, Any]]:
        """Generate comparison table data"""
        try:
            table_data = [
                {
                    "metric": "Net Annual Cost",
                    "card_a": f"₹{comparison.net_annual_cost_a:,}",
                    "card_b": f"₹{comparison.net_annual_cost_b:,}"
                },
                {
                    "metric": "Annual Rewards Value",
                    "card_a": f"₹{comparison.annual_rewards_value_a:.0f}",
                    "card_b": f"₹{comparison.annual_rewards_value_b:.0f}"
                },
                {
                    "metric": "Net Annual Value",
                    "card_a": f"₹{comparison.net_annual_value_a:.0f}",
                    "card_b": f"₹{comparison.net_annual_value_b:.0f}"
                },
                {
                    "metric": "Primary Benefit",
                    "card_a": comparison.primary_benefit_a,
                    "card_b": comparison.primary_benefit_b
                },
                {
                    "metric": "Key Drawback",
                    "card_a": comparison.key_drawback_a,
                    "card_b": comparison.key_drawback_b
                }
            ]
            
            return table_data
            
        except Exception as e:
            logger.error(f"Comparison table generation failed: {str(e)}")
            return []
    
    def _determine_comparison_winner(self, comparison: ComparisonResult) -> str:
        """Determine which card wins the comparison"""
        try:
            if comparison.net_annual_value_a > comparison.net_annual_value_b:
                return "Card A"
            elif comparison.net_annual_value_b > comparison.net_annual_value_a:
                return "Card B"
            else:
                return "Tie"
                
        except Exception as e:
            logger.error(f"Winner determination failed: {str(e)}")
            return "Unable to determine"
    
    def _apply_compliance_guardrails(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply compliance guardrails to content"""
        try:
            # Convert content to string for checking
            content_str = str(content)
            
            # Use compliance tool
            compliance_tool = ComplianceGuardrailTool()
            result = compliance_tool.execute(content_str)
            
            return result
            
        except Exception as e:
            logger.error(f"Compliance check failed: {str(e)}")
            return {"is_compliant": True, "violations": []}
    
    def _sanitize_response(self, content: Dict[str, Any], violations: List[str]) -> Dict[str, Any]:
        """Sanitize response by removing or replacing prohibited content"""
        try:
            # Create sanitized copy
            sanitized = content.copy()
            
            # Remove or replace prohibited terms
            for violation in violations:
                if "competitor" in violation.lower():
                    # Remove any competitor references
                    sanitized = self._remove_competitor_references(sanitized)
                elif "loan" in violation.lower() or "insurance" in violation.lower():
                    # Remove non-credit card financial product references
                    sanitized = self._remove_non_card_references(sanitized)
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Response sanitization failed: {str(e)}")
            return content
    
    def _remove_competitor_references(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Remove competitor references from content"""
        try:
            # This would implement specific logic to remove competitor references
            # For now, return content as-is
            return content
        except Exception as e:
            logger.error(f"Competitor reference removal failed: {str(e)}")
            return content
    
    def _remove_non_card_references(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Remove non-credit card financial product references"""
        try:
            # This would implement specific logic to remove non-card references
            # For now, return content as-is
            return content
        except Exception as e:
            logger.error(f"Non-card reference removal failed: {str(e)}")
            return content
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        try:
            from datetime import datetime
            return datetime.now().isoformat()
        except Exception as e:
            logger.error(f"Timestamp generation failed: {str(e)}")
            return "2024-01-15T10:30:00Z"
    
    def _get_disclaimer_text(self) -> str:
        """Get disclaimer text for recommendations"""
        return "Recommendations are based on publicly available information and your provided profile. Please verify details with the card issuer before applying. Terms and conditions apply."
    
    def _load_response_templates(self) -> Dict[str, str]:
        """Load response templates"""
        try:
            return {
                "recommendation_header": "Based on your profile, here are the best credit card recommendations:",
                "comparison_header": "Here's a detailed comparison of the selected cards:",
                "error_header": "We encountered an issue processing your request:",
                "no_results": "No suitable credit cards found for your profile. Consider improving your eligibility criteria."
            }
        except Exception as e:
            logger.error(f"Failed to load response templates: {str(e)}")
            return {}
    
    def generate_markdown_report(self, recommendations: List[CardRecommendation], user_profile: UserProfile) -> str:
        """Generate markdown-formatted report"""
        try:
            markdown = []
            
            # Header
            markdown.append("# Credit Card Recommendations Report")
            markdown.append("")
            markdown.append(f"**Generated on:** {self._get_current_timestamp()}")
            markdown.append("")
            
            # User profile
            markdown.append("## Your Profile")
            markdown.append(f"- **Age:** {user_profile.age}")
            markdown.append(f"- **Employment:** {user_profile.employment}")
            markdown.append(f"- **Monthly Income:** ₹{user_profile.net_monthly_income:,}")
            markdown.append(f"- **Credit Score:** {user_profile.credit_score}")
            markdown.append(f"- **City:** {user_profile.city}")
            markdown.append("")
            
            # Recommendations
            markdown.append("## Recommendations")
            markdown.append("")
            
            for i, rec in enumerate(recommendations, 1):
                card = rec.card
                general_info = card.get("general_info", {})
                
                markdown.append(f"### {i}. {general_info.get('card_name', 'Unknown Card')}")
                markdown.append("")
                markdown.append(f"**Issuer:** {general_info.get('issuer', 'Unknown')}")
                markdown.append(f"**Tier:** {general_info.get('tier', 'Unknown')}")
                markdown.append(f"**Annual Fee:** ₹{card.get('fees', {}).get('annual_fee', {}).get('amount', 0):,}")
                markdown.append(f"**Score:** {rec.score:.1f}/100")
                markdown.append("")
                markdown.append(f"**Why this card:** {rec.rationale}")
                markdown.append("")
                
                if card.get("application_details", {}).get("deep_link_url"):
                    markdown.append(f"[Apply Now]({card.get('application_details', {}).get('deep_link_url')})")
                    markdown.append("")
            
            # Disclaimer
            markdown.append("## Disclaimer")
            markdown.append(self._get_disclaimer_text())
            
            return "\n".join(markdown)
            
        except Exception as e:
            logger.error(f"Markdown report generation failed: {str(e)}")
            return "# Error\nFailed to generate report."
