"""Telegram bot handler."""

import logging
from typing import Optional

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config.settings import settings
from core.agent import PlantCareAgent

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot handler for PlantCare Agent."""
    
    def __init__(self, agent: PlantCareAgent):
        """
        Initialize Telegram bot.
        
        Args:
            agent: PlantCare agent instance
        """
        self.agent = agent
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.application: Optional[Application] = None
        
    async def start(self) -> None:
        """Start the Telegram bot."""
        # Create application
        self.application = Application.builder().token(self.token).build()
        
        # Register handlers
        self._register_handlers()
        
        # Set bot commands
        await self._set_bot_commands()
        
        # Start polling
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Telegram bot started successfully")
    
    async def stop(self) -> None:
        """Stop the Telegram bot."""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            
        logger.info("Telegram bot stopped")
    
    def _register_handlers(self) -> None:
        """Register command and message handlers."""
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("help", self.handle_help))
        self.application.add_handler(CommandHandler("my_plants", self.handle_my_plants))
        
        # Photo handler
        self.application.add_handler(
            MessageHandler(filters.PHOTO, self.handle_photo)
        )
        
        # Text message handler
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text)
        )
    
    async def _set_bot_commands(self) -> None:
        """Set bot commands for the menu."""
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help information"),
            BotCommand("my_plants", "View your plants"),
        ]
        await self.application.bot.set_my_commands(commands)
    
    async def handle_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /start command."""
        user = update.effective_user
        welcome_message = f"""
🌱🌱 Добро пожаловать в PlantMama AI, {user.first_name}!

Я — твой персональный помощник по уходу за растениями. Я могу помочь тебе:
• 🔍 Определить болезни растений по фото
• 🌿 Опознать неизвестные растения
• 💚 Дать персональные советы по уходу
• 📅 Настроить напоминания по уходу

Просто отправь мне фото своего растения или задай любой вопрос, связанный с растениями!

Используй /help, чтобы увидеть все доступные команды.
        """
        await update.message.reply_text(welcome_message)
    
    async def handle_help(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /help command."""
        help_text = """
📚 **PlantMama AI Help**

**Commands:**
/start - Start the bot
/help - Show this help message
/my_plants - View your registered plants

**How to use:**
• 📸 Send a photo to get plant diagnosis
• 💬 Ask any plant care question
• 🌱 Tell me about your plant problems

**Examples:**
• "Why are my monstera leaves turning yellow?"
• "How often should I water my succulents?"
• "What fertilizer is best for orchids?"

**Tips:**
• For best results, send clear photos in good lighting
• Include details about your plant's environment
• Feel free to ask follow-up questions!
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def handle_my_plants(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /my_plants command."""
        user_id = str(update.effective_user.id)
        
        # Get user's plants from agent
        response = await self.agent.process_message(
            message="Show me my registered plants",
            user_id=user_id,
        )
        
        await update.message.reply_text(response)
    
    async def handle_photo(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle photo messages."""
        user_id = str(update.effective_user.id)
        
        # Send typing indicator
        await update.message.chat.send_action("typing")
        
        # Get the largest photo
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Get caption if any
        caption = update.message.caption or ""
        
        # Process with agent
        response = await self.agent.analyze_plant_image(
            image_data=bytes(photo_bytes),
            user_id=user_id,
            additional_info=caption,
        )
        
        await update.message.reply_text(response)
    
    async def handle_text(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle text messages."""
        user_id = str(update.effective_user.id)
        message = update.message.text
        
        # Send typing indicator
        await update.message.chat.send_action("typing")
        
        # Process with agent
        response = await self.agent.process_message(
            message=message,
            user_id=user_id,
        )
        
        await update.message.reply_text(response)
