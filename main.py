import logging
import asyncio
from config.settings import settings
from core.agent import PlantCareAgent
from handlers.telegram_handler import TelegramBot
from utils.logging_config import setup_logging


def main() -> None:
    """Start the PlantCare Agent application."""
    setup_logging(settings.LOG_LEVEL)
    logger = logging.getLogger(__name__)

    logger.info("Starting PlantCare Agent...")

    try:
        # Initialize agent
        agent = PlantCareAgent()

        # Initialize Telegram bot
        bot = TelegramBot(agent)

        # Run blocking polling
        bot.run()

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()


# Extend TelegramBot with run() method for blocking polling
setattr(TelegramBot, "run", lambda self: asyncio.run(self._run_polling()))

# Define the internal async method _run_polling
async def _run_polling(self):
    from telegram.ext import Application
    self.application = Application.builder().token(self.token).build()
    self._register_handlers()
    await self._set_bot_commands()
    await self.application.run_polling()

setattr(TelegramBot, "_run_polling", _run_polling)
