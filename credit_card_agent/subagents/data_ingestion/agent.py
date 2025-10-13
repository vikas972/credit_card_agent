"""
DataIngestionAgent - Manages credit card data from multiple sources
Handles data collection, normalization, and validation
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from google.adk.agents import Agent
from google.adk.tools import BaseTool

from ...models import CreditCard, CardNetwork, CardTier, ResidencyType
from ...tools import CardDataIngestionTool

logger = logging.getLogger(__name__)


class DataIngestionAgent(Agent):
    """
    Data ingestion agent responsible for building and maintaining
    the comprehensive knowledge base of credit card information.
    """
    
    def __init__(self, **kwargs):
        name = kwargs.pop('name', 'data_ingestion')
        super().__init__(name=name, **kwargs)
        self.tools = [CardDataIngestionTool()]
        self._data_cache = {}
        self._last_update = {}
        self._cache_ttl = 3600  # 1 hour cache TTL
    
    def ingest_all_sources(self) -> Dict[str, Any]:
        """
        Ingest data from all available sources
        
        Returns:
            Dictionary containing aggregated card data
        """
        try:
            all_cards = []
            sources_used = []
            
            # Ingest from ZetApp
            zetapp_result = self._ingest_from_zetapp()
            if zetapp_result["success"]:
                all_cards.extend(zetapp_result["data"])
                sources_used.append("zetapp")
            
            # Ingest from bank APIs
            bank_apis_result = self._ingest_from_bank_apis()
            if bank_apis_result["success"]:
                all_cards.extend(bank_apis_result["data"])
                sources_used.append("bank_apis")
            
            # Ingest from internal database
            internal_result = self._ingest_from_internal_db()
            if internal_result["success"]:
                all_cards.extend(internal_result["data"])
                sources_used.append("internal_db")
            
            # Deduplicate and validate cards
            unique_cards = self._deduplicate_cards(all_cards)
            validated_cards = self._validate_cards(unique_cards)
            
            # Update cache
            self._data_cache["cards"] = validated_cards
            self._data_cache["last_update"] = datetime.now().isoformat()
            self._data_cache["sources"] = sources_used
            
            logger.info(f"Successfully ingested {len(validated_cards)} cards from {len(sources_used)} sources")
            
            return {
                "success": True,
                "data": validated_cards,
                "count": len(validated_cards),
                "sources": sources_used,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Data ingestion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
    
    def _ingest_from_zetapp(self) -> Dict[str, Any]:
        """Ingest data from ZetApp API"""
        try:
            ingestion_tool = CardDataIngestionTool()
            result = ingestion_tool.execute(source="zetapp")
            return result
        except Exception as e:
            logger.error(f"ZetApp ingestion failed: {str(e)}")
            return {"success": False, "error": str(e), "data": []}
    
    def _ingest_from_bank_apis(self) -> Dict[str, Any]:
        """Ingest data from individual bank APIs"""
        try:
            # Mock implementation for bank APIs
            bank_cards = [
                {
                    "card_id": "sbi_simplyclick",
                    "general_info": {
                        "card_name": "SBI SimplyCLICK Credit Card",
                        "issuer": "State Bank of India",
                        "card_network": "Visa",
                        "tier": "Entry-Level",
                        "image_url": "https://example.com/sbi_simplyclick.jpg"
                    },
                    "eligibility": {
                        "min_age": 21,
                        "max_age": 65,
                        "residency": "Resident Indian",
                        "credit_score": {
                            "minimum_required": 730,
                            "preferred": 750
                        },
                        "income_requirements": {
                            "salaried_monthly": 15000,
                            "self_employed_annual": 450000
                        },
                        "serviceable_locations": ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"]
                    },
                    "fees": {
                        "joining_fee": 499,
                        "annual_fee": {
                            "amount": 499,
                            "waiver_condition": {
                                "spend_threshold": 100000,
                                "description": "Waived on annual spend of ₹1,00,000"
                            }
                        },
                        "interest_rate_apr": 3.5,
                        "late_payment_charges": [
                            {"min_amount": 100, "max_amount": 500, "charge": 100}
                        ],
                        "cash_advance_fee": "2.5% of amount",
                        "forex_markup": 3.5
                    },
                    "rewards": {
                        "base_rate": 1.0,
                        "earning_rates": [
                            {"category": "online_shopping", "rate": 5.0, "cap": 10000},
                            {"category": "groceries", "rate": 2.0, "cap": 5000},
                            {"category": "dining", "rate": 1.0, "cap": None}
                        ],
                        "welcome_bonus": {
                            "points": 1000,
                            "value": 500,
                            "condition": "Spend ₹2,000 in first 90 days"
                        },
                        "redemption": {
                            "cashback_value_per_point": 0.5,
                            "airmiles_partners": [],
                            "transfer_ratio": "1:1"
                        }
                    },
                    "benefits": {
                        "lifestyle": {
                            "dining_discounts": "Up to 15% off at partner restaurants",
                            "movie_offers": "Buy 1 Get 1 free on movie tickets"
                        }
                    },
                    "application_details": {
                        "deep_link_url": "https://sbi.co.in/credit-cards/simplyclick"
                    }
                }
            ]
            
            return {
                "success": True,
                "data": bank_cards,
                "source": "bank_apis"
            }
            
        except Exception as e:
            logger.error(f"Bank APIs ingestion failed: {str(e)}")
            return {"success": False, "error": str(e), "data": []}
    
    def _ingest_from_internal_db(self) -> Dict[str, Any]:
        """Ingest data from internal database"""
        try:
            # Mock implementation for internal database
            internal_cards = [
                {
                    "card_id": "axis_atlas",
                    "general_info": {
                        "card_name": "Axis Bank ATLAS Credit Card",
                        "issuer": "Axis Bank",
                        "card_network": "Mastercard",
                        "tier": "Premium",
                        "image_url": "https://example.com/axis_atlas.jpg"
                    },
                    "eligibility": {
                        "min_age": 18,
                        "max_age": 70,
                        "residency": "Resident Indian",
                        "credit_score": {
                            "minimum_required": 750,
                            "preferred": 780
                        },
                        "income_requirements": {
                            "salaried_monthly": 100000,
                            "self_employed_annual": 1500000
                        },
                        "serviceable_locations": ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Pune"]
                    },
                    "fees": {
                        "joining_fee": 5000,
                        "annual_fee": {
                            "amount": 5000,
                            "waiver_condition": {
                                "spend_threshold": 500000,
                                "description": "Waived on annual spend of ₹5,00,000"
                            }
                        },
                        "interest_rate_apr": 3.5,
                        "late_payment_charges": [
                            {"min_amount": 100, "max_amount": 1000, "charge": 100}
                        ],
                        "cash_advance_fee": "2.5% of amount",
                        "forex_markup": 3.5
                    },
                    "rewards": {
                        "base_rate": 2.0,
                        "earning_rates": [
                            {"category": "travel_flights_hotels", "rate": 4.0, "cap": 50000},
                            {"category": "dining", "rate": 3.0, "cap": 10000},
                            {"category": "groceries", "rate": 2.0, "cap": 20000}
                        ],
                        "welcome_bonus": {
                            "points": 10000,
                            "value": 5000,
                            "condition": "Spend ₹50,000 in first 90 days"
                        },
                        "milestone_benefits": [
                            {
                                "milestone": "Annual spend ₹5,00,000",
                                "benefit": "Complimentary domestic flight ticket"
                            }
                        ],
                        "redemption": {
                            "cashback_value_per_point": 0.5,
                            "airmiles_partners": ["Air India", "Vistara", "IndiGo"],
                            "transfer_ratio": "1:1"
                        }
                    },
                    "benefits": {
                        "travel": {
                            "lounge_access": {
                                "domestic_visits_per_quarter": 4,
                                "international_visits_per_year": 2,
                                "guest_policy": "1 guest per visit"
                            },
                            "travel_insurance": "Up to ₹50,00,000 travel insurance"
                        },
                        "lifestyle": {
                            "concierge_service": True,
                            "dining_discounts": "Up to 25% off at partner restaurants"
                        },
                        "insurance": {
                            "fraud_liability_cover": "Zero liability on fraudulent transactions",
                            "personal_accident_cover": "Up to ₹10,00,000"
                        }
                    },
                    "application_details": {
                        "deep_link_url": "https://axisbank.com/credit-cards/atlas"
                    }
                }
            ]
            
            return {
                "success": True,
                "data": internal_cards,
                "source": "internal_db"
            }
            
        except Exception as e:
            logger.error(f"Internal DB ingestion failed: {str(e)}")
            return {"success": False, "error": str(e), "data": []}
    
    def _deduplicate_cards(self, cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate cards based on card_id"""
        try:
            seen_ids = set()
            unique_cards = []
            
            for card in cards:
                card_id = card.get("card_id")
                if card_id and card_id not in seen_ids:
                    seen_ids.add(card_id)
                    unique_cards.append(card)
                elif not card_id:
                    logger.warning("Card without ID found, skipping")
            
            logger.info(f"Deduplicated {len(cards)} cards to {len(unique_cards)} unique cards")
            return unique_cards
            
        except Exception as e:
            logger.error(f"Card deduplication failed: {str(e)}")
            return cards
    
    def _validate_cards(self, cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate card data structure and content"""
        try:
            validated_cards = []
            
            for card in cards:
                if self._validate_single_card(card):
                    validated_cards.append(card)
                else:
                    logger.warning(f"Invalid card data for {card.get('card_id', 'unknown')}")
            
            logger.info(f"Validated {len(validated_cards)} out of {len(cards)} cards")
            return validated_cards
            
        except Exception as e:
            logger.error(f"Card validation failed: {str(e)}")
            return cards
    
    def _validate_single_card(self, card: Dict[str, Any]) -> bool:
        """Validate a single card's data structure"""
        try:
            required_fields = [
                "card_id",
                "general_info.card_name",
                "general_info.issuer",
                "eligibility.min_age",
                "fees.annual_fee.amount"
            ]
            
            for field in required_fields:
                keys = field.split(".")
                current = card
                for key in keys:
                    if not isinstance(current, dict) or key not in current:
                        return False
                    current = current[key]
            
            return True
            
        except Exception as e:
            logger.error(f"Single card validation failed: {str(e)}")
            return False
    
    def get_cached_data(self) -> Dict[str, Any]:
        """Get cached card data if still valid"""
        try:
            if not self._data_cache or "last_update" not in self._data_cache:
                return {"success": False, "error": "No cached data available"}
            
            last_update = datetime.fromisoformat(self._data_cache["last_update"])
            if datetime.now() - last_update > timedelta(seconds=self._cache_ttl):
                return {"success": False, "error": "Cache expired"}
            
            return {
                "success": True,
                "data": self._data_cache.get("cards", []),
                "cached": True,
                "last_update": self._data_cache["last_update"]
            }
            
        except Exception as e:
            logger.error(f"Cache retrieval failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def search_cards(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search cards based on filters
        
        Args:
            filters: Dictionary of search filters
            
        Returns:
            List of matching cards
        """
        try:
            # Get data (from cache or fresh ingestion)
            cache_result = self.get_cached_data()
            if not cache_result["success"]:
                # Cache miss, do fresh ingestion
                ingest_result = self.ingest_all_sources()
                if not ingest_result["success"]:
                    return []
                cards = ingest_result["data"]
            else:
                cards = cache_result["data"]
            
            # Apply filters
            filtered_cards = []
            for card in cards:
                if self._matches_filters(card, filters):
                    filtered_cards.append(card)
            
            return filtered_cards
            
        except Exception as e:
            logger.error(f"Card search failed: {str(e)}")
            return []
    
    def _matches_filters(self, card: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if card matches the given filters"""
        try:
            # Filter by issuer
            if "issuer" in filters:
                if card.get("general_info", {}).get("issuer", "").lower() != filters["issuer"].lower():
                    return False
            
            # Filter by tier
            if "tier" in filters:
                if card.get("general_info", {}).get("tier", "").lower() != filters["tier"].lower():
                    return False
            
            # Filter by card network
            if "card_network" in filters:
                if card.get("general_info", {}).get("card_network", "").lower() != filters["card_network"].lower():
                    return False
            
            # Filter by minimum income
            if "min_income" in filters:
                income_reqs = card.get("eligibility", {}).get("income_requirements", {})
                salaried_min = income_reqs.get("salaried_monthly", 0)
                if salaried_min > filters["min_income"]:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Filter matching failed: {str(e)}")
            return False
    
    def get_card_by_id(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get specific card by ID"""
        try:
            cache_result = self.get_cached_data()
            if not cache_result["success"]:
                ingest_result = self.ingest_all_sources()
                if not ingest_result["success"]:
                    return None
                cards = ingest_result["data"]
            else:
                cards = cache_result["data"]
            
            for card in cards:
                if card.get("card_id") == card_id:
                    return card
            
            return None
            
        except Exception as e:
            logger.error(f"Get card by ID failed: {str(e)}")
            return None
