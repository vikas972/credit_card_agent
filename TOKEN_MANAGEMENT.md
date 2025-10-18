# Token Management for Credit Card Agent

## Overview
The credit card agent now uses a pre-generated token approach for better security and performance. Tokens are generated in advance and stored in the `.env` file.

## Setup Instructions

### 1. Environment Variables
Create a `.env` file with the following variables:

```env
# ZET Partner API Configuration
ZET_API_KEY=your_zet_api_key_here
ZET_PHONE_NUMBER=your_phone_number_here

# Generated tokens (will be added automatically)
ZET_ACCESS_TOKEN=your_generated_access_token
ZET_REFRESH_TOKEN=your_generated_refresh_token
ZET_TOKEN_EXPIRY=your_token_expiry_date

# Google AI API Key
GOOGLE_API_KEY=your_google_api_key_here
```

### 2. Generate Initial Token
Run the token generation script to create and store your initial token:

```bash
# Generate initial token
python generate_token.py generate

# Or just run without arguments (defaults to generate)
python generate_token.py
```

This will:
- Generate a new ZET API access token
- Store it in your `.env` file
- Display the token information

### 3. Refresh Token (When Needed)
When your token expires (every 7 days), refresh it manually:

```bash
# Refresh existing token
python generate_token.py refresh
```

This will:
- Use the stored refresh token to get a new access token
- Update the `.env` file with new tokens
- Display the new token information

## Agent Flow

### New Flow (Token Pre-generated)
1. **List Credit Cards**: Agent shows available credit cards for user's pincode
2. **Collect User Profile**: Agent asks for user details (income, age, etc.)
3. **Add Customer**: Agent adds user to ZET platform
4. **Get Recommendations**: Agent gets personalized recommendations
5. **Check Eligibility**: Agent checks eligibility for specific cards
6. **Apply for Cards**: Agent helps with applications
7. **Track Status**: Agent monitors application progress

### Key Changes
- ✅ **No token generation in agent flow** - Token is pre-generated
- ✅ **Direct credit card listing** - Agent can immediately show available cards
- ✅ **Manual token refresh** - You control when to refresh tokens
- ✅ **Better security** - Tokens stored in .env file, not in agent memory
- ✅ **Faster responses** - No token generation delay

## Usage Examples

### Generate Token
```bash
cd /path/to/13-credit-card-agent
python generate_token.py generate
```

### Refresh Token
```bash
cd /path/to/13-credit-card-agent
python generate_token.py refresh
```

### Run Agent
```bash
# After token is generated and stored
adk run credit_card_agent
```

## Troubleshooting

### Token Expired
If you get authentication errors:
1. Run `python generate_token.py refresh`
2. Restart the agent

### No Token Found
If you get "no token" errors:
1. Run `python generate_token.py generate`
2. Restart the agent

### Invalid API Key
If you get API key errors:
1. Check your `ZET_API_KEY` in `.env` file
2. Verify the key is correct with ZET support

## Benefits

1. **Security**: Tokens are stored securely in `.env` file
2. **Performance**: No token generation delay in agent responses
3. **Control**: You control when tokens are refreshed
4. **Reliability**: Pre-generated tokens are more reliable
5. **User Experience**: Faster agent responses

## File Structure

```
13-credit-card-agent/
├── generate_token.py          # Token management script
├── .env                       # Environment variables (including tokens)
├── credit_card_agent/
│   ├── agent.py              # Main agent (updated flow)
│   ├── tools.py              # Tools (refresh_token instead of generate_token)
│   └── zet_api.py            # ZET API client (loads stored tokens)
└── TOKEN_MANAGEMENT.md       # This file
```
