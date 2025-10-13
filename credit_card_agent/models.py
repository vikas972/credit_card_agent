"""
Credit Card Data Models - Core Ontology
Based on the comprehensive schema defined in the workflow design document.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class CardNetwork(str, Enum):
    VISA = "Visa"
    MASTERCARD = "Mastercard"
    RUPAY = "RuPay"
    AMEX = "Amex"


class CardTier(str, Enum):
    ENTRY_LEVEL = "Entry-Level"
    MID_TIER = "Mid-Tier"
    PREMIUM = "Premium"
    SUPER_PREMIUM = "Super-Premium"


class ResidencyType(str, Enum):
    RESIDENT_INDIAN = "Resident Indian"
    NRI = "NRI"


class EmploymentType(str, Enum):
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"


class IntentType(str, Enum):
    FIND_TRAVEL_CARD = "find_travel_card"
    FIND_CASHBACK_CARD = "find_cashback_card"
    FIND_PREMIUM_CARD = "find_premium_card"
    GENERAL_COMPARISON = "general_comparison"
    COMPARE_CARDS = "compare_cards"


class CreditScore(BaseModel):
    minimum_required: int = Field(..., description="Minimum credit score required")
    preferred: int = Field(..., description="Preferred credit score")


class IncomeRequirements(BaseModel):
    salaried_monthly: Optional[int] = Field(None, description="Minimum monthly income for salaried")
    self_employed_annual: Optional[int] = Field(None, description="Minimum annual ITR for self-employed")


class Eligibility(BaseModel):
    min_age: int = Field(..., description="Minimum age requirement")
    max_age: Optional[int] = Field(None, description="Maximum age requirement")
    residency: ResidencyType = Field(..., description="Residency requirement")
    credit_score: CreditScore = Field(..., description="Credit score requirements")
    income_requirements: IncomeRequirements = Field(..., description="Income requirements")
    serviceable_locations: List[str] = Field(default_factory=list, description="Cities where card is available")


class FeeWaiverCondition(BaseModel):
    spend_threshold: int = Field(..., description="Annual spend threshold for fee waiver")
    description: str = Field(..., description="Description of waiver condition")


class AnnualFee(BaseModel):
    amount: int = Field(..., description="Annual fee amount in INR")
    waiver_condition: Optional[FeeWaiverCondition] = Field(None, description="Conditions for fee waiver")


class LatePaymentCharge(BaseModel):
    min_amount: int = Field(..., description="Minimum amount for this charge tier")
    max_amount: int = Field(..., description="Maximum amount for this charge tier")
    charge: int = Field(..., description="Charge amount in INR")


class Fees(BaseModel):
    joining_fee: int = Field(..., description="Joining fee in INR")
    annual_fee: AnnualFee = Field(..., description="Annual fee details")
    interest_rate_apr: float = Field(..., description="Interest rate APR")
    late_payment_charges: List[LatePaymentCharge] = Field(default_factory=list)
    cash_advance_fee: str = Field(..., description="Cash advance fee structure")
    forex_markup: float = Field(..., description="Forex markup percentage")


class EarningRate(BaseModel):
    category: str = Field(..., description="Spending category")
    rate: float = Field(..., description="Reward rate (percentage)")
    cap: Optional[int] = Field(None, description="Monthly cap in INR")


class WelcomeBonus(BaseModel):
    points: int = Field(..., description="Welcome bonus points")
    value: int = Field(..., description="Value in INR")
    condition: str = Field(..., description="Condition to earn bonus")


class MilestoneBenefit(BaseModel):
    milestone: str = Field(..., description="Milestone description")
    benefit: str = Field(..., description="Benefit description")


class Redemption(BaseModel):
    cashback_value_per_point: float = Field(..., description="Cashback value per point")
    airmiles_partners: List[str] = Field(default_factory=list, description="Airline partners")
    transfer_ratio: str = Field(..., description="Transfer ratio to partners")


class Rewards(BaseModel):
    base_rate: float = Field(..., description="Base reward rate")
    earning_rates: List[EarningRate] = Field(..., description="Category-wise earning rates")
    welcome_bonus: Optional[WelcomeBonus] = Field(None, description="Welcome bonus details")
    milestone_benefits: List[MilestoneBenefit] = Field(default_factory=list, description="Milestone benefits")
    redemption: Redemption = Field(..., description="Redemption options")


class LoungeAccess(BaseModel):
    domestic_visits_per_quarter: int = Field(..., description="Domestic lounge visits per quarter")
    international_visits_per_year: int = Field(..., description="International lounge visits per year")
    guest_policy: str = Field(..., description="Guest access policy")


class TravelBenefits(BaseModel):
    lounge_access: Optional[LoungeAccess] = Field(None, description="Lounge access details")
    travel_insurance: Optional[str] = Field(None, description="Travel insurance coverage")


class LifestyleBenefits(BaseModel):
    dining_discounts: Optional[str] = Field(None, description="Dining discount offers")
    movie_offers: Optional[str] = Field(None, description="Movie ticket offers")
    golf_access: Optional[str] = Field(None, description="Golf course access")
    concierge_service: bool = Field(False, description="Concierge service availability")


class InsuranceBenefits(BaseModel):
    fraud_liability_cover: Optional[str] = Field(None, description="Fraud liability coverage")
    personal_accident_cover: Optional[str] = Field(None, description="Personal accident coverage")


class Benefits(BaseModel):
    travel: Optional[TravelBenefits] = Field(None, description="Travel-related benefits")
    lifestyle: Optional[LifestyleBenefits] = Field(None, description="Lifestyle benefits")
    insurance: Optional[InsuranceBenefits] = Field(None, description="Insurance benefits")


class GeneralInfo(BaseModel):
    card_name: str = Field(..., description="Credit card name")
    issuer: str = Field(..., description="Issuing bank")
    card_network: CardNetwork = Field(..., description="Payment network")
    tier: CardTier = Field(..., description="Card tier")
    image_url: Optional[str] = Field(None, description="Card image URL")


class ApplicationDetails(BaseModel):
    deep_link_url: str = Field(..., description="Direct application link")


class CreditCard(BaseModel):
    card_id: str = Field(..., description="Unique card identifier")
    general_info: GeneralInfo = Field(..., description="General card information")
    application_details: ApplicationDetails = Field(..., description="Application details")
    eligibility: Eligibility = Field(..., description="Eligibility criteria")
    fees: Fees = Field(..., description="Fee structure")
    rewards: Rewards = Field(..., description="Rewards program")
    benefits: Benefits = Field(..., description="Card benefits")


class UserProfile(BaseModel):
    age: int = Field(..., description="User age")
    employment: EmploymentType = Field(..., description="Employment type")
    net_monthly_income: Optional[int] = Field(None, description="Net monthly income for salaried")
    annual_income: Optional[int] = Field(None, description="Annual income for self-employed")
    credit_score: int = Field(..., description="Credit score")
    city: str = Field(..., description="City of residence")
    monthly_spending: Dict[str, int] = Field(..., description="Monthly spending by category")


class MonthlySpending(BaseModel):
    groceries: int = Field(default=0, description="Monthly grocery spending")
    dining: int = Field(default=0, description="Monthly dining spending")
    travel_flights_hotels: int = Field(default=0, description="Monthly travel spending")
    fuel: int = Field(default=0, description="Monthly fuel spending")
    online_shopping_ecommerce: int = Field(default=0, description="Monthly online shopping")
    utility_bills: int = Field(default=0, description="Monthly utility bills")
    other_retail: int = Field(default=0, description="Other retail spending")


class UserQuery(BaseModel):
    query_text: str = Field(..., description="User's natural language query")
    intent: Optional[IntentType] = Field(None, description="Classified intent")
    user_profile: Optional[UserProfile] = Field(None, description="User profile data")


class CardRecommendation(BaseModel):
    card: CreditCard = Field(..., description="Recommended credit card")
    score: float = Field(..., description="Recommendation score")
    rationale: str = Field(..., description="Why this card is recommended")


class ComparisonResult(BaseModel):
    card_a: CreditCard = Field(..., description="First card for comparison")
    card_b: CreditCard = Field(..., description="Second card for comparison")
    net_annual_cost_a: int = Field(..., description="Net annual cost for card A")
    net_annual_cost_b: int = Field(..., description="Net annual cost for card B")
    annual_rewards_value_a: float = Field(..., description="Annual rewards value for card A")
    annual_rewards_value_b: float = Field(..., description="Annual rewards value for card B")
    net_annual_value_a: float = Field(..., description="Net annual value for card A")
    net_annual_value_b: float = Field(..., description="Net annual value for card B")
    primary_benefit_a: str = Field(..., description="Primary benefit for card A")
    primary_benefit_b: str = Field(..., description="Primary benefit for card B")
    key_drawback_a: str = Field(..., description="Key drawback for card A")
    key_drawback_b: str = Field(..., description="Key drawback for card B")
    recommendation: str = Field(..., description="Final recommendation")
    justification: str = Field(..., description="Justification for recommendation")


class AgentResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")
    trace_id: str = Field(..., description="Unique trace ID for tracking")
