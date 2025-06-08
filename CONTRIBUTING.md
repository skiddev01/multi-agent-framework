# Contributing to Multi-Agent Framework

We welcome contributions! This guide will help you get started.

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/multi-agent-framework.git
   cd multi-agent-framework
   ```

2. **Setup Development Environment**
   ```bash
   # On Windows:
   scripts\setup.bat
   # On Unix/Linux/Mac:
   ./scripts/setup.sh
   ```

3. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Standards

### Python Style
- Follow PEP 8
- Use Black for formatting
- Use isort for import sorting
- Type hints for all functions
- Docstrings for all public methods

### Testing Requirements
- Unit tests for all new code
- Integration tests for workflows
- Behavioral tests for user scenarios
- Minimum 80% code coverage

## Submission Process

1. **Before Submitting**
   ```bash
   # Run tests
   pytest tests/
   
   # Run linting
   black src tests
   isort src tests
   flake8 src tests
   ```

2. **Commit Guidelines**
   - Use conventional commits
   - Clear, descriptive messages
   - Reference issues when applicable

3. **Pull Request**
   - Fill out PR template completely
   - Link to related issues
   - Include screenshots if UI changes
   - Request review from maintainers

Thank you for contributing!
