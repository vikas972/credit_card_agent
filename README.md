# Credit Card Agent - ZET API Integration

A simplified credit card recommendation system that integrates with the ZET Partner API to provide personalized credit card advice, recommendations, and application support.

## Features

- **Credit Card Advice**: General guidance and information about credit cards
- **Personalized Recommendations**: Get tailored credit card suggestions based on user profile
- **Eligibility Checking**: Check if users qualify for specific credit cards
- **Application Support**: Help users apply for credit cards through ZET platform
- **Lead Management**: Track application status and provide updates

## Customer Journey

1. **Initial Consultation**: User asks for advice or recommendations
2. **Profile Creation**: Collect user information (income, age, spending patterns, etc.)
3. **Recommendation Generation**: Get personalized recommendations from ZET API
4. **Eligibility Verification**: Check eligibility for recommended cards
5. **Application Process**: Guide users through the application process
6. **Status Tracking**: Monitor application progress and provide updates

## Architecture

The system uses a simplified multi-agent architecture with three main agents:

### Main Agent (`credit_card_agent`)
- Orchestrates the entire credit card journey
- Routes requests to appropriate sub-agents
- Provides comprehensive credit card assistance

### Sub-Agents

#### 1. Advisor Agent (`advisor_agent`)
- Provides general credit card advice and guidance
- Explains different types of credit cards and their benefits
- Answers questions about credit card usage and best practices

#### 2. Recommendation Agent (`recommendation_agent`)
- Collects user profile information
- Gets personalized recommendations from ZET API
- Explains why specific cards are recommended
- Checks eligibility for different cards

#### 3. Application Agent (`application_agent`)
- Helps users apply for credit cards
- Tracks application status and provides updates
- Manages leads and follow-ups
- Explains application requirements and process

## ZET API Integration

The system integrates with the ZET Partner API to provide real-time credit card data and recommendations:

- **Product Information**: Get available credit cards and detailed information
- **Personalized Recommendations**: Get tailored suggestions based on user profile
- **Eligibility Checking**: Check user eligibility for specific products
- **Application Processing**: Submit applications and track leads
- **Lead Management**: Monitor application status and updates

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   Create a `.env` file with the following variables:
   ```
   ZET_API_KEY=your_zet_api_key_here
   ZET_PHONE_NUMBER=your_phone_number_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

3. **Run the System**:
   ```bash
   python main.py
   ```

4. **Interactive Mode**:
   ```bash
   python main.py --interactive
   ```

## Usage Examples

### General Advice
```
"I need advice on choosing a credit card"
"What are the benefits of travel credit cards?"
"How do I improve my credit score?"
```

### Personalized Recommendations
```
"Find me credit cards suitable for my profile"
"I'm looking for cashback cards for online shopping"
"Show me premium credit cards for travel"
```

### Eligibility Checking
```
"Am I eligible for HDFC credit cards?"
"Check my eligibility for the SBI SimplyClick card"
"What cards can I get with my income level?"
```

### Application Support
```
"Help me apply for a credit card"
"I want to apply for the HDFC MoneyBack+ card"
"What documents do I need for the application?"
```

### Status Tracking
```
"What's the status of my credit card application?"
"Check my lead status"
"Any updates on my application?"
```

## API Endpoints Used

The system uses the following ZET Partner API endpoints:

- `POST /generate-token` - Generate access token
- `POST /refresh-token` - Refresh access token
- `POST /customer-addition` - Add customer to platform
- `GET /products` - Get available credit cards
- `GET /products/{id}` - Get specific card details
- `GET /recommendations/{user_id}` - Get personalized recommendations
- `GET /recommendations/{product_id}/{user_id}` - Check product eligibility
- `POST /apply/{user_id}` - Apply for credit card
- `GET /customer/leads` - Get lead information
- `GET /customer/leads/{lead_id}` - Get specific lead details

## File Structure

```
credit_card_agent/
├── agent.py                 # Main credit card agent
├── models.py               # Data models
├── tools.py                # ZET API tools
├── zet_api.py              # ZET API client
└── subagents/
    ├── advisor_agent.py    # Advice and guidance
    ├── recommendation_agent.py  # Personalized recommendations
    └── application_agent.py     # Applications and leads
```

## Key Features

- **Real-time Data**: Uses ZET API for up-to-date credit card information
- **Personalized Recommendations**: Tailored suggestions based on user profile
- **Complete Journey**: From advice to application to status tracking
- **Simple Architecture**: Easy to understand and maintain
- **No Dummy Data**: All data comes from real API calls

## Requirements

- Python 3.8+
- ZET Partner API access
- Google AI API key (for Gemini models)

## License

This project is part of the Agent Development Kit crash course.