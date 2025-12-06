# Repository Structure

## 📁 Clean Repository Structure

### Core Application
```
app/
├── __init__.py
├── main.py                    # FastAPI application
├── recommendation_engine.py  # Collaborative filtering algorithm
├── cache_manager.py          # Caching layer (in-memory + DAX)
├── dynamodb_client.py        # DynamoDB operations
└── local_storage.py          # Local storage for testing
```

### Lambda Functions
```
lambda_functions/
├── __init__.py
└── stream_processor.py        # DynamoDB stream handler
```

### Scripts
```
scripts/
├── __init__.py
└── seed_data.py              # Sample data generator
```

### Tests
```
tests/
├── __init__.py
├── test_recommendations.py   # Unit tests
└── load_test.py              # Load testing script
```

### Configuration Files
- `requirements.txt`           # Python dependencies
- `template.yaml`             # AWS SAM template
- `Dockerfile`                # Container configuration
- `.dockerignore`             # Docker ignore rules
- `.gitignore`                # Git ignore rules
- `samconfig.toml`            # SAM configuration
- `Makefile`                  # Build commands

### Deployment Scripts
- `deploy.sh`                 # AWS deployment script
- `run_local.sh`              # Local run script

### Documentation
- `README.md`                 # Main documentation
- `ARCHITECTURE.md`           # System architecture
- `QUICKSTART.md`             # Quick start guide

### Examples
- `example_client.py`         # Example API client

---

## 🗑️ Removed Files

The following temporary/helper files have been removed:
- AUTO_SETUP_STATUS.md
- AWS_SETUP_HELPER.md
- DEPLOYMENT_GUIDE.md
- DEPLOYMENT_SUCCESS.md
- HOW_TO_RUN_COMMANDS.md
- PUSH_TO_GITHUB.md
- QUICK_CHECKLIST.md
- RUN_LOCAL.md
- SETUP_GUIDE.md
- SIMPLE_GUIDE.txt
- SUCCESS.md
- RUN_EXAMPLE.bat
- TEST_API.bat
- test_setup.py
- local_data/ (user data, now in .gitignore)

---

## ✅ Final Clean Structure

The repository now contains only:
- ✅ Core application code
- ✅ Essential configuration files
- ✅ Main documentation (README, ARCHITECTURE, QUICKSTART)
- ✅ Tests and examples
- ✅ Deployment scripts

All temporary helper files and local data have been removed!

