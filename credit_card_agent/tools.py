"""
Credit Card Agent Tools
Simple tools for credit card operations using ZET API
"""

import os
import logging
from typing import Dict, Any, Optional
from google.adk.tools import BaseTool
from .zet_api import ZETAPIClient

logger = logging.getLogger(__name__)

# Initialize ZET API client
ZET_API_KEY = os.getenv("ZET_API_KEY", "")
ZET_CLIENT = ZETAPIClient(ZET_API_KEY) if ZET_API_KEY else None

class GetCreditCardsTool(BaseTool):
    """Tool to get available credit cards from ZET API"""
    
    def __init__(self):
        super().__init__(
            name="get_credit_cards",
            description="Get list of available credit cards from ZET API"
        )
    
    def execute(self, pincode: int, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Get credit cards for a specific pincode"""
        try:
            if not ZET_CLIENT:
                return {"success": False, "error": "ZET API not configured"}
            
            result = ZET_CLIENT.get_products(pincode=pincode, category="CREDIT_CARDS", limit=limit, offset=offset)
            return result
            
        except Exception as e:
            logger.error(f"Get credit cards failed: {str(e)}")
            return {"success": False, "error": str(e)}

class GetCreditCardDetailsTool(BaseTool):
    """Tool to get detailed information about a specific credit card"""
    
    def __init__(self):
        super().__init__(
            name="get_credit_card_details",
            description="Get detailed information about a specific credit card"
        )
    
    def execute(self, product_id: str) -> Dict[str, Any]:
        """Get detailed information about a credit card"""
        try:
            if not ZET_CLIENT:
                return {"success": False, "error": "ZET API not configured"}
            
            result = ZET_CLIENT.get_product_details(product_id)
            return result
            
        except Exception as e:
            logger.error(f"Get credit card details failed: {str(e)}")
            return {"success": False, "error": str(e)}

class GetRecommendationsTool(BaseTool):
    """Tool to get personalized credit card recommendations"""
    
    def __init__(self):
        super().__init__(
            name="get_recommendations",
            description="Get personalized credit card recommendations for a user"
        )
    
    def execute(self, user_id: str, filter_type: Optional[str] = None) -> Dict[str, Any]:
        """Get personalized recommendations"""
        try:
            if not ZET_CLIENT:
                return {"success": False, "error": "ZET API not configured"}
            
            result = ZET_CLIENT.get_recommendations(user_id, filter_type=filter_type)
            return result
            
        except Exception as e:
            logger.error(f"Get recommendations failed: {str(e)}")
            return {"success": False, "error": str(e)}

class CheckEligibilityTool(BaseTool):
    """Tool to check user eligibility for a specific credit card"""
    
    def __init__(self):
        super().__init__(
            name="check_eligibility",
            description="Check if user is eligible for a specific credit card"
        )
    
    def execute(self, product_id: str, user_id: str) -> Dict[str, Any]:
        """Check eligibility for a specific product"""
        try:
            if not ZET_CLIENT:
                return {"success": False, "error": "ZET API not configured"}
            
            result = ZET_CLIENT.get_product_eligibility(product_id, user_id)
            return result
            
        except Exception as e:
            logger.error(f"Check eligibility failed: {str(e)}")
            return {"success": False, "error": str(e)}

class ApplyForCardTool(BaseTool):
    """Tool to apply for a credit card"""
    
    def __init__(self):
        super().__init__(
            name="apply_for_card",
            description="Apply for a credit card and generate a lead"
        )
    
    def execute(self, user_id: str, product_id: str, source: Optional[str] = None) -> Dict[str, Any]:
        """Apply for a credit card"""
        try:
            if not ZET_CLIENT:
                return {"success": False, "error": "ZET API not configured"}
            
            result = ZET_CLIENT.apply_for_product(user_id, product_id, source)
            return result
            
        except Exception as e:
            logger.error(f"Apply for card failed: {str(e)}")
            return {"success": False, "error": str(e)}

class GetLeadStatusTool(BaseTool):
    """Tool to get lead status and application updates"""
    
    def __init__(self):
        super().__init__(
            name="get_lead_status",
            description="Get status of credit card applications and leads"
        )
    
    def execute(self, user_id: Optional[str] = None, lead_id: Optional[str] = None) -> Dict[str, Any]:
        """Get lead status"""
        try:
            if not ZET_CLIENT:
                return {"success": False, "error": "ZET API not configured"}
            
            if lead_id:
                result = ZET_CLIENT.get_lead_details(lead_id)
            else:
                result = ZET_CLIENT.get_leads(user_id=user_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Get lead status failed: {str(e)}")
            return {"success": False, "error": str(e)}

class AddCustomerTool(BaseTool):
    """Tool to add customer to ZET platform"""
    
    def __init__(self):
        super().__init__(
            name="add_customer",
            description="Add customer to ZET platform for recommendations"
        )
    
    def execute(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add customer to ZET platform"""
        try:
            if not ZET_CLIENT:
                return {"success": False, "error": "ZET API not configured"}
            
            result = ZET_CLIENT.add_customer(customer_data)
            return result
            
        except Exception as e:
            logger.error(f"Add customer failed: {str(e)}")
            return {"success": False, "error": str(e)}

# Initialize tools
get_credit_cards = GetCreditCardsTool()
get_credit_card_details = GetCreditCardDetailsTool()
get_recommendations = GetRecommendationsTool()
check_eligibility = CheckEligibilityTool()
apply_for_card = ApplyForCardTool()
get_lead_status = GetLeadStatusTool()
add_customer = AddCustomerTool()