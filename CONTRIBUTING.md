# Contributing to Anymouse

Thank you for your interest in contributing to Anymouse! This document provides guidelines and information for contributors.

## 🤝 Code of Conduct

This project adheres to a code of conduct adapted from the [Contributor Covenant](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code.

### Our Standards

- **Be respectful**: Treat everyone with respect and consideration
- **Be inclusive**: Welcome contributors from all backgrounds and experience levels  
- **Be collaborative**: Work together constructively and give helpful feedback
- **Be professional**: Keep discussions focused on the project and avoid personal attacks

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- AWS CLI configured with appropriate permissions
- Docker for containerized deployments
- Git for version control

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/anymouse.git
   cd anymouse
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   python -m spacy download en_core_web_sm
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Verify the setup**
   ```bash
   python -m pytest tests/
   ```

## 📋 Development Workflow

### Branching Strategy

We use a Git flow-inspired branching model:

- **`main`**: Production-ready code, deployed to staging
- **`develop`**: Integration branch for features, deployed to development
- **`feature/*`**: Feature development branches
- **`hotfix/*`**: Critical bug fixes for production
- **`release/*`**: Release preparation branches

### Creating a Feature Branch

```bash
# Create and switch to feature branch
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name

# Make your changes
# ... code, test, commit ...

# Push and create pull request
git push origin feature/your-feature-name
```

### Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or tooling changes
- `security`: Security improvements

**Examples:**
```bash
feat(anonymize): add support for custom entity patterns
fix(lambda): resolve cold start timeout issue  
docs(api): update anonymization endpoint examples
test(integration): add AWS service integration tests
security(auth): implement API key rotation
```

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/ -m "not integration"
python -m pytest tests/ -m "not performance"

# Run with coverage
python -m pytest tests/ --cov=anymouse --cov-report=html

# Run integration tests (requires AWS credentials)
python -m pytest tests/integration/ \
  --api-url https://your-api-gateway-url \
  --api-key your-api-key
```

### Test Categories

Use pytest markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_basic_functionality():
    pass

@pytest.mark.integration  
def test_aws_integration():
    pass

@pytest.mark.performance
def test_load_handling():
    pass

@pytest.mark.slow
def test_comprehensive_scenario():
    pass
```

### Writing Good Tests

- **Unit tests**: Test individual functions and classes in isolation
- **Integration tests**: Test interactions between components
- **End-to-end tests**: Test complete user workflows
- **Performance tests**: Verify performance requirements

**Test Guidelines:**
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Mock external dependencies in unit tests
- Use fixtures for common test setup
- Aim for >80% code coverage

## 🏗️ Architecture Guidelines

### Code Organization

```
anymouse/
├── __init__.py          # Package initialization
├── lambda_handler.py    # AWS Lambda entry point
├── anonymize.py         # Core anonymization logic
├── deanonymize.py       # Core deanonymization logic
└── config.py           # Configuration management

tests/
├── unit/               # Unit tests
├── integration/        # Integration tests
└── performance/        # Performance tests
```

### Design Principles

- **Stateless**: No persistent state between requests
- **Secure by default**: No sensitive data in logs or storage
- **Performance first**: Optimize for sub-second response times
- **Cloud native**: Designed for AWS Lambda and serverless
- **Type safe**: Use type hints and mypy for type checking

### Adding New Features

When adding new features:

1. **Design**: Consider API design and backward compatibility
2. **Security**: Ensure no PII exposure or security vulnerabilities
3. **Performance**: Profile and optimize for Lambda constraints
4. **Testing**: Add comprehensive tests for all code paths
5. **Documentation**: Update README and API docs

## 🔍 Code Quality Standards

### Code Formatting

We use automated code formatting tools:

```bash
# Format code
black anymouse/ tests/
isort anymouse/ tests/

# Check formatting
black --check anymouse/ tests/
isort --check-only anymouse/ tests/
```

### Linting

```bash
# Lint code
flake8 anymouse/ tests/
mypy anymouse/
bandit -r anymouse/
```

### Pre-commit Hooks

Pre-commit hooks automatically run quality checks:

```bash
# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## 🚀 Deployment and Infrastructure

### Local Testing

```bash
# Build container locally
docker build -f Dockerfile.optimized -t anymouse:local .

# Test container
docker run --rm anymouse:local python -c "import anymouse.lambda_handler"
```

### Infrastructure Changes

When modifying AWS infrastructure:

1. **Test locally**: Validate CloudFormation templates
2. **Deploy to dev**: Test in development environment
3. **Review costs**: Ensure changes don't increase costs significantly
4. **Update docs**: Document new parameters and features

```bash
# Validate CloudFormation template
sam validate --template-file template.yaml

# Deploy to development
./deploy.sh dev

# Run integration tests
./test-deployment.sh dev
```

## 📚 Documentation Guidelines

### Code Documentation

- **Docstrings**: Use Google-style docstrings for all public functions
- **Type hints**: Add type hints to all function signatures
- **Comments**: Explain complex logic and business rules

**Example:**
```python
def anonymize_text(text: str) -> dict:
    """Anonymize PERSON, ORG, GPE, and DATE entities in free-form text.

    Parameters
    ----------
    text : str
        Input text possibly containing entities.

    Returns
    -------
    dict
        Dictionary with keys:
        - message: text with entities replaced by placeholders
        - tokens: mapping from placeholder to original entity
        - fields: list of entity types anonymized

    Examples
    --------
    >>> result = anonymize_text("Hello Dr. Smith")
    >>> result["message"]
    "Hello [name1]"
    """
```

### API Documentation

- Keep README examples up to date
- Include response examples for all endpoints
- Document error codes and messages
- Provide curl examples for all endpoints

### Infrastructure Documentation

- Document all CloudFormation parameters
- Include deployment examples
- Explain monitoring and alerting setup
- Provide troubleshooting guides

## 🔒 Security Guidelines

### Secure Coding Practices

- **Input validation**: Validate all user inputs
- **Output sanitization**: Never log sensitive data
- **Authentication**: Verify API keys on every request
- **Authorization**: Use least-privilege IAM policies
- **Encryption**: Encrypt data in transit and at rest

### Security Review Process

1. **Automated scanning**: Run Bandit and Safety checks
2. **Manual review**: Review code for security issues
3. **Dependency scanning**: Check for vulnerable dependencies
4. **Container scanning**: Scan container images for vulnerabilities

### Reporting Security Issues

For security vulnerabilities, please:

1. **Do not** create public GitHub issues
2. Email security@anymouse.dev with details
3. Include steps to reproduce the issue
4. Allow time for investigation and fix

## 📋 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Security checks pass
- [ ] No breaking changes (or properly documented)

### PR Template

Use this template for pull requests:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that breaks existing functionality)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass  
- [ ] Manual testing completed

## Security
- [ ] No sensitive data exposed
- [ ] Security scans pass
- [ ] IAM permissions follow least privilege

## Performance
- [ ] Performance impact assessed
- [ ] Load tests pass (if applicable)
- [ ] Memory usage reasonable

## Documentation
- [ ] README updated
- [ ] API docs updated
- [ ] CHANGELOG updated
```

### Review Process

1. **Automated checks**: CI/CD pipeline runs all checks
2. **Code review**: At least one maintainer reviews code
3. **Security review**: Security-focused review for sensitive changes
4. **Performance review**: Performance impact assessment
5. **Documentation review**: Ensure docs are accurate and complete

### Merging

- **Squash and merge**: Use for feature branches
- **Merge commit**: Use for release branches
- **Rebase and merge**: Use for small, clean commits

## 🎯 Issue Guidelines

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
Clear description of the issue

**To Reproduce**
Steps to reproduce the behavior

**Expected behavior**
What you expected to happen

**Environment**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.9.7]
- AWS region: [e.g. us-east-1]

**Additional context**
Logs, screenshots, etc.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
Description of the problem

**Describe the solution you'd like**
Clear description of desired functionality

**Describe alternatives considered**
Alternative solutions considered

**Additional context**
Mockups, examples, etc.
```

## 🏷️ Release Process

### Version Bumping

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with release notes
3. Create release branch: `release/vX.Y.Z`
4. Test thoroughly in staging environment
5. Create tag: `git tag vX.Y.Z`
6. Push tag to trigger production deployment

### Release Notes

Include in release notes:
- New features and improvements
- Bug fixes and security updates
- Breaking changes and migration guide
- Performance improvements
- Infrastructure changes

## 🆘 Getting Help

### Community Support

- **GitHub Discussions**: Ask questions and share ideas
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check README and docs folder

### Maintainer Contact

- **General questions**: Create GitHub discussion
- **Security issues**: Email security@anymouse.dev
- **Urgent issues**: Tag maintainers in GitHub issues

## 🙏 Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes for significant contributions
- README acknowledgments

Thank you for contributing to Anymouse! 🎉