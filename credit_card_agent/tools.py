"""
Tools for Credit Card Agent System
External API integrations and utility functions
"""

import requests
import json
from typing import List, Dict, Any, Optional
from google.adk.tools import BaseTool
from pydantic import Field
import logging

logger = logging.getLogger(__name__)


class CreditScoreCheckTool(BaseTool):
    """Tool for checking credit score via external API"""
    
    def __init__(self):
        super().__init__(
            name="credit_score_check",
            description="Check user's credit score using external credit bureau API"
        )
    
    def execute(self, user_id: str, api_key: str) -> Dict[str, Any]:
        """
        Check credit score for a user
        
        Args:
            user_id: Unique user identifier
            api_key: API key for credit bureau service
            
        Returns:
            Dictionary containing credit score and related information
        """
        try:
            # Mock implementation - replace with actual API call
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # In production, this would be a real API call
            # response = requests.get(f"https://api.creditbureau.com/score/{user_id}", headers=headers)
            
            # Mock response for demonstration
            mock_response = {
                "credit_score": 780,
                "score_range": "Excellent",
                "last_updated": "2024-01-15",
                "bureau": "CIBIL"
            }
            
            return {
                "success": True,
                "data": mock_response
            }
            
        except Exception as e:
            logger.error(f"Credit score check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class CardDataIngestionTool(BaseTool):
    """Tool for ingesting credit card data from external sources"""
    
    def __init__(self):
        super().__init__(
            name="card_data_ingestion",
            description="Fetch and process credit card data from external APIs"
        )
    
    def execute(self, source: str = "zetapp", api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest credit card data from external sources
        
        Args:
            source: Data source identifier (zetapp, bank_apis, etc.)
            api_key: API key for the data source
            
        Returns:
            Dictionary containing ingested card data
        """
        try:
            if source == "zetapp":
                return self._ingest_from_zetapp(api_key)
            elif source == "bank_apis":
                return self._ingest_from_bank_apis(api_key)
            else:
                return self._ingest_mock_data()
                
        except Exception as e:
            logger.error(f"Card data ingestion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _ingest_from_zetapp(self, api_key: Optional[str]) -> Dict[str, Any]:
        """Ingest data from ZetApp API"""
        # Mock implementation - replace with actual ZetApp API integration
        mock_cards = [
            {
                "card_id": "hdfc_moneyback_plus",
                "general_info": {
                    "card_name": "HDFC MoneyBack+ Credit Card",
                    "issuer": "HDFC Bank",
                    "card_network": "Visa",
                    "tier": "Entry-Level",
                    "image_url": "https://example.com/hdfc_moneyback.jpg"
                },
                "eligibility": {
                    "min_age": 21,
                    "max_age": 65,
                    "residency": "Resident Indian",
                    "credit_score": {
                        "minimum_required": 750,
                        "preferred": 780
                    },
                    "income_requirements": {
                        "salaried_monthly": 20000,
                        "self_employed_annual": 600000
                    },
                    "serviceable_locations": ["Mumbai", "Delhi", "Bangalore", "Chennai"]
                },
                "fees": {
                    "joining_fee": 500,
                    "annual_fee": {
                        "amount": 500,
                        "waiver_condition": {
                            "spend_threshold": 50000,
                            "description": "Waived on annual spend of ₹50,000"
                        }
                    },
                    "interest_rate_apr": 3.5,
                    "late_payment_charges": [
                        {"min_amount": 100, "max_amount": 500, "charge": 100},
                        {"min_amount": 500, "max_amount": 1000, "charge": 200}
                    ],
                    "cash_advance_fee": "2.5% of amount",
                    "forex_markup": 3.5
                },
                "rewards": {
                    "base_rate": 1.0,
                    "earning_rates": [
                        {"category": "groceries", "rate": 2.0, "cap": 10000},
                        {"category": "dining", "rate": 2.0, "cap": 5000},
                        {"category": "online_shopping", "rate": 1.0, "cap": None}
                    ],
                    "welcome_bonus": {
                        "points": 2000,
                        "value": 1000,
                        "condition": "Spend ₹5,000 in first 90 days"
                    },
                    "redemption": {
                        "cashback_value_per_point": 0.5,
                        "airmiles_partners": [],
                        "transfer_ratio": "1:1"
                    }
                },
                "benefits": {
                    "travel": {
                        "lounge_access": {
                            "domestic_visits_per_quarter": 2,
                            "international_visits_per_year": 0,
                            "guest_policy": "No guest access"
                        }
                    },
                    "lifestyle": {
                        "dining_discounts": "Up to 20% off at partner restaurants",
                        "movie_offers": "Buy 1 Get 1 free on movie tickets"
                    }
                },
                "application_details": {
                    "deep_link_url": "https://hdfcbank.com/credit-cards/moneyback-plus"
                }
            }
        ]
        
        return {
            "success": True,
            "data": mock_cards,
            "source": "zetapp",
            "count": len(mock_cards)
        }
    
    def _ingest_from_bank_apis(self, api_key: Optional[str]) -> Dict[str, Any]:
        """Ingest data from individual bank APIs"""
        # Mock implementation for bank APIs
        return {
            "success": True,
            "data": [],
            "source": "bank_apis",
            "count": 0
        }
    
    def _ingest_mock_data(self) -> Dict[str, Any]:
        """Fallback to mock data when external sources fail"""
        return self._ingest_from_zetapp(None)


class EligibilityRuleEngineTool(BaseTool):
    """Tool for applying eligibility rules to filter credit cards"""
    
    def __init__(self):
        super().__init__(
            name="eligibility_rule_engine",
            description="Apply eligibility rules to filter credit cards based on user profile"
        )
    
    def execute(self, user_profile: Dict[str, Any], cards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply eligibility rules to filter cards
        
        Args:
            user_profile: User's profile data
            cards: List of credit cards to filter
            
        Returns:
            Dictionary containing eligible cards
        """
        try:
            eligible_cards = []
            
            for card in cards:
                if self._check_eligibility(user_profile, card):
                    eligible_cards.append(card)
            
            return {
                "success": True,
                "data": eligible_cards,
                "total_cards": len(cards),
                "eligible_cards": len(eligible_cards)
            }
            
        except Exception as e:
            logger.error(f"Eligibility check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _check_eligibility(self, user_profile: Dict[str, Any], card: Dict[str, Any]) -> bool:
        """Check if user is eligible for a specific card"""
        try:
            eligibility = card.get("eligibility", {})
            
            # Check age
            user_age = user_profile.get("age", 0)
            min_age = eligibility.get("min_age", 0)
            max_age = eligibility.get("max_age")
            
            if user_age < min_age:
                return False
            if max_age and user_age > max_age:
                return False
            
            # Check credit score
            user_credit_score = user_profile.get("credit_score", 0)
            required_score = eligibility.get("credit_score", {}).get("minimum_required", 0)
            
            if user_credit_score < required_score:
                return False
            
            # Check income requirements
            employment = user_profile.get("employment", "")
            income_reqs = eligibility.get("income_requirements", {})
            
            if employment == "salaried":
                monthly_income = user_profile.get("net_monthly_income", 0)
                required_monthly = income_reqs.get("salaried_monthly", 0)
                if monthly_income < required_monthly:
                    return False
            elif employment == "self_employed":
                annual_income = user_profile.get("annual_income", 0)
                required_annual = income_reqs.get("self_employed_annual", 0)
                if annual_income < required_annual:
                    return False
            
            # Check location
            user_city = user_profile.get("city", "")
            serviceable_locations = eligibility.get("serviceable_locations", [])
            if serviceable_locations and user_city not in serviceable_locations:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking eligibility for card {card.get('card_id', 'unknown')}: {str(e)}")
            return False


class ComplianceGuardrailTool(BaseTool):
    """Tool for enforcing compliance guardrails on generated content"""
    
    def __init__(self):
        super().__init__(
            name="compliance_guardrail",
            description="Check generated content for compliance violations"
        )
    
    def execute(self, content: str) -> Dict[str, Any]:
        """
        Check content for compliance violations
        
        Args:
            content: Text content to check
            
        Returns:
            Dictionary containing compliance check results
        """
        try:
            prohibited_keywords = [
                "loan", "insurance", "mutual fund", "investment", "savings account",
                "fixed deposit", "fd", "rd", "sip", "nps", "ppf", "elss",
                "competitor", "other platform", "alternative service"
            ]
            
            violations = []
            content_lower = content.lower()
            
            for keyword in prohibited_keywords:
                if keyword in content_lower:
                    violations.append(keyword)
            
            is_compliant = len(violations) == 0
            
            return {
                "success": True,
                "is_compliant": is_compliant,
                "violations": violations,
                "content_length": len(content)
            }
            
        except Exception as e:
            logger.error(f"Compliance check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class RewardsCalculatorTool(BaseTool):
    """Tool for calculating potential rewards value"""
    
    def __init__(self):
        super().__init__(
            name="rewards_calculator",
            description="Calculate potential annual rewards value for a credit card"
        )
    
    def execute(self, card: Dict[str, Any], user_spending: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculate annual rewards value for a card based on user spending
        
        Args:
            card: Credit card data
            user_spending: User's monthly spending by category
            
        Returns:
            Dictionary containing calculated rewards value
        """
        try:
            rewards = card.get("rewards", {})
            earning_rates = rewards.get("earning_rates", [])
            base_rate = rewards.get("base_rate", 1.0)
            cashback_value = rewards.get("redemption", {}).get("cashback_value_per_point", 0.5)
            
            total_monthly_rewards = 0
            category_breakdown = {}
            
            # Calculate rewards for each spending category
            for category, monthly_spend in user_spending.items():
                # Find matching earning rate
                category_rate = base_rate
                for rate_info in earning_rates:
                    if rate_info.get("category") == category:
                        category_rate = rate_info.get("rate", base_rate)
                        break
                
                # Apply monthly cap if exists
                monthly_cap = None
                for rate_info in earning_rates:
                    if rate_info.get("category") == category and rate_info.get("cap"):
                        monthly_cap = rate_info.get("cap")
                        break
                
                if monthly_cap:
                    capped_spend = min(monthly_spend, monthly_cap)
                else:
                    capped_spend = monthly_spend
                
                monthly_rewards = capped_spend * (category_rate / 100)
                total_monthly_rewards += monthly_rewards
                
                category_breakdown[category] = {
                    "monthly_spend": monthly_spend,
                    "rate": category_rate,
                    "monthly_rewards": monthly_rewards,
                    "capped": monthly_cap is not None and monthly_spend > monthly_cap
                }
            
            # Calculate annual values
            annual_rewards_points = total_monthly_rewards * 12
            annual_cashback_value = annual_rewards_points * cashback_value
            
            # Add welcome bonus if applicable
            welcome_bonus = rewards.get("welcome_bonus", {})
            if welcome_bonus:
                annual_cashback_value += welcome_bonus.get("value", 0)
            
            return {
                "success": True,
                "data": {
                    "monthly_rewards_points": total_monthly_rewards,
                    "annual_rewards_points": annual_rewards_points,
                    "annual_cashback_value": annual_cashback_value,
                    "category_breakdown": category_breakdown,
                    "welcome_bonus_included": bool(welcome_bonus)
                }
            }
            
        except Exception as e:
            logger.error(f"Rewards calculation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
