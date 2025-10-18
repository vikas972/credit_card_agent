"""
ZET Partner API Integration
Handles all API calls to ZET for credit card data and recommendations
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class ZETAPIClient:
    """Client for ZET Partner API integration"""
    
    def __init__(self, api_key: str, base_url: str = "https://integration.staging.onecode.in/v2"):
        self.api_key = api_key
        self.base_url = base_url
        self.token = None
        self.refresh_token = None
        self.token_expiry = None
        
        # Try to load stored tokens from environment
        self._load_stored_tokens()
    
    def _load_stored_tokens(self):
        """Load stored tokens from environment variables"""
        import os
        self.token = os.getenv("ZET_ACCESS_TOKEN")
        self.refresh_token = os.getenv("ZET_REFRESH_TOKEN")
        self.token_expiry = os.getenv("ZET_TOKEN_EXPIRY")
    
    def generate_token(self, phone_number: str) -> Dict[str, Any]:
        """Generate access token for API calls"""
        try:
            url = f"{self.base_url}/generate-token"
            headers = {"api-key": self.api_key}
            body = {"id": phone_number}
            
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["data"]["app_token"]
                self.refresh_token = data["data"]["refresh_token"]
                self.token_expiry = data["data"]["expiry_date"]
                
                return {
                    "success": True,
                    "token": self.token,
                    "refresh_token": self.refresh_token,
                    "expiry_date": self.token_expiry
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", {}).get("message", "Token generation failed"),
                    "code": error_data.get("error", {}).get("code", "unknown")
                }
                
        except Exception as e:
            logger.error(f"Token generation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh the access token"""
        try:
            if not self.token or not self.refresh_token:
                return {"success": False, "error": "No token to refresh"}
            
            url = f"{self.base_url}/refresh-token"
            headers = {"Authorization": f"Bearer {self.token}"}
            body = {"refresh_token": self.refresh_token}
            
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["data"]["token"]
                self.refresh_token = data["data"]["refresh_token"]
                self.token_expiry = data["data"]["expiry_date"]
                
                return {"success": True, "token": self.token}
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", {}).get("message", "Token refresh failed")
                }
                
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def add_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add customer to ZET platform"""
        try:
            if not self.token:
                return {"success": False, "error": "No valid token available"}
            
            url = f"{self.base_url}/customer-addition"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.post(url, headers=headers, json=customer_data)
            
            if response.status_code == 200:
                return {"success": True, "message": "Customer added successfully"}
            elif response.status_code == 500:
                # Check if it's a "customer already exists" error
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", "")
                    if "already exist" in error_message.lower():
                        return {"success": True, "message": "Customer already exists in the system"}
                    else:
                        return {
                            "success": False,
                            "error": error_message,
                            "code": error_data.get("error", {}).get("code", "500")
                        }
                except Exception as json_error:
                    # If JSON parsing fails, check response text
                    response_text = response.text
                    if "already exist" in response_text.lower():
                        return {"success": True, "message": "Customer already exists in the system"}
                    else:
                        return {"success": False, "error": f"Internal server error: {response_text}", "code": "500"}
            else:
                try:
                    error_data = response.json()
                    return {
                        "success": False,
                        "error": error_data.get("error", {}).get("message", "Customer addition failed"),
                        "code": error_data.get("error", {}).get("code", "unknown")
                    }
                except Exception as json_error:
                    return {
                        "success": False,
                        "error": f"API error {response.status_code}: {response.text}",
                        "code": str(response.status_code)
                    }
                
        except Exception as e:
            logger.error(f"Customer addition failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_products(self, pincode: int, category: str = "CREDIT_CARDS", limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Get list of credit cards"""
        try:
            if not self.token:
                return {"success": False, "error": "No valid token available"}
            
            url = f"{self.base_url}/products"
            headers = {"Authorization": f"Bearer {self.token}"}
            params = {
                "pincode": pincode,
                "category": category,
                "limit": limit,
                "offset": offset
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data.get("data", []),
                    "pagination": data.get("pagination", {})
                }
            else:
                return {"success": False, "error": f"API call failed with status {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Get products failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific product"""
        try:
            if not self.token:
                return {"success": False, "error": "No valid token available"}
            
            url = f"{self.base_url}/products/{product_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data.get("data", {})}
            else:
                return {"success": False, "error": f"API call failed with status {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Get product details failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_recommendations(self, user_id: str, category: str = "CREDIT_CARDS", filter_type: Optional[str] = None) -> Dict[str, Any]:
        """Get personalized recommendations for a user"""
        try:
            if not self.token:
                return {"success": False, "error": "No valid token available"}
            
            url = f"{self.base_url}/recommendations/{user_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            params = {"category": category}
            
            if filter_type:
                params["filter"] = filter_type
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data.get("data", []),
                    "pagination": data.get("pagination", {})
                }
            elif response.status_code == 204:
                return {
                    "success": True,
                    "data": [],
                    "status": "Generating recommendations for the user"
                }
            else:
                return {"success": False, "error": f"API call failed with status {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Get recommendations failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_product_eligibility(self, product_id: str, user_id: str) -> Dict[str, Any]:
        """Check user eligibility for a specific product"""
        try:
            if not self.token:
                return {"success": False, "error": "No valid token available"}
            
            url = f"{self.base_url}/recommendations/{product_id}/{user_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data.get("data", {})}
            elif response.status_code == 204:
                return {
                    "success": True,
                    "data": {"status": "Generating recommendations for the user"}
                }
            else:
                return {"success": False, "error": f"API call failed with status {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Get product eligibility failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def apply_for_product(self, user_id: str, product_id: str, source: Optional[str] = None) -> Dict[str, Any]:
        """Apply for a credit card product"""
        try:
            if not self.token:
                return {"success": False, "error": "No valid token available"}
            
            url = f"{self.base_url}/apply/{user_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            body = {"id": product_id}
            
            if source:
                body["source"] = source
            
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "lead_id": data.get("data", {}).get("lead_id"),
                    "url": data.get("data", {}).get("url")
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", {}).get("message", "Application failed"),
                    "code": error_data.get("error", {}).get("code", "unknown")
                }
                
        except Exception as e:
            logger.error(f"Apply for product failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_leads(self, user_id: Optional[str] = None, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Get lead information"""
        try:
            if not self.token:
                return {"success": False, "error": "No valid token available"}
            
            url = f"{self.base_url}/customer/leads"
            headers = {"Authorization": f"Bearer {self.token}"}
            params = {"limit": limit, "offset": offset}
            
            if user_id:
                params["customer_id"] = user_id
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data.get("data", []),
                    "pagination": data.get("pagination", {})
                }
            else:
                return {"success": False, "error": f"API call failed with status {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Get leads failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_lead_details(self, lead_id: str) -> Dict[str, Any]:
        """Get details of a specific lead"""
        try:
            if not self.token:
                return {"success": False, "error": "No valid token available"}
            
            url = f"{self.base_url}/customer/leads/{lead_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data.get("data", {})}
            else:
                return {"success": False, "error": f"API call failed with status {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Get lead details failed: {str(e)}")
            return {"success": False, "error": str(e)}
