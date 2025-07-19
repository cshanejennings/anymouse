# Anymouse: Stateless Anonymization Service

[![Deploy](https://github.com/your-org/anymouse/workflows/Deploy%20Anymouse%20Service/badge.svg)](https://github.com/your-org/anymouse/actions)
[![Coverage](https://codecov.io/gh/your-org/anymouse/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/anymouse)
[![Security](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)

Anymouse is a production-ready AWS Lambda service for anonymizing and deanonymizing sensitive data using tokenization. Designed for healthcare and administrative integrations, it provides stateless, scalable data protection with sub-second latency.

## ✨ Features

- **🔒 Stateless Design**: No server-side data storage - all mappings returned to client
- **⚡ High Performance**: Handles 10-100 RPS with sub-second latency
- **🧠 Smart NER**: Uses spaCy for detecting PERSON, ORG, GPE, and DATE entities
- **🛡️ Security First**: API key auth, WAF protection, audit-safe logging
- **📊 Production Ready**: CloudWatch monitoring, alerting, and performance optimization
- **🚀 Auto-scaling**: AWS Lambda with configurable provisioned concurrency

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- Docker installed
- Python 3.9+ (for local development)

### Deploy to AWS

```bash
# Clone the repository
git clone https://github.com/your-org/anymouse
cd anymouse

# Deploy to development environment
./deploy.sh dev

# Test the deployment
./test-deployment.sh dev

# Set up monitoring (optional)
./setup-alerts.sh dev your-email@company.com
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=anymouse --cov-report=html
```

## 📡 API Usage

### Anonymize Text

```bash
curl -X POST https://your-api-gateway-url/anonymize \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "payload": "Hello Dr. Smith, this is a message from Jane Doe about the appointment."
  }'
```

**Response:**
```json
{
  "message": "Hello [name1], this is a message from [name2] about the appointment.",
  "tokens": {
    "[name1]": "Dr. Smith",
    "[name2]": "Jane Doe"
  },
  "fields": ["PERSON"]
}
```

### Deanonymize Text

```bash
curl -X POST https://your-api-gateway-url/deanonymize \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "message": "Hello [name1], this is a message from [name2] about the appointment.",
    "tokens": {
      "[name1]": "Dr. Smith",
      "[name2]": "Jane Doe"
    }
  }'
```

**Response:**
```json
{
  "message": "Hello Dr. Smith, this is a message from Jane Doe about the appointment."
}
```

### Structured Data Anonymization

```bash
curl -X POST https://your-api-gateway-url/anonymize \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "payload": {
      "patient_name": "John Smith",
      "doctor": "Dr. Johnson",
      "appointment_date": "2024-03-15"
    },
    "config": {
      "fields": ["patient_name", "doctor"]
    }
  }'
```

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  API Gateway│    │   Lambda    │    │   spaCy NER │
│             │────│             │────│             │
│ ✓ Auth      │    │ ✓ Stateless │    │ ✓ Multi-lang│
│ ✓ Throttling│    │ ✓ Auto-scale│    │ ✓ Entities  │
│ ✓ WAF       │    │ ✓ Monitoring│    │ ✓ Patterns  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
               ┌─────────────────────┐
               │   AWS Services      │
               │                     │
               │ • CloudWatch Logs   │
               │ • SSM Parameters    │
               │ • S3 Config         │
               │ • X-Ray Tracing     │
               └─────────────────────┘
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PYTHONPATH` | Python module path | `/var/task` |
| `PYTHONDONTWRITEBYTECODE` | Disable .pyc files | `1` |
| `SPACY_MODEL_PATH` | Custom spaCy model path | Auto-detect |

### SAM Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `Stage` | Deployment environment | `dev` |
| `LambdaMemorySize` | Memory allocation (MB) | `1024` |
| `ProvisionedConcurrency` | Warm instances | `0` |
| `EnableWAF` | Enable AWS WAF | `false` |
| `AllowedIPs` | IP allowlist (CIDR) | `0.0.0.0/0` |

### Example Deployment with Custom Settings

```bash
./deploy.sh prod \
  --parameter-overrides \
  LambdaMemorySize=2048 \
  ProvisionedConcurrency=5 \
  EnableWAF=true \
  AllowedIPs="10.0.0.0/8,192.168.1.0/24"
```

## 📊 Performance & Monitoring

### Performance Targets

- **Throughput**: 10-100 requests/second
- **Latency**: P95 < 1000ms, P99 < 2000ms  
- **Availability**: 99.9% uptime
- **Error Rate**: < 0.1% under normal load

### Run Performance Tests

```bash
# Install performance testing dependencies
pip install aiohttp pandas matplotlib

# Run comprehensive performance suite
./run_performance_tests.sh dev

# Custom load test
python load_test.py \
  --api-url https://your-api-gateway-url \
  --api-key your-api-key \
  --rps 50 \
  --duration 60 \
  --payload-type medium
```

### Monitoring

- **CloudWatch Dashboard**: Auto-created with deployment
- **Alerts**: Email notifications for errors and high latency
- **Logs**: Structured JSON logs (no PII exposure)
- **Metrics**: Custom business metrics for anonymization requests

## 🔐 Security

### Authentication & Authorization

- **API Key**: Required for all requests (stored in SSM)
- **IP Allowlist**: Configurable CIDR block restrictions
- **WAF Protection**: Optional AWS WAF with rate limiting
- **IAM Roles**: Least-privilege access policies

### Data Protection

- **Stateless**: No persistent storage of sensitive data
- **Audit Logs**: IP addresses and timestamps only (no payload data)
- **Encryption**: Data encrypted in transit and at rest
- **Token Security**: Deterministic but non-reversible without mapping

### Security Scanning

```bash
# Run security checks
bandit -r anymouse/
safety check -r requirements.txt

# Container security scan (via CI/CD)
trivy image your-ecr-repo/anymouse:latest
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=anymouse --cov-report=html

# Run specific test categories
python -m pytest tests/ -m "not integration"
```

### Integration Tests

```bash
# Test against real AWS deployment
python -m pytest tests/integration/ \
  --api-url https://your-api-gateway-url \
  --api-key your-api-key
```

### Load Testing

```bash
# Quick performance check
./run_performance_tests.sh dev

# Detailed load testing
python load_test.py --help
```

## 🚀 CI/CD Pipeline

The project includes comprehensive GitHub Actions workflows:

### Pull Request Checks

- **Code Quality**: Black, isort, flake8, mypy
- **Security**: Bandit, safety, dependency scanning
- **Tests**: Unit tests with coverage reporting
- **Infrastructure**: CloudFormation validation
- **Container**: Docker build verification

### Deployment Pipeline

- **Development**: Auto-deploy from `develop` branch
- **Staging**: Auto-deploy from `main` branch with performance tests
- **Production**: Deploy on version tags with full validation

### Environments

| Environment | Branch/Tag | Features |
|-------------|------------|----------|
| Development | `develop` | Basic deployment, integration tests |
| Staging | `main` | Performance tests, WAF enabled |
| Production | `v*` tags | Full security, monitoring, alerts |

## 📖 Implementation Guide

### Core Components

The Anymouse service consists of four main Python modules:

#### 1. `anymouse/lambda_handler.py` - AWS Lambda Entry Point

The main Lambda handler that routes requests and manages authentication:

```python
from anymouse.lambda_handler import lambda_handler

# Handles all API Gateway events
# Routes to: /anonymize, /deanonymize, /config/test
# Manages: Authentication, logging, error handling
```

**Key Features:**
- API key authentication via SSM Parameter Store
- Request routing and validation
- Audit-safe logging (no PII exposure)
- Error handling and HTTP response formatting

#### 2. `anymouse/anonymize.py` - Core Anonymization Logic

Handles text and structured data anonymization with spaCy NER:

```python
from anymouse.anonymize import anonymize_text, anonymize_payload

# Free-form text anonymization
result = anonymize_text("Hello Dr. Smith, message from Jane Doe")
# Returns: {"message": "Hello [name1], message from [name2]", 
#          "tokens": {"[name1]": "Dr. Smith", "[name2]": "Jane Doe"}}

# Structured data anonymization  
result = anonymize_payload(
    {"patient": "John Smith", "notes": "Follow up needed"}, 
    {"fields": ["patient"]}
)
```

**Supported Entity Types:**
- **PERSON**: Names, titles (Dr., Mr., Ms., Mrs.)
- **ORG**: Organizations, companies
- **GPE**: Geographic locations (cities, countries)
- **DATE**: Dates and temporal expressions

#### 3. `anymouse/deanonymize.py` - Deanonymization Logic

Reverses anonymization using client-provided token mappings:

```python
from anymouse.deanonymize import deanonymize_text

# Restore original text
original = deanonymize_text(
    "Hello [name1], message from [name2]",
    {"[name1]": "Dr. Smith", "[name2]": "Jane Doe"}
)
# Returns: "Hello Dr. Smith, message from Jane Doe"
```

#### 4. `anymouse/config.py` - Configuration Management

Handles validation and loading of anonymization configurations:

```python
from anymouse.config import validate_config, load_config_from_s3

# Validate field configuration
config = validate_config({"fields": ["name", "email", "ssn"]})

# Load from S3
config = load_config_from_s3("my-bucket", "config.json")
```

### Implementation Patterns

#### Lazy Loading for Performance

The service uses lazy loading for the spaCy NER model to optimize cold start performance:

```python
# Global model instance - loaded only when needed
_NLP = None
_SPACY_AVAILABLE = None

def _get_nlp_model():
    """Lazy load spaCy model to improve cold start performance."""
    global _NLP, _SPACY_AVAILABLE
    
    if _SPACY_AVAILABLE is None:
        try:
            import spacy
            _NLP = spacy.load("en_core_web_sm")
            # Add custom patterns for medical titles
            _SPACY_AVAILABLE = True
        except Exception:
            _SPACY_AVAILABLE = False
            _NLP = None
    
    return _NLP if _SPACY_AVAILABLE else None
```

#### Stateless Design

All functions are stateless and return complete mappings:

```python
def anonymize_text(text: str) -> dict:
    """
    Returns complete anonymization result including:
    - message: anonymized text with tokens
    - tokens: mapping from tokens to original values  
    - fields: list of entity types processed
    """
    # No state stored - everything returned to client
    return {"message": anonymized, "tokens": mappings, "fields": types}
```

## 🛠️ Advanced Usage Guide

### Custom Entity Patterns

Add custom patterns to the spaCy EntityRuler for domain-specific entities:

```python
# In anonymize.py, modify the patterns list
patterns = [
    # Medical titles
    {"label": "PERSON", "pattern": [{"TEXT": {"REGEX": r"^(Dr\.|Mr\.|Ms\.|Mrs\.)"}}, {"POS": "PROPN"}]},
    
    # Custom hospital pattern
    {"label": "ORG", "pattern": [{"TEXT": "Sunnybrook"}, {"TEXT": "Hospital"}]},
    
    # Add your custom patterns here
    {"label": "PERSON", "pattern": [{"TEXT": "Patient"}, {"POS": "PROPN"}]},
    {"label": "ORG", "pattern": [{"TEXT": {"REGEX": r".*Medical Center$"}}]}
]
```

### Environment-Specific Configuration

#### Development Environment

```bash
# Deploy with minimal resources
./deploy.sh dev \
  --parameter-overrides \
  LambdaMemorySize=512 \
  ProvisionedConcurrency=0 \
  EnableWAF=false
```

#### Production Environment

```bash
# Deploy with full security and performance
./deploy.sh prod \
  --parameter-overrides \
  LambdaMemorySize=2048 \
  ProvisionedConcurrency=5 \
  EnableWAF=true \
  AllowedIPs="10.0.0.0/8,192.168.1.0/24"
```

### S3 Configuration Management

Store anonymization configurations in S3 for dynamic updates:

```json
{
  "fields": ["patient_name", "doctor_name", "ssn", "dob"],
  "entity_types": ["PERSON", "DATE"],
  "custom_patterns": [
    {
      "label": "PERSON", 
      "pattern": [{"TEXT": "Patient"}, {"POS": "PROPN"}]
    }
  ]
}
```

**Upload configuration:**

```bash
aws s3 cp config.json s3://anymouse-config-prod/config.json
```

**Use in API call:**

```bash
curl -X POST https://your-api-gateway-url/anonymize \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "payload": {"patient_name": "John Doe", "notes": "Patient doing well"},
    "config_source": {
      "s3": {"bucket": "anymouse-config-prod", "key": "config.json"}
    }
  }'
```

### Batch Processing Pattern

While the service is designed for single requests, you can implement batch processing at the client level:

```python
import asyncio
import aiohttp

async def batch_anonymize(texts, api_url, api_key):
    """Process multiple texts concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for text in texts:
            task = session.post(
                f"{api_url}/anonymize",
                json={"payload": text},
                headers={"X-API-Key": api_key}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        return [await r.json() for r in responses]

# Usage
texts = ["Hello Dr. Smith", "Message from Jane Doe", "Call John Wilson"]
results = await batch_anonymize(texts, api_url, api_key)
```

### Integration Patterns

#### Healthcare EMR Integration

```python
class EMRAnonymizer:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
    
    def anonymize_patient_record(self, record):
        """Anonymize a patient record while preserving structure."""
        response = requests.post(
            f"{self.api_url}/anonymize",
            json={
                "payload": record,
                "config": {
                    "fields": ["patient_name", "doctor_name", "emergency_contact"]
                }
            },
            headers={"X-API-Key": self.api_key}
        )
        return response.json()
    
    def process_clinical_notes(self, notes):
        """Anonymize free-form clinical notes."""
        response = requests.post(
            f"{self.api_url}/anonymize", 
            json={"payload": notes},
            headers={"X-API-Key": self.api_key}
        )
        return response.json()
```

#### Email Processing Integration

```python
def anonymize_email_thread(email_content):
    """Anonymize email while preserving thread structure."""
    
    # Split email into header and body
    lines = email_content.split('\n')
    header_end = next(i for i, line in enumerate(lines) if line.strip() == '')
    
    header = '\n'.join(lines[:header_end])
    body = '\n'.join(lines[header_end:])
    
    # Anonymize body only (preserve email headers for routing)
    response = requests.post(
        f"{api_url}/anonymize",
        json={"payload": body},
        headers={"X-API-Key": api_key}
    )
    
    result = response.json()
    
    # Reconstruct email with anonymized body
    anonymized_email = header + '\n' + result['message']
    
    return {
        "email": anonymized_email,
        "tokens": result['tokens'],  # Store securely for later deanonymization
        "original_body": body
    }
```

### Error Handling and Retries

Implement robust error handling for production use:

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    response = func(*args, **kwargs)
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 429:  # Rate limited
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                        continue
                    else:
                        response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=2)
def anonymize_with_retry(text, api_url, api_key):
    return requests.post(
        f"{api_url}/anonymize",
        json={"payload": text},
        headers={"X-API-Key": api_key}
    )
```

### Monitoring and Observability

#### Custom Metrics Collection

```python
import boto3

def track_anonymization_metrics(entity_count, processing_time, text_length):
    """Send custom metrics to CloudWatch."""
    cloudwatch = boto3.client('cloudwatch')
    
    cloudwatch.put_metric_data(
        Namespace='Anymouse/Business',
        MetricData=[
            {
                'MetricName': 'EntitiesProcessed',
                'Value': entity_count,
                'Unit': 'Count'
            },
            {
                'MetricName': 'ProcessingTime',
                'Value': processing_time,
                'Unit': 'Milliseconds'
            },
            {
                'MetricName': 'TextLength',
                'Value': text_length,
                'Unit': 'Bytes'
            }
        ]
    )
```

#### Health Check Implementation

```python
def health_check(api_url, api_key):
    """Verify service health with a simple test."""
    test_payload = "Hello Dr. Test"
    
    try:
        # Test anonymization
        response = requests.post(
            f"{api_url}/anonymize",
            json={"payload": test_payload},
            headers={"X-API-Key": api_key},
            timeout=10
        )
        
        if response.status_code != 200:
            return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        
        result = response.json()
        
        # Test deanonymization
        deano_response = requests.post(
            f"{api_url}/deanonymize",
            json={
                "message": result["message"],
                "tokens": result["tokens"]
            },
            headers={"X-API-Key": api_key},
            timeout=10
        )
        
        if deano_response.status_code != 200:
            return {"status": "unhealthy", "error": "Deanonymization failed"}
        
        deano_result = deano_response.json()
        
        # Verify round-trip
        if deano_result["message"] == test_payload:
            return {"status": "healthy", "latency": response.elapsed.total_seconds()}
        else:
            return {"status": "unhealthy", "error": "Round-trip verification failed"}
            
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Performance Optimization Tips

#### Client-Side Optimization

1. **Connection Pooling**: Use persistent connections for high-volume processing
2. **Async Processing**: Use async HTTP clients for concurrent requests
3. **Caching**: Cache API keys and configuration to reduce overhead
4. **Batch Grouping**: Group similar requests to minimize cold starts

#### Server-Side Tuning

1. **Memory Allocation**: Increase Lambda memory for CPU-intensive NER processing
2. **Provisioned Concurrency**: Use for predictable traffic patterns
3. **Container Optimization**: Use optimized Dockerfile for faster cold starts
4. **Model Caching**: Consider custom spaCy model packaging

### Security Best Practices

#### Token Management

```python
import secrets
import hashlib

class SecureTokenManager:
    """Secure handling of anonymization tokens."""
    
    def __init__(self, encryption_key=None):
        self.encryption_key = encryption_key or secrets.token_bytes(32)
    
    def store_tokens_securely(self, tokens, user_id):
        """Store tokens with encryption and access control."""
        # Encrypt token mappings
        encrypted_tokens = self.encrypt_tokens(tokens)
        
        # Store with user association and expiration
        token_record = {
            "user_id": user_id,
            "tokens": encrypted_tokens,
            "created_at": time.time(),
            "expires_at": time.time() + 3600,  # 1 hour expiration
        }
        
        # Store in secure backend (DynamoDB, encrypted S3, etc.)
        return self.store_to_backend(token_record)
    
    def retrieve_tokens_securely(self, token_id, user_id):
        """Retrieve and decrypt tokens with access control."""
        record = self.retrieve_from_backend(token_id)
        
        # Verify ownership and expiration
        if record["user_id"] != user_id:
            raise PermissionError("Access denied")
        
        if record["expires_at"] < time.time():
            raise ValueError("Tokens expired")
        
        return self.decrypt_tokens(record["tokens"])
```

#### Audit Logging

```python
import json
import logging

class AuditLogger:
    """Audit logging for compliance and security."""
    
    def __init__(self):
        self.logger = logging.getLogger('anymouse.audit')
    
    def log_anonymization(self, user_id, source_ip, entity_count, success=True):
        """Log anonymization request without exposing PII."""
        audit_event = {
            "event_type": "anonymization",
            "user_id": user_id,
            "source_ip": source_ip,
            "entity_count": entity_count,
            "success": success,
            "timestamp": time.time()
        }
        
        self.logger.info(json.dumps(audit_event))
    
    def log_deanonymization(self, user_id, source_ip, token_count, success=True):
        """Log deanonymization request."""
        audit_event = {
            "event_type": "deanonymization", 
            "user_id": user_id,
            "source_ip": source_ip,
            "token_count": token_count,
            "success": success,
            "timestamp": time.time()
        }
        
        self.logger.info(json.dumps(audit_event))
```

## 📚 Documentation

- [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md) - Detailed requirements and specifications
- [`docs/Project-Structure.md`](docs/Project-Structure.md) - Codebase organization
- [`iam-policies.yaml`](iam-policies.yaml) - Reference IAM policies
- [`monitoring.yaml`](monitoring.yaml) - Complete monitoring setup

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run code formatting
black anymouse/ tests/
isort anymouse/ tests/

# Run all checks
pre-commit run --all-files
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🆘 Support

- **Documentation**: [https://anymouse.readthedocs.io](https://anymouse.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/your-org/anymouse/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/anymouse/discussions)

## 🏷️ Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

---

**Made with ❤️ for secure, compliant data processing**
