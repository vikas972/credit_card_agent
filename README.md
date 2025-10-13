# 13. Credit Card Agent - Multi-Agent System

A sophisticated multi-agent system for intelligent credit card recommendations and comparisons, built using Google's Agent Development Kit (ADK).

## 🏗️ Architecture Overview

This system implements a Multi-Agent System (MAS) paradigm with specialized agents working together to provide personalized credit card recommendations:

### Core Agents

1. **OrchestratorAgent** - Central coordinator managing workflow and inter-agent communication
2. **IntentAgent** - Classifies user queries into predefined intents (travel, cashback, premium, etc.)
3. **DataIngestionAgent** - Manages credit card data from multiple sources
4. **EligibilityCheckAgent** - Applies deterministic rules to filter eligible cards
5. **RecommendationAgent** - Ranks and selects best-fit cards based on user profile
6. **ComparisonAnalysisAgent** - Performs detailed LLM-powered card comparisons
7. **ExplainerAgent** - Generates human-readable rationale for recommendations
8. **ResponseGenerationAgent** - Synthesizes analysis into user-friendly reports with compliance guardrails

## 🚀 Features

### Intelligent Recommendations
- **Personalized Analysis**: Considers user's spending patterns, income, credit score, and preferences
- **Multi-Factor Scoring**: Combines rewards value, fee efficiency, intent alignment, and profile fit
- **Real-time Eligibility**: Applies comprehensive eligibility rules based on issuer criteria

### Advanced Comparison
- **Quantitative Analysis**: Calculates annual rewards value, net costs, and ROI
- **Qualitative Assessment**: Evaluates benefits relevance using LLM analysis
- **Side-by-side Comparison**: Detailed feature-by-feature comparison tables

### Compliance & Safety
- **Multi-layer Guardrails**: Input filtering, prompt constraints, and output moderation
- **Topic Restrictions**: Strictly limited to credit cards, no other financial products
- **Zero-shot Refusal**: Safe fallback for prohibited content

### Data Management
- **Multi-source Ingestion**: ZetApp API, bank APIs, and internal databases
- **Unified Ontology**: Standardized credit card data schema
- **Real-time Updates**: Cached data with TTL-based refresh

## 📊 Data Model

The system uses a comprehensive credit card ontology with the following key sections:

- **General Information**: Card name, issuer, network, tier
- **Eligibility Rules**: Age, income, credit score, location requirements
- **Fee Structure**: Joining fee, annual fee, waiver conditions, interest rates
- **Rewards Program**: Earning rates, welcome bonuses, redemption options
- **Benefits**: Travel, lifestyle, and insurance benefits
- **Application Details**: Deep links to issuer application pages

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Google ADK framework
- Required dependencies (see requirements.txt)

### Setup
```bash
# Navigate to the credit card agent directory
cd 13-credit-card-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables
```env
GOOGLE_API_KEY=your_google_api_key_here
ZETAPP_API_KEY=your_zetapp_api_key_here
CREDIT_BUREAU_API_KEY=your_credit_bureau_api_key_here
```

## 🎯 Usage

### Basic Usage
```python
from credit_card_agent.agent import CreditCardAgent
from credit_card_agent.models import UserProfile, IntentType

# Initialize agent
agent = CreditCardAgent()

# Process natural language query
response = agent.process_query("Find travel credit cards with lounge access")

# Get recommendations with user profile
user_profile = UserProfile(
    age=32,
    employment="salaried",
    net_monthly_income=80000,
    credit_score=780,
    city="Mumbai",
    monthly_spending={
        "groceries": 15000,
        "dining": 8000,
        "travel_flights_hotels": 5000,
        "online_shopping_ecommerce": 20000
    }
)

recommendations = agent.get_recommendations(user_profile, IntentType.FIND_TRAVEL_CARD)
```

### Command Line Interface
```bash
# Run demo
python main.py

# Interactive mode
python main.py --interactive
```

### API Endpoints (if deployed)
```bash
# Get recommendations
POST /api/recommendations
{
    "query": "Find cashback credit cards",
    "user_profile": { ... }
}

# Compare cards
POST /api/compare
{
    "card_a_id": "hdfc_moneyback_plus",
    "card_b_id": "sbi_simplyclick",
    "user_profile": { ... }
}

# Search cards
GET /api/search?issuer=HDFC&tier=Premium
```

## 🔄 Workflow

### 1. Query Processing
```
User Query → IntentAgent → OrchestratorAgent
```

### 2. Data Gathering
```
OrchestratorAgent → DataIngestionAgent → Card Database
```

### 3. Eligibility Filtering
```
OrchestratorAgent → EligibilityCheckAgent → Filtered Cards
```

### 4. Recommendation Generation
```
OrchestratorAgent → RecommendationAgent → Ranked Cards
```

### 5. Analysis & Explanation
```
RecommendationAgent → ExplainerAgent → Rationale
```

### 6. Response Generation
```
All Agents → ResponseGenerationAgent → Final Response
```

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/unit/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### Agent Health Check
```python
agent = CreditCardAgent()
health_status = agent.health_check()
print(health_status)
```

## 📈 Monitoring & Observability

### Metrics
- Agent performance and latency
- Recommendation accuracy
- Compliance violation rates
- Data freshness and quality

### Logging
- Structured JSON logs with trace IDs
- Agent interaction tracing
- Error tracking and alerting

### Health Checks
- Data source connectivity
- Agent availability
- LLM API status
- Cache performance

## 🔧 Configuration

### Agent Configuration
```python
agent_config = {
    "llm_model": "gemini-pro",
    "temperature": 0.3,
    "max_tokens": 2000,
    "cache_ttl": 3600,
    "max_recommendations": 5
}
```

### Eligibility Rules
```json
{
    "credit_score_thresholds": {
        "excellent": 780,
        "good": 750,
        "fair": 700
    },
    "income_multipliers": {
        "high": 2.0,
        "good": 1.5,
        "minimum": 1.0
    }
}
```

## 🚨 Error Handling

### Graceful Degradation
- Fallback to cached data when external APIs fail
- Template-based responses when LLM is unavailable
- Partial results when some agents fail

### Retry Mechanisms
- Exponential backoff for API calls
- Circuit breaker pattern for external services
- Automatic retry for transient failures

### Error Recovery
- Automatic fallback to alternative data sources
- Graceful handling of malformed responses
- User-friendly error messages

## 🔒 Security & Compliance

### Data Protection
- No storage of sensitive user data
- Secure API key management
- Encrypted data transmission

### Compliance Guardrails
- Strict topic restrictions
- Content filtering and sanitization
- Audit logging for compliance

### Rate Limiting
- API rate limiting
- User request throttling
- Resource usage monitoring

## 📚 API Documentation

### Models
- `UserProfile`: User demographic and financial information
- `CreditCard`: Complete card data following the ontology
- `CardRecommendation`: Ranked recommendation with rationale
- `ComparisonResult`: Detailed comparison analysis
- `AgentResponse`: Standardized response format

### Tools
- `CreditScoreCheckTool`: External credit score verification
- `CardDataIngestionTool`: Multi-source data collection
- `EligibilityRuleEngineTool`: Rule-based eligibility checking
- `ComplianceGuardrailTool`: Content safety verification
- `RewardsCalculatorTool`: Rewards value calculation

## 🤝 Contributing

### Development Setup
```bash
git clone <repository>
cd 13-credit-card-agent
pip install -e .
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings
- Include unit tests

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation
- Review existing issues
- Create a new issue with detailed information

## 🔮 Future Enhancements

### Planned Features
- Real-time credit score integration
- Advanced ML-based recommendations
- Mobile app integration
- Voice interface support
- Multi-language support

### Scalability Improvements
- Horizontal agent scaling
- Distributed data processing
- Advanced caching strategies
- Performance optimization

---

**Note**: This is a demonstration system. For production use, ensure proper security measures, data validation, and compliance with financial regulations.
