"""
IntentAgent - Classifies user queries into predefined intents
First point of contact for understanding user goals
"""

import logging
import re
from typing import Dict, Any, Optional
from google.adk.agents import Agent
from google.adk.models import LlmRequest

from ...models import IntentType, UserQuery

logger = logging.getLogger(__name__)


class IntentAgent(Agent):
    """
    Intent classification agent that determines user's primary goal
    from their natural language query.
    """
    
    def __init__(self, **kwargs):
        name = kwargs.pop('name', 'intent')
        # Set a default model for ADK compatibility
        if 'model' not in kwargs:
            kwargs['model'] = 'gemini-pro'
        super().__init__(name=name, **kwargs)
        self._intent_keywords = {
            IntentType.FIND_TRAVEL_CARD: [
                "travel", "airline", "flight", "hotel", "lounge", "miles", 
                "airport", "vacation", "trip", "journey", "wanderlust"
            ],
            IntentType.FIND_CASHBACK_CARD: [
                "cashback", "cash back", "money back", "rewards", "points",
                "discount", "savings", "earn", "earning", "return"
            ],
            IntentType.FIND_PREMIUM_CARD: [
                "premium", "luxury", "exclusive", "elite", "high-end",
                "concierge", "priority", "vip", "platinum", "gold"
            ],
            IntentType.COMPARE_CARDS: [
                "compare", "comparison", "vs", "versus", "difference",
                "better", "which", "choose", "between"
            ],
            IntentType.GENERAL_COMPARISON: [
                "recommend", "suggest", "best", "good", "suitable",
                "help", "advice", "guide", "options"
            ]
        }
    
    def classify_intent(self, query_text: str) -> IntentType:
        """
        Classify user query into predefined intent categories
        
        Args:
            query_text: User's natural language query
            
        Returns:
            Classified intent type
        """
        try:
            query_lower = query_text.lower()
            
            # Rule-based classification with keyword matching
            intent_scores = {}
            
            for intent, keywords in self._intent_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in query_lower:
                        score += 1
                        # Give higher weight to exact phrase matches
                        if f" {keyword} " in f" {query_lower} ":
                            score += 0.5
                intent_scores[intent] = score
            
            # Find intent with highest score
            if intent_scores:
                best_intent = max(intent_scores, key=intent_scores.get)
                if intent_scores[best_intent] > 0:
                    logger.info(f"Classified intent: {best_intent} (score: {intent_scores[best_intent]})")
                    return best_intent
            
            # Fallback to general comparison if no specific intent detected
            logger.info("No specific intent detected, defaulting to general comparison")
            return IntentType.GENERAL_COMPARISON
            
        except Exception as e:
            logger.error(f"Intent classification failed: {str(e)}")
            return IntentType.GENERAL_COMPARISON
    
    def classify_with_llm(self, query_text: str) -> IntentType:
        """
        Classify intent using LLM for more nuanced understanding
        
        Args:
            query_text: User's natural language query
            
        Returns:
            Classified intent type
        """
        try:
            prompt = f"""
            Classify the following user query into one of these intent categories:
            
            1. find_travel_card - User wants a credit card for travel benefits
            2. find_cashback_card - User wants a credit card for cashback/rewards
            3. find_premium_card - User wants a premium/luxury credit card
            4. compare_cards - User wants to compare specific cards
            5. general_comparison - User wants general recommendations
            
            User Query: "{query_text}"
            
            Respond with only the intent category name (e.g., "find_travel_card").
            """
            
            request = LlmRequest(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50
            )
            
            response = self.llm_client.generate(request)
            intent_text = response.choices[0].message.content.strip().lower()
            
            # Map response to IntentType enum
            intent_mapping = {
                "find_travel_card": IntentType.FIND_TRAVEL_CARD,
                "find_cashback_card": IntentType.FIND_CASHBACK_CARD,
                "find_premium_card": IntentType.FIND_PREMIUM_CARD,
                "compare_cards": IntentType.COMPARE_CARDS,
                "general_comparison": IntentType.GENERAL_COMPARISON
            }
            
            return intent_mapping.get(intent_text, IntentType.GENERAL_COMPARISON)
            
        except Exception as e:
            logger.error(f"LLM intent classification failed: {str(e)}")
            # Fallback to rule-based classification
            return self.classify_intent(query_text)
    
    def process_query(self, query: UserQuery) -> UserQuery:
        """
        Process user query and add classified intent
        
        Args:
            query: User query object
            
        Returns:
            Updated query with classified intent
        """
        try:
            if not query.intent:
                # Use LLM classification for better accuracy
                query.intent = self.classify_with_llm(query.query_text)
            
            logger.info(f"Processed query with intent: {query.intent}")
            return query
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            # Ensure query has an intent even if processing fails
            query.intent = IntentType.GENERAL_COMPARISON
            return query
    
    def extract_entities(self, query_text: str) -> Dict[str, Any]:
        """
        Extract relevant entities from user query
        
        Args:
            query_text: User's natural language query
            
        Returns:
            Dictionary of extracted entities
        """
        try:
            entities = {
                "spending_categories": [],
                "card_types": [],
                "specific_cards": [],
                "amounts": [],
                "timeframes": []
            }
            
            query_lower = query_text.lower()
            
            # Extract spending categories
            spending_keywords = {
                "groceries": ["grocery", "food", "supermarket", "vegetables"],
                "dining": ["dining", "restaurant", "food", "eat", "meal"],
                "travel": ["travel", "flight", "hotel", "trip", "vacation"],
                "fuel": ["fuel", "petrol", "diesel", "gas", "gasoline"],
                "online_shopping": ["online", "shopping", "ecommerce", "amazon", "flipkart"],
                "utility_bills": ["utility", "bills", "electricity", "water", "internet"]
            }
            
            for category, keywords in spending_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    entities["spending_categories"].append(category)
            
            # Extract card types
            card_type_keywords = {
                "travel": ["travel", "airline", "miles"],
                "cashback": ["cashback", "rewards", "points"],
                "premium": ["premium", "luxury", "platinum", "gold"],
                "secured": ["secured", "fd", "deposit"]
            }
            
            for card_type, keywords in card_type_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    entities["card_types"].append(card_type)
            
            # Extract amounts (basic regex)
            amount_pattern = r'₹?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:lakh|lac|k|thousand|million)?'
            amounts = re.findall(amount_pattern, query_text)
            entities["amounts"] = amounts
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
            return {
                "spending_categories": [],
                "card_types": [],
                "specific_cards": [],
                "amounts": [],
                "timeframes": []
            }
    
    def validate_query(self, query_text: str) -> Dict[str, Any]:
        """
        Validate user query for completeness and clarity
        
        Args:
            query_text: User's natural language query
            
        Returns:
            Validation result with suggestions
        """
        try:
            validation_result = {
                "is_valid": True,
                "suggestions": [],
                "missing_info": []
            }
            
            query_lower = query_text.lower()
            
            # Check for minimum length
            if len(query_text.strip()) < 10:
                validation_result["is_valid"] = False
                validation_result["suggestions"].append("Please provide more details about what you're looking for")
            
            # Check for credit card related terms
            card_terms = ["card", "credit", "bank", "rewards", "cashback", "travel", "premium"]
            if not any(term in query_lower for term in card_terms):
                validation_result["suggestions"].append("Please mention what type of credit card you're interested in")
            
            # Check for specific requirements
            if "income" not in query_lower and "salary" not in query_lower:
                validation_result["missing_info"].append("Income information would help provide better recommendations")
            
            if "spend" not in query_lower and "expense" not in query_lower:
                validation_result["missing_info"].append("Spending patterns would help match the right card")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Query validation failed: {str(e)}")
            return {
                "is_valid": False,
                "suggestions": ["Please try rephrasing your query"],
                "missing_info": []
            }
