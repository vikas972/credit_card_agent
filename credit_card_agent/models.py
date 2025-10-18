"""
Credit Card Agent Data Models
Simplified models for ZET API integration
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

class EmploymentType(str, Enum):
    SALARIED = "SALARIED"
    SELF_EMPLOYED = "SELF_EMPLOYED"

class GenderType(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHERS = "OTHERS"

class IncomeMode(str, Enum):
    BANK = "BANK"
    CASH = "CASH"

class UserProfile(BaseModel):
    """User profile for credit card recommendations"""
    name: str = Field(..., description="User's full name")
    phone_number: str = Field(..., description="User's phone number (10 digits)")
    email: str = Field(..., description="User's email address")
    gender: GenderType = Field(..., description="User's gender")
    dob: str = Field(..., description="Date of birth in YYYY-MM-DD format")
    monthly_income: int = Field(..., description="Monthly income in INR")
    employment_type: EmploymentType = Field(..., description="Employment type")
    mode_of_income: IncomeMode = Field(..., description="Mode of income")
    pincode: int = Field(..., description="Pincode for location-based recommendations")
    pan_no: str = Field(..., description="PAN number")
    consent_message: str = Field(..., description="Consent message user agreed to")
    consented_at: str = Field(..., description="Consent timestamp")

class CreditCard(BaseModel):
    """Credit card information from ZET API"""
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Credit card name")
    image_url: Optional[str] = Field(None, description="Card image URL")
    category: str = Field(..., description="Product category")
    partnerId: Optional[str] = Field(None, description="Partner ID")
    brandName: Optional[str] = Field(None, description="Brand name")
    fees: Optional[Dict[str, Any]] = Field(None, description="Fee structure")
    best_suited_for: Optional[List[str]] = Field(None, description="Best suited for categories")
    highlights: Optional[List[Dict[str, Any]]] = Field(None, description="Card highlights")
    benefits: Optional[List[Dict[str, Any]]] = Field(None, description="Card benefits")
    terms_and_conditions: Optional[List[str]] = Field(None, description="Terms and conditions")
    eligibility_criteria: Optional[Dict[str, Any]] = Field(None, description="Eligibility criteria")
    is_eligible: Optional[bool] = Field(None, description="Whether user is eligible")
    reason: Optional[str] = Field(None, description="Reason for ineligibility")

class Recommendation(BaseModel):
    """Credit card recommendation"""
    card: CreditCard = Field(..., description="Recommended credit card")
    score: Optional[float] = Field(None, description="Recommendation score")
    rationale: Optional[str] = Field(None, description="Why this card is recommended")

class Application(BaseModel):
    """Credit card application"""
    user_id: str = Field(..., description="User ID")
    product_id: str = Field(..., description="Product ID to apply for")
    source: Optional[str] = Field(None, description="Application source")
    lead_id: Optional[str] = Field(None, description="Generated lead ID")
    application_url: Optional[str] = Field(None, description="Application URL")

class Lead(BaseModel):
    """Lead information"""
    lead_id: str = Field(..., description="Lead ID")
    lead_status: str = Field(..., description="Current lead status")
    asks: Optional[List[str]] = Field(None, description="Required actions")
    customer_name: Optional[str] = Field(None, description="Customer name")
    partner_id: Optional[str] = Field(None, description="Partner ID")
    partner_name: Optional[str] = Field(None, description="Partner name")
    category: Optional[str] = Field(None, description="Product category")
    source: Optional[str] = Field(None, description="Lead source")

class AgentResponse(BaseModel):
    """Standard agent response"""
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")
    message: Optional[str] = Field(None, description="Success or info message")