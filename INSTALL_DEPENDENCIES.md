# Dependencies Installation Instructions

## Activate Virtual Environment

Before installing dependencies, make sure you have activated the virtual environment:

```bash
# On Windows
.venv\Scripts\activate

# On Unix/macOS
source .venv/bin/activate
```

## Install All Dependencies

To install all project dependencies, run:

```bash
pip install -r requirements.txt
```

## Install Individual Dependencies (if needed)

If you want to install dependencies step by step:

```bash
# Core dependencies
pip install openai-agents>=0.0.15
pip install python-telegram-bot>=20.0
pip install Pillow>=10.0.0
pip install SQLAlchemy>=2.0.0
pip install python-dotenv>=1.0.0
pip install pydantic>=2.0.0
pip install asyncio-mqtt>=0.16.0

# Database tools
pip install alembic>=1.13.0
pip install asyncpg>=0.29.0
pip install psycopg2-binary>=2.9.0

# Development tools (optional)
pip install black flake8 mypy pytest pytest-asyncio pytest-cov
```

## Verify Installation

After installation, verify that core packages are installed:

```bash
python -c "import agents; print('openai-agents installed successfully')"
python -c "import telegram; print('python-telegram-bot installed successfully')"
python -c "import PIL; print('Pillow installed successfully')"
python -c "import sqlalchemy; print('SQLAlchemy installed successfully')"
```

## Freeze Dependencies

To freeze the current dependencies with exact versions:

```bash
pip freeze > requirements.lock
```

## Troubleshooting

1. **openai-agents not found**: The package might not be on PyPI yet. You may need to install from source:
   ```bash
   pip install git+https://github.com/openai/openai-agents-python.git
   ```

2. **PostgreSQL dependencies fail**: On Windows, you might need to install PostgreSQL client libraries first.

3. **Permission errors**: Make sure you're in the activated virtual environment.

## Next Steps

After installing dependencies:
1. Create `.env` file from `.env.example`
2. Configure your API keys
3. Set up the database connection
4. Run the application
