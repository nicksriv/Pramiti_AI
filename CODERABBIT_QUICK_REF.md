# CodeRabbit Quick Reference

## ⚡ Quick Start

### Automatic Reviews
CodeRabbit reviews your code automatically on:
- ✓ Every commit
- ✓ Every push
- ✓ Pull requests

### View Reviews
1. **Inline**: Look for CodeRabbit comments in your code
2. **Problems Panel**: `Cmd+Shift+M` (macOS) or `Ctrl+Shift+M` (Windows/Linux)
3. **Output**: View → Output → Select "CodeRabbit"

## 🎯 Review Focus Areas

Current configuration focuses on:
- 🔒 **Security** - API keys, secrets, vulnerabilities
- ⚡ **Performance** - Async issues, complexity, memory
- 🐛 **Bugs** - Potential errors, edge cases
- 📋 **Best Practices** - PEP 8, code patterns
- 🎨 **Code Quality** - Maintainability, documentation

## 📊 Review Levels

| Level | Speed | Coverage | Use Case |
|-------|-------|----------|----------|
| Basic | Fast | Critical only | Quick checks |
| Standard | Medium | Common issues | Daily development |
| Detailed | Slower | Deep analysis | Pre-release |
| **Comprehensive** | Slowest | Complete | **Current setting** |

## 🔧 Common Commands

### VS Code Command Palette (`Cmd+Shift+P`)
```
CodeRabbit: Review Current File
CodeRabbit: Review Changes
CodeRabbit: Show Documentation
CodeRabbit: Configure Settings
```

### Git Integration
```bash
git commit    # Triggers auto-review
git push      # Reviews pushed changes
```

## 📝 Configuration Files

```
.coderabbit.yaml        # Main configuration
.coderabbitignore       # Excluded files
.vscode/settings.json   # VS Code settings
CODERABBIT_CONFIG.md    # Full documentation
```

## ⚙️ Quick Settings Changes

### Change Review Level
Edit `.coderabbit.yaml`:
```yaml
reviews:
  level: standard  # basic | standard | detailed | comprehensive
```

### Enable/Disable Auto-Review
Edit `.vscode/settings.json`:
```json
{
  "coderabbit.autoReview": true,      // Enable/disable
  "coderabbit.reviewOnCommit": true   // Review on commit
}
```

### Focus on Specific Areas
Edit `.coderabbit.yaml`:
```yaml
focus_areas:
  - security       # Keep
  - performance    # Keep
  # - documentation  # Comment out to skip
```

## 🚨 Handling Review Results

### Critical Issues (Red) 🔴
- **Must fix**: Security vulnerabilities, bugs
- **Block commits**: Should be resolved before merge

### Warnings (Yellow) 🟡
- **Should fix**: Performance, code quality
- **Review carefully**: May have valid reasons to ignore

### Suggestions (Blue) 🔵
- **Consider**: Best practices, improvements
- **Optional**: Team decision on adoption

## 🎯 Project-Specific Checks

Enabled for Pramiti AI:

### FastAPI
- ✓ Async endpoint validation
- ✓ Type hints on routes
- ✓ Response models
- ✓ Error handlers

### OpenAI Integration
- ✓ API key security
- ✓ Rate limiting
- ✓ Timeout handling
- ✓ Token management

### Database
- ✓ Connection pooling
- ✓ SQL injection prevention
- ✓ Proper connection closing

### Docker
- ✓ Dockerfile best practices
- ✓ Security scanning
- ✓ Environment variables

## 📈 Metrics Tracked

- Code Quality Score
- Security Vulnerabilities
- Test Coverage (target: 70%)
- Code Complexity (max: 10)
- Documentation Coverage

## 🔍 Example Review

```python
# ❌ CodeRabbit will flag this:
async def get_data(id):  # Missing type hints
    result = db.query(f"SELECT * FROM users WHERE id={id}")  # SQL injection
    return result

# ✅ CodeRabbit approves this:
async def get_data(user_id: int) -> Dict[str, Any]:
    result = await db.query(
        "SELECT * FROM users WHERE id = :id",
        {"id": user_id}
    )
    return result
```

## 💡 Tips

1. **Commit Often**: Get feedback early
2. **Read Suggestions**: AI learns from context
3. **Customize**: Adjust config for your workflow
4. **Track Metrics**: Monitor code quality trends
5. **Team Alignment**: Share config with team

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| No reviews appearing | Check extension is enabled in VS Code |
| Too many suggestions | Lower review level to 'standard' |
| Missing file reviews | Check `.coderabbitignore` |
| Slow reviews | Disable `reviewOnSave`, keep `reviewOnCommit` |

## 📚 Learn More

- Full docs: `CODERABBIT_CONFIG.md`
- VS Code settings: `.vscode/settings.json`
- Main config: `.coderabbit.yaml`
- CodeRabbit extension: Search in VS Code marketplace

---

**Current Config**: Comprehensive | Auto-review: ON | Focus: Security, Performance, Bugs
