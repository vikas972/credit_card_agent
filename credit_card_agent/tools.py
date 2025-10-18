"""
Credit Card Agent Tools
Simple tools for credit card operations using ZET API
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .zet_api import ZETAPIClient

logger = logging.getLogger(__name__)

# Initialize ZET API client
ZET_API_KEY = os.getenv("ZET_API_KEY", "")
ZET_PHONE_NUMBER = os.getenv("ZET_PHONE_NUMBER", "")
ZET_CLIENT = ZETAPIClient(ZET_API_KEY) if ZET_API_KEY else None

def get_consent_timestamp() -> str:
    """
    Generate consent timestamp in the required format: YYYY-MM-DD HH:MM:SS.SSS
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def refresh_token() -> Dict[str, Any]:
    """
    Refresh ZET API access token (manual function)
    """
    try:
        if not ZET_CLIENT:
            return {"success": False, "error": "ZET API not configured"}
        
        result = ZET_CLIENT.refresh_access_token()
        return result
        
    except Exception as e:
        logger.error(f"Refresh token failed: {str(e)}")
        return {"success": False, "error": str(e)}

def get_credit_cards(pincode: int, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """
    Get list of available credit cards from ZET API
    """
    try:
        if not ZET_CLIENT:
            return {"success": False, "error": "ZET API not configured"}
        
        result = ZET_CLIENT.get_products(pincode=pincode, category="CREDIT_CARDS", limit=limit, offset=offset)
        return result
        
    except Exception as e:
        logger.error(f"Get credit cards failed: {str(e)}")
        return {"success": False, "error": str(e)}

def get_credit_card_details(product_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific credit card
    """
    try:
        if not ZET_CLIENT:
            return {"success": False, "error": "ZET API not configured"}
        
        result = ZET_CLIENT.get_product_details(product_id)
        return result
        
    except Exception as e:
        logger.error(f"Get credit card details failed: {str(e)}")
        return {"success": False, "error": str(e)}

def get_recommendations(user_id: str, filter_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get personalized credit card recommendations for a user
    """
    try:
        if not ZET_CLIENT:
            return {"success": False, "error": "ZET API not configured"}
        
        result = ZET_CLIENT.get_recommendations(user_id, filter_type=filter_type)
        return result
        
    except Exception as e:
        logger.error(f"Get recommendations failed: {str(e)}")
        return {"success": False, "error": str(e)}

def check_eligibility(product_id: str, user_id: str) -> Dict[str, Any]:
    """
    Check if user is eligible for a specific credit card
    """
    try:
        if not ZET_CLIENT:
            return {"success": False, "error": "ZET API not configured"}
        
        result = ZET_CLIENT.get_product_eligibility(product_id, user_id)
        return result
        
    except Exception as e:
        logger.error(f"Check eligibility failed: {str(e)}")
        return {"success": False, "error": str(e)}

def apply_for_card(user_id: str, product_id: str, source: Optional[str] = None) -> Dict[str, Any]:
    """
    Apply for a credit card and generate a lead
    """
    try:
        if not ZET_CLIENT:
            return {"success": False, "error": "ZET API not configured"}
        
        result = ZET_CLIENT.apply_for_product(user_id, product_id, source)
        return result
        
    except Exception as e:
        logger.error(f"Apply for card failed: {str(e)}")
        return {"success": False, "error": str(e)}

def get_lead_status(user_id: Optional[str] = None, lead_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get status of credit card applications and leads
    """
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

def add_customer(
    name: str,
    phone_number: str,
    email: str,
    gender: str,
    dob: str,
    monthly_income: int,
    employment_type: str,
    mode_of_income: str,
    pincode: int,
    pan_no: str,
    consent_message: str = "I agree to the terms and conditions for credit card recommendations",
    consented_at: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add customer to ZET platform for recommendations
    
    Args:
        name: Customer's full name
        phone_number: Customer's phone number (10 digits, will be formatted to +91-XXXXXXXXXX)
        email: Customer's email address
        gender: MALE | FEMALE | OTHERS
        dob: Date of birth in YYYY-MM-DD format
        monthly_income: Monthly income as integer
        employment_type: SALARIED | SELF_EMPLOYED
        mode_of_income: BANK | CASH
        pincode: Pincode as integer
        pan_no: PAN number
        consent_message: Consent message user agreed to
        consented_at: Consent timestamp in YYYY-MM-DD HH:MM:SS.SSS format
    """
    try:
        if not ZET_CLIENT:
            return {"success": False, "error": "ZET API not configured"}
        
        # Format phone number to +91-XXXXXXXXXX format
        if phone_number.startswith('+91'):
            formatted_phone = phone_number
        elif phone_number.startswith('91'):
            formatted_phone = f"+{phone_number}"
        else:
            formatted_phone = f"+91-{phone_number}"
        
        # Generate consent timestamp if not provided
        if consented_at is None:
            consented_at = get_consent_timestamp()
        
        # Prepare customer data according to API specification
        customer_data = {
            "id": formatted_phone,  # Phone number in +91-9876543211 format
            "name": name,
            "phone_number": phone_number,  # Original phone number (10 digits)
            "email": email,
            "gender": gender.upper(),
            "dob": dob,
            "monthly_income": monthly_income,
            "employment_type": employment_type.upper(),
            "mode_of_income": mode_of_income.upper(),
            "pincode": pincode,
            "pan_no": pan_no,
            "consent": {
                "message": consent_message,
                "consented_at": consented_at
            }
        }
        
        result = ZET_CLIENT.add_customer(customer_data)
        return result
        
    except Exception as e:
        logger.error(f"Add customer failed: {str(e)}")
        return {"success": False, "error": str(e)}