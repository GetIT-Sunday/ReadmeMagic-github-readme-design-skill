# Contributing to GitHub README Design Skill

Thank you for your interest in contributing! This document provides guidelines and information about contributing to this project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

1. **Clear title** - Describe the bug briefly
2. **Steps to reproduce** - How to trigger the bug
3. **Expected behavior** - What should happen
4. **Actual behavior** - What actually happens
5. **Environment** - OS, Python version, etc.

### Suggesting Features

We welcome feature suggestions! Please create an issue with:

1. **Problem statement** - What problem does this solve?
2. **Proposed solution** - How would you implement it?
3. **Alternatives considered** - Other solutions you thought about
4. **Additional context** - Any other relevant information

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Add tests** (if applicable)
5. **Update documentation** (if needed)
6. **Commit your changes** (`git commit -m 'Add amazing feature'`)
7. **Push to the branch** (`git push origin feature/amazing-feature`)
8. **Create a Pull Request**

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- pip

### Setup

```bash
# Clone your fork
git clone https://github.com/your-username/ReadmeMagic.git
cd ReadmeMagic

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Project Structure

```
ReadmeMagic/
├── SKILL.md                    # Skill documentation
├── README.md                   # Project README
├── templates/                  # Template files
├── examples/                   # Example READMEs
├── src/                        # Source code
├── tests/                      # Test suite
└── docs/                       # Documentation
```

## Coding Standards

### Python Code

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all public functions
- Keep functions small and focused

### Markdown Templates

- Use consistent formatting
- Include placeholders in `{{PLACEHOLDER}}` format
- Add comments where helpful
- Keep templates modular

### Testing

- Write tests for new features
- Maintain test coverage
- Use pytest fixtures when appropriate

## Commit Messages

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "feat: add new AI project template"
git commit -m "fix: resolve badge alignment issue"
git commit -m "docs: update SKILL.md with examples"

# Bad
git commit -m "update"
git commit -m "fix stuff"
git commit -m "changes"
```

### Commit Types

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Pull Request Guidelines

### Before Submitting

1. **Run tests** - Ensure all tests pass
2. **Check formatting** - Use black and flake8
3. **Update documentation** - If adding new features
4. **Add examples** - If applicable

### PR Description

Include:

1. **Summary** - What does this PR do?
2. **Changes** - List of changes
3. **Testing** - How did you test it?
4. **Screenshots** - If UI changes (for preview HTML)

### Review Process

1. PR will be reviewed by maintainers
2. Feedback will be provided
3. Make requested changes
4. PR will be merged when approved

## Adding New Templates

To add a new template:

1. Create template file in `templates/`
2. Use `{{PLACEHOLDER}}` for dynamic content
3. Add example in `examples/`
4. Update `SKILL.md` documentation
5. Add tests if applicable

### Template Guidelines

- Keep templates modular
- Use consistent formatting
- Include comments for complex sections
- Provide clear placeholder descriptions

## Adding New Features

To add a new feature:

1. Create feature branch
2. Implement feature
3. Add tests
4. Update documentation
5. Create PR

### Feature Guidelines

- Follow existing patterns
- Keep backwards compatibility
- Add error handling
- Write clear documentation

## Code Review

### What We Look For

- Code quality
- Test coverage
- Documentation
- Backwards compatibility
- Performance

### Review Process

1. PR submitted
2. Automated checks run
3. Maintainer reviews
4. Feedback provided
5. Changes made
6. PR merged

## Release Process

1. Update version number
2. Update CHANGELOG.md
3. Create release branch
4. Tag release
5. Publish to PyPI

## Getting Help

- **Issues** - For bugs and feature requests
- **Discussions** - For questions and ideas
- **Discord** - For real-time chat

## Code of Conduct

Please follow our Code of Conduct:

- Be respectful
- Be inclusive
- Be constructive
- Be professional

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Thank you for contributing to GitHub README Design Skill! Your help is appreciated.

