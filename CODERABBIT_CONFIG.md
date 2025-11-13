# CodeRabbit Configuration Guide

## Overview
This project uses CodeRabbit for AI-powered code reviews. CodeRabbit automatically reviews your commits and provides intelligent suggestions for improving code quality, security, and performance.

## Configuration Files

### `.coderabbit.yaml`
Main configuration file with comprehensive review settings:
- **Review Level**: Comprehensive (can be: basic, standard, detailed, comprehensive)
- **Focus Areas**: Security, performance, bugs, best practices, code quality, maintainability
- **Python Version**: 3.11 with type checking and PEP 8 compliance
- **Security**: Enabled with secrets detection and dependency scanning
- **Testing**: Requires 70% minimum code coverage

### `.vscode/settings.json`
VS Code workspace settings for CodeRabbit integration:
- Auto-review on commit enabled
- Comprehensive review level
- Shows suggestions in problems panel
- Python formatting and linting enabled

### `.coderabbitignore`
Files and patterns excluded from CodeRabbit reviews:
- Python cache files
- Virtual environments
- Test coverage reports
- Environment variables
- SSH keys and credentials

## Key Features Enabled

### 🔒 Security
- Secret detection in code
- Dependency vulnerability scanning
- API key security checks
- SQL injection detection
- Environment variable validation

### ⚡ Performance
- Complexity analysis (max complexity: 10)
- Memory leak detection
- Async function optimization
- Database connection management

### 🐛 Code Quality
- PEP 8 compliance
- Type checking
- Anti-pattern detection
- Code coverage monitoring (70% minimum)
- Documentation requirements

### 🧪 Testing
- Test coverage requirements
- Test quality analysis
- Async endpoint testing

### 🚀 FastAPI Specific
- Async endpoint validation
- Type hints verification
- Response model checks
- Error handling validation

### 🤖 OpenAI Integration
- API key security
- Rate limiting checks
- Token management
- Error handling

### 🐳 Docker/Deployment
- Dockerfile best practices
- Security vulnerability scanning
- Environment variable checks

## How to Use

### Automatic Reviews
CodeRabbit automatically reviews your code when you:
1. Commit changes (`git commit`)
2. Push to repository (`git push`)
3. Create pull requests

### Manual Review
To manually trigger a review:
1. Open Command Palette (Cmd+Shift+P on macOS)
2. Type "CodeRabbit: Review Current File"
3. Select the command

### View Reviews
- **Inline Comments**: Suggestions appear directly in your code
- **Problems Panel**: View all issues in VS Code Problems panel
- **Output Channel**: Detailed logs in CodeRabbit output channel

### Review Levels

You can adjust the review level in `.coderabbit.yaml`:

```yaml
reviews:
  level: comprehensive  # Options: basic, standard, detailed, comprehensive
```

- **Basic**: Quick checks for critical issues
- **Standard**: Common code quality and security issues
- **Detailed**: In-depth analysis with suggestions
- **Comprehensive**: Full analysis including documentation, testing, and best practices

## Custom Rules

### For This Project

The configuration includes custom prompts specific to Pramiti AI:
- ✓ Error handling in async functions
- ✓ OpenAI API timeout handling
- ✓ Database connection management
- ✓ SQL injection prevention
- ✓ Environment variable validation
- ✓ Blockchain logging verification

## Configuration Tips

### Adjust Review Frequency
Edit `.vscode/settings.json`:
```json
{
  "coderabbit.reviewOnSave": false,    // Review on every save
  "coderabbit.reviewOnCommit": true    // Review on commit
}
```

### Change Focus Areas
Edit `.coderabbit.yaml`:
```yaml
focus_areas:
  - security          # High priority
  - performance       # High priority
  - bugs              # High priority
  - best_practices    # Medium priority
  - code_quality      # Medium priority
```

### Exclude Files
Add patterns to `.coderabbitignore`:
```
# Exclude specific files
config/secrets.py

# Exclude directories
data/
temp/
```

## Integration with Git Workflow

### Pre-commit Review
CodeRabbit reviews code before you commit, helping catch issues early.

### Pull Request Review
When you create a PR, CodeRabbit provides:
- Summary of changes
- Security concerns
- Performance suggestions
- Code quality improvements

### Commit Messages
CodeRabbit can suggest better commit messages based on your changes.

## Troubleshooting

### Reviews Not Appearing
1. Check CodeRabbit is enabled: `.vscode/settings.json` → `"coderabbit.enabled": true`
2. Verify extension is installed and active
3. Check Output panel for CodeRabbit logs

### Too Many Suggestions
Reduce review level:
```yaml
reviews:
  level: standard  # Instead of comprehensive
```

### Missing Reviews for Specific Files
1. Check `.coderabbitignore` doesn't exclude the files
2. Verify file patterns in `.coderabbit.yaml` include section

## Best Practices

1. **Review Before Commit**: Always review CodeRabbit suggestions before committing
2. **Address Critical Issues**: Fix security and bug issues immediately
3. **Consider Suggestions**: Performance and quality suggestions are valuable but contextual
4. **Update Configuration**: Adjust settings based on team needs
5. **Keep Config in Sync**: Commit configuration changes to share with team

## Metrics and Reporting

CodeRabbit generates reports including:
- Code quality score
- Security vulnerabilities found
- Performance issues
- Test coverage
- Documentation coverage

Access reports through:
- VS Code CodeRabbit panel
- GitHub PR comments
- Output channel logs

## Support

For issues or questions:
- VS Code Command Palette → "CodeRabbit: Show Documentation"
- Extension settings: Search "CodeRabbit" in VS Code settings
- GitHub: Check CodeRabbit comments on PRs

## Version History

- **v1.0** (Nov 2025): Initial comprehensive configuration for Pramiti AI
  - Comprehensive review level
  - Python 3.11 support
  - FastAPI specific checks
  - OpenAI integration validation
  - Docker deployment checks
