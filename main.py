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
        
        # Start the bot
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "event loop is already running" in str(e):
            loop = asyncio.get_event_loop()
            loop.create_task(main())
            loop.run_forever()
        else:
            raise
