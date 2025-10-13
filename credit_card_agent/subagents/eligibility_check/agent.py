"""
EligibilityCheckAgent - Applies deterministic eligibility rules
Primary gatekeeper for credit card eligibility assessment
"""

import logging
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.tools import BaseTool

from ...models import UserProfile, CreditCard, EmploymentType, ResidencyType
from ...tools import EligibilityRuleEngineTool, CreditScoreCheckTool

logger = logging.getLogger(__name__)


class EligibilityCheckAgent(Agent):
    """
    Eligibility check agent that applies deterministic rules
    to determine user eligibility for credit cards.
    """
    
    def __init__(self, **kwargs):
        name = kwargs.pop('name', 'eligibility_check')
        super().__init__(name=name, **kwargs)
        self.tools = [EligibilityRuleEngineTool(), CreditScoreCheckTool()]
        self._eligibility_rules = self._load_eligibility_rules()
    
    def check_eligibility(self, user_profile: UserProfile, cards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check eligibility for multiple credit cards
        
        Args:
            user_profile: User's profile data
            cards: List of credit cards to check
            
        Returns:
            Dictionary containing eligible cards and analysis
        """
        try:
            eligible_cards = []
            ineligible_cards = []
            
            for card in cards:
                eligibility_result = self._check_single_card_eligibility(user_profile, card)
                
                if eligibility_result["is_eligible"]:
                    eligible_cards.append({
                        "card": card,
                        "eligibility_details": eligibility_result
                    })
                else:
                    ineligible_cards.append({
                        "card": card,
                        "rejection_reasons": eligibility_result["rejection_reasons"]
                    })
            
            # Sort eligible cards by recommendation score
            eligible_cards.sort(key=lambda x: x["eligibility_details"]["score"], reverse=True)
            
            logger.info(f"Eligibility check completed: {len(eligible_cards)} eligible, {len(ineligible_cards)} ineligible")
            
            return {
                "success": True,
                "eligible_cards": [item["card"] for item in eligible_cards],
                "ineligible_cards": ineligible_cards,
                "total_checked": len(cards),
                "eligibility_rate": len(eligible_cards) / len(cards) if cards else 0,
                "analysis": {
                    "primary_filters": self._analyze_primary_filters(user_profile, ineligible_cards),
                    "recommendations": self._generate_eligibility_recommendations(user_profile, ineligible_cards)
                }
            }
            
        except Exception as e:
            logger.error(f"Eligibility check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "eligible_cards": [],
                "ineligible_cards": []
            }
    
    def _check_single_card_eligibility(self, user_profile: UserProfile, card: Dict[str, Any]) -> Dict[str, Any]:
        """Check eligibility for a single credit card"""
        try:
            rejection_reasons = []
            score = 0
            
            # Get card eligibility criteria
            eligibility = card.get("eligibility", {})
            
            # Check age
            age_result = self._check_age_eligibility(user_profile.age, eligibility)
            if not age_result["eligible"]:
                rejection_reasons.append(age_result["reason"])
            else:
                score += age_result.get("score", 0)
            
            # Check credit score
            credit_result = self._check_credit_score_eligibility(user_profile.credit_score, eligibility)
            if not credit_result["eligible"]:
                rejection_reasons.append(credit_result["reason"])
            else:
                score += credit_result.get("score", 0)
            
            # Check income
            income_result = self._check_income_eligibility(user_profile, eligibility)
            if not income_result["eligible"]:
                rejection_reasons.append(income_result["reason"])
            else:
                score += income_result.get("score", 0)
            
            # Check residency
            residency_result = self._check_residency_eligibility(user_profile, eligibility)
            if not residency_result["eligible"]:
                rejection_reasons.append(residency_result["reason"])
            else:
                score += residency_result.get("score", 0)
            
            # Check location
            location_result = self._check_location_eligibility(user_profile.city, eligibility)
            if not location_result["eligible"]:
                rejection_reasons.append(location_result["reason"])
            else:
                score += location_result.get("score", 0)
            
            is_eligible = len(rejection_reasons) == 0
            
            return {
                "is_eligible": is_eligible,
                "rejection_reasons": rejection_reasons,
                "score": score,
                "card_id": card.get("card_id"),
                "card_name": card.get("general_info", {}).get("card_name")
            }
            
        except Exception as e:
            logger.error(f"Single card eligibility check failed: {str(e)}")
            return {
                "is_eligible": False,
                "rejection_reasons": [f"Error checking eligibility: {str(e)}"],
                "score": 0,
                "card_id": card.get("card_id", "unknown"),
                "card_name": card.get("general_info", {}).get("card_name", "Unknown")
            }
    
    def _check_age_eligibility(self, user_age: int, eligibility: Dict[str, Any]) -> Dict[str, Any]:
        """Check age eligibility"""
        try:
            min_age = eligibility.get("min_age", 18)
            max_age = eligibility.get("max_age")
            
            if user_age < min_age:
                return {
                    "eligible": False,
                    "reason": f"Age {user_age} is below minimum required age {min_age}",
                    "score": 0
                }
            
            if max_age and user_age > max_age:
                return {
                    "eligible": False,
                    "reason": f"Age {user_age} exceeds maximum allowed age {max_age}",
                    "score": 0
                }
            
            # Calculate age score (closer to middle of range gets higher score)
            if max_age:
                age_range = max_age - min_age
                age_position = (user_age - min_age) / age_range
                score = 10 * (1 - abs(age_position - 0.5) * 2)  # Peak at middle of range
            else:
                score = 10  # No upper limit, full score
            
            return {
                "eligible": True,
                "reason": f"Age {user_age} meets requirements",
                "score": score
            }
            
        except Exception as e:
            logger.error(f"Age eligibility check failed: {str(e)}")
            return {
                "eligible": False,
                "reason": f"Error checking age eligibility: {str(e)}",
                "score": 0
            }
    
    def _check_credit_score_eligibility(self, user_credit_score: int, eligibility: Dict[str, Any]) -> Dict[str, Any]:
        """Check credit score eligibility"""
        try:
            credit_score_req = eligibility.get("credit_score", {})
            min_required = credit_score_req.get("minimum_required", 750)
            preferred = credit_score_req.get("preferred", 780)
            
            if user_credit_score < min_required:
                return {
                    "eligible": False,
                    "reason": f"Credit score {user_credit_score} below minimum required {min_required}",
                    "score": 0
                }
            
            # Calculate credit score bonus
            if user_credit_score >= preferred:
                score = 15  # Excellent score
            elif user_credit_score >= min_required + 20:
                score = 10  # Good score
            else:
                score = 5   # Minimum qualifying score
            
            return {
                "eligible": True,
                "reason": f"Credit score {user_credit_score} meets requirements",
                "score": score
            }
            
        except Exception as e:
            logger.error(f"Credit score eligibility check failed: {str(e)}")
            return {
                "eligible": False,
                "reason": f"Error checking credit score: {str(e)}",
                "score": 0
            }
    
    def _check_income_eligibility(self, user_profile: UserProfile, eligibility: Dict[str, Any]) -> Dict[str, Any]:
        """Check income eligibility based on employment type"""
        try:
            income_reqs = eligibility.get("income_requirements", {})
            employment = user_profile.employment
            
            if employment == EmploymentType.SALARIED:
                monthly_income = user_profile.net_monthly_income
                required_monthly = income_reqs.get("salaried_monthly", 0)
                
                if not monthly_income:
                    return {
                        "eligible": False,
                        "reason": "Monthly income not provided for salaried applicant",
                        "score": 0
                    }
                
                if monthly_income < required_monthly:
                    return {
                        "eligible": False,
                        "reason": f"Monthly income ₹{monthly_income:,} below required ₹{required_monthly:,}",
                        "score": 0
                    }
                
                # Calculate income score
                income_ratio = monthly_income / required_monthly
                if income_ratio >= 2.0:
                    score = 15  # High income
                elif income_ratio >= 1.5:
                    score = 12  # Good income
                else:
                    score = 8   # Minimum qualifying income
                
                return {
                    "eligible": True,
                    "reason": f"Monthly income ₹{monthly_income:,} meets requirements",
                    "score": score
                }
            
            elif employment == EmploymentType.SELF_EMPLOYED:
                annual_income = user_profile.annual_income
                required_annual = income_reqs.get("self_employed_annual", 0)
                
                if not annual_income:
                    return {
                        "eligible": False,
                        "reason": "Annual income not provided for self-employed applicant",
                        "score": 0
                    }
                
                if annual_income < required_annual:
                    return {
                        "eligible": False,
                        "reason": f"Annual income ₹{annual_income:,} below required ₹{required_annual:,}",
                        "score": 0
                    }
                
                # Calculate income score
                income_ratio = annual_income / required_annual
                if income_ratio >= 2.0:
                    score = 15  # High income
                elif income_ratio >= 1.5:
                    score = 12  # Good income
                else:
                    score = 8   # Minimum qualifying income
                
                return {
                    "eligible": True,
                    "reason": f"Annual income ₹{annual_income:,} meets requirements",
                    "score": score
                }
            
            else:
                return {
                    "eligible": False,
                    "reason": f"Unknown employment type: {employment}",
                    "score": 0
                }
            
        except Exception as e:
            logger.error(f"Income eligibility check failed: {str(e)}")
            return {
                "eligible": False,
                "reason": f"Error checking income eligibility: {str(e)}",
                "score": 0
            }
    
    def _check_residency_eligibility(self, user_profile: UserProfile, eligibility: Dict[str, Any]) -> Dict[str, Any]:
        """Check residency eligibility"""
        try:
            required_residency = eligibility.get("residency", ResidencyType.RESIDENT_INDIAN)
            
            # In a real implementation, this would check actual residency status
            # For now, assume all users are Resident Indians
            user_residency = ResidencyType.RESIDENT_INDIAN
            
            if user_residency != required_residency:
                return {
                    "eligible": False,
                    "reason": f"Residency requirement not met: {required_residency}",
                    "score": 0
                }
            
            return {
                "eligible": True,
                "reason": f"Residency status meets requirements",
                "score": 5
            }
            
        except Exception as e:
            logger.error(f"Residency eligibility check failed: {str(e)}")
            return {
                "eligible": False,
                "reason": f"Error checking residency: {str(e)}",
                "score": 0
            }
    
    def _check_location_eligibility(self, user_city: str, eligibility: Dict[str, Any]) -> Dict[str, Any]:
        """Check location eligibility"""
        try:
            serviceable_locations = eligibility.get("serviceable_locations", [])
            
            if not serviceable_locations:
                # No location restrictions
                return {
                    "eligible": True,
                    "reason": "No location restrictions",
                    "score": 5
                }
            
            if user_city in serviceable_locations:
                return {
                    "eligible": True,
                    "reason": f"City {user_city} is serviceable",
                    "score": 5
                }
            else:
                return {
                    "eligible": False,
                    "reason": f"City {user_city} not in serviceable locations: {serviceable_locations}",
                    "score": 0
                }
            
        except Exception as e:
            logger.error(f"Location eligibility check failed: {str(e)}")
            return {
                "eligible": False,
                "reason": f"Error checking location: {str(e)}",
                "score": 0
            }
    
    def _analyze_primary_filters(self, user_profile: UserProfile, ineligible_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze primary rejection reasons"""
        try:
            rejection_counts = {}
            
            for item in ineligible_cards:
                for reason in item["rejection_reasons"]:
                    # Categorize rejection reasons
                    if "age" in reason.lower():
                        rejection_counts["age"] = rejection_counts.get("age", 0) + 1
                    elif "credit score" in reason.lower():
                        rejection_counts["credit_score"] = rejection_counts.get("credit_score", 0) + 1
                    elif "income" in reason.lower():
                        rejection_counts["income"] = rejection_counts.get("income", 0) + 1
                    elif "location" in reason.lower():
                        rejection_counts["location"] = rejection_counts.get("location", 0) + 1
                    else:
                        rejection_counts["other"] = rejection_counts.get("other", 0) + 1
            
            return {
                "total_rejections": len(ineligible_cards),
                "rejection_breakdown": rejection_counts,
                "primary_issue": max(rejection_counts, key=rejection_counts.get) if rejection_counts else None
            }
            
        except Exception as e:
            logger.error(f"Primary filter analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def _generate_eligibility_recommendations(self, user_profile: UserProfile, ineligible_cards: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations to improve eligibility"""
        try:
            recommendations = []
            
            # Analyze rejection patterns
            analysis = self._analyze_primary_filters(user_profile, ineligible_cards)
            primary_issue = analysis.get("primary_issue")
            
            if primary_issue == "credit_score":
                recommendations.append("Consider improving your credit score by paying bills on time and reducing credit utilization")
                recommendations.append("Look for secured credit cards to build credit history")
            
            elif primary_issue == "income":
                if user_profile.employment == EmploymentType.SALARIED:
                    recommendations.append("Consider cards with lower income requirements")
                    recommendations.append("Look for entry-level cards designed for lower income brackets")
                else:
                    recommendations.append("Ensure your ITR shows consistent annual income above card requirements")
            
            elif primary_issue == "age":
                if user_profile.age < 21:
                    recommendations.append("Consider waiting until you turn 21 for most credit cards")
                    recommendations.append("Look for student credit cards or secured cards")
                else:
                    recommendations.append("Consider cards with higher age limits")
            
            elif primary_issue == "location":
                recommendations.append("Consider cards available in your city")
                recommendations.append("Check if the card issuer has branches in your area")
            
            if not recommendations:
                recommendations.append("Consider applying for secured credit cards to build credit history")
                recommendations.append("Look for cards with more flexible eligibility criteria")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return ["Please contact customer support for personalized eligibility guidance"]
    
    def _load_eligibility_rules(self) -> Dict[str, Any]:
        """Load eligibility rules configuration"""
        try:
            # In a real implementation, this would load from a configuration file or database
            return {
                "credit_score_thresholds": {
                    "excellent": 780,
                    "good": 750,
                    "fair": 700,
                    "poor": 650
                },
                "income_multipliers": {
                    "high": 2.0,
                    "good": 1.5,
                    "minimum": 1.0
                },
                "age_preferences": {
                    "optimal_range": [25, 45],
                    "penalty_threshold": 60
                }
            }
        except Exception as e:
            logger.error(f"Failed to load eligibility rules: {str(e)}")
            return {}
