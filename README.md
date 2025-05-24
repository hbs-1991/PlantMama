# 🌱 PlantMama AI Bot

An intelligent AI assistant for plant care, powered by OpenAI agents SDK and integrated with Telegram.

## 🎯 Features

- **Plant Disease Diagnosis**: Analyze plant photos to detect diseases, pests, and nutrient deficiencies
- **Personalized Care Recommendations**: Get tailored advice based on your plant type, season, and location
- **Species Identification**: Identify unknown plants from photos
- **Care Reminders**: Set up watering, fertilizing, and pruning schedules
- **Expert Knowledge Base**: Access comprehensive plant care information
- **Telegram Integration**: Easy-to-use interface through Telegram bot

## 🛠 Tech Stack

- **Python 3.11+**: Core programming language
- **OpenAI Agents SDK**: AI agent framework
- **Telegram Bot API**: User interface
- **SQLAlchemy**: Database ORM
- **PostgreSQL**: Data persistence
- **Pillow**: Image processing
- **Docker**: Containerization

## 📁 Project Structure

```
plantcare_agent/
├── core/           # Core agent logic
├── tools/          # Agent tools for plant care
├── handlers/       # Telegram bot handlers
├── database/       # Database models and migrations
├── services/       # Business logic services
├── utils/          # Utility functions
├── config/         # Configuration management
└── tests/          # Test suite
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- Telegram Bot Token (from @BotFather)
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PlantMamaAIBot
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix/macOS
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the bot:
```bash
python -m plantcare_agent.main
```

## 🔧 Configuration

Create a `.env` file with the following variables:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/plantcare

# Application
LOG_LEVEL=INFO
DEBUG=False
```

## 📊 Usage

1. Start a conversation with your bot on Telegram
2. Send `/start` to register
3. Send a photo of your plant for diagnosis
4. Ask questions about plant care
5. Set up care reminders

### Available Commands

- `/start` - Start the bot and register
- `/help` - Show available commands
- `/my_plants` - View your registered plants
- `/add_plant` - Add a new plant
- `/reminders` - Manage care reminders

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

For coverage report:

```bash
pytest --cov=plantcare_agent tests/
```

## 🐳 Docker Deployment

Build and run with Docker:

```bash
docker-compose up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- OpenAI for the amazing agents SDK
- Telegram for the bot platform
- All contributors and testers

---

For more detailed documentation, see the [To-Do List](To-Do_List.md) and project documentation.
