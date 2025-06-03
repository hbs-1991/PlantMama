"""Telegram bot handler."""

import logging
import io
from typing import Optional
import speech_recognition as sr

from telegram import (
    Update, 
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config.settings import settings
from core.agent import PlantCareAgent
from services.image_processing import ImageProcessor

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
        await self.application.run_polling()

        
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
        
        # Voice message handler
        self.application.add_handler(
            MessageHandler(filters.VOICE, self.handle_voice)
        )
        
        # Callback query handler for inline keyboards
        self.application.add_handler(
            CallbackQueryHandler(self.handle_callback_query)
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
        await update.message.reply_text(
            welcome_message,
            reply_markup=self._get_main_keyboard()
        )
    
    async def handle_help(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /help command."""
        help_text = """
📚 **PlantMama AI — Справка**

**Команды:**
/start — Запустить бота
/help — Показать это сообщение
/my\_plants — Просмотреть зарегистрированные растения

**Как пользоваться:**
• 📸 Отправьте фото, чтобы получить диагноз растения
• 💬 Задайте любой вопрос по уходу за растениями
• 🌱 Расскажите о проблемах с вашим растением

**Примеры:**
• «Почему у моей монстеры желтеют листья?»
• «Как часто поливать суккуленты?»
• «Какое удобрение лучше для орхидей?»

**Советы:**
• Для лучшего результата присылайте чёткие фото при хорошем освещении
• Указывайте детали об окружающей среде растения
• Не стесняйтесь задавать уточняющие вопросы!
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

    async def handle_voice(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle voice messages."""
        user_id = str(update.effective_user.id)

        try:
            # Send typing indicator
            await update.message.chat.send_action("typing")

            # Download voice file
            voice_file = await update.message.voice.get_file()
            voice_bytes = await voice_file.download_as_bytearray()

            # Convert voice to text (placeholder - in production use OpenAI Whisper)
            text = "Извините, обработка голосовых сообщений временно недоступна. Пожалуйста, отправьте текстовое сообщение или фото растения."

            # For now, inform user about the limitation
            await update.message.reply_text(
                "🎤 Голосовое сообщение получено.\n\n" + text
            )

        except Exception as e:
            logger.error(f"Error processing voice message: {e}")
            await update.message.reply_text(
                "Произошла ошибка при обработке голосового сообщения. Попробуйте еще раз."
            )

    def _get_main_keyboard(self) -> InlineKeyboardMarkup:
        """Get main inline keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("📸 Диагностика по фото", callback_data="action_photo"),
                InlineKeyboardButton("🌿 Мои растения", callback_data="action_my_plants")
            ],
            [
                InlineKeyboardButton("💡 Совет дня", callback_data="action_tip"),
                InlineKeyboardButton("📚 Энциклопедия", callback_data="action_encyclopedia")
            ],
            [
                InlineKeyboardButton("⏰ Напоминания", callback_data="action_reminders"),
                InlineKeyboardButton("❓ Помощь", callback_data="action_help")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def handle_callback_query(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle callback queries from inline keyboards."""
        query = update.callback_query
        user_id = str(query.from_user.id)
        
        # Answer callback query to remove loading state
        await query.answer()
        
        # Handle different actions
        if query.data == "action_photo":
            await query.edit_message_text(
                "📸 Отправьте фото вашего растения, и я проведу диагностику!\n\n"
                "Для лучшего результата:\n"
                "• Фотографируйте при хорошем освещении\n"
                "• Покажите проблемные участки крупным планом\n"
                "• Можете добавить описание в подписи к фото"
            )
        
        elif query.data == "action_my_plants":
            response = await self.agent.process_message(
                message="Покажи мои растения",
                user_id=user_id,
            )
            await query.edit_message_text(response)
        
        elif query.data == "action_tip":
            response = await self.agent.process_message(
                message="Дай совет по уходу за растениями на сегодня",
                user_id=user_id,
            )
            await query.edit_message_text(
                f"💡 **Совет дня**\n\n{response}",
                parse_mode="Markdown"
            )
        
        elif query.data == "action_encyclopedia":
            await query.edit_message_text(
                "📚 **Энциклопедия растений**\n\n"
                "Напишите название растения, и я расскажу о нем всё:\n"
                "• Научная классификация\n"
                "• Условия содержания\n"
                "• Особенности ухода\n\n"
                "Например: _Монстера_, _Фикус_, _Орхидея_",
                parse_mode="Markdown"
            )
        
        elif query.data == "action_reminders":
            await query.edit_message_text(
                "⏰ **Управление напоминаниями**\n\n"
                "Я могу напоминать вам о:\n"
                "• Поливе растений\n"
                "• Подкормке\n"
                "• Пересадке\n"
                "• Обработке от вредителей\n\n"
                "Чтобы создать напоминание, напишите, например:\n"
                "_Напомни полить монстеру через 3 дня_",
                parse_mode="Markdown"
            )
        
        elif query.data == "action_help":
            help_text = self._get_help_text()
            await query.edit_message_text(help_text, parse_mode="Markdown")
        
        # Plant-specific actions
        elif query.data.startswith("plant_"):
            action = query.data.split("_")[1]
            plant_id = query.data.split("_")[2]
            
            if action == "water":
                response = await self.agent.process_message(
                    message=f"Запланируй полив для растения {plant_id}",
                    user_id=user_id,
                )
                await query.edit_message_text(response)
            
            elif action == "diagnose":
                await query.edit_message_text(
                    f"Отправьте фото растения #{plant_id} для диагностики"
                )
    
    def _get_help_text(self) -> str:
        """Get help text."""
        return """
📚 **PlantMama AI — Справка**

**Команды:**
/start — Начать работу с ботом
/help — Показать эту справку
/my\_plants — Мои растения

**Возможности:**
• 📸 Диагностика по фото
• 🔍 Определение вида растения
• 💚 Персональные советы по уходу
• 📅 Напоминания о поливе
• 📚 База знаний о растениях

**Как пользоваться:**
1. Отправьте фото растения для диагностики
2. Задайте вопрос об уходе
3. Получите рекомендации

**Примеры вопросов:**
• "Почему желтеют листья?"
• "Как часто поливать фикус?"
• "Что за пятна на листьях?"

💡 *Совет*: Для точной диагностики отправляйте четкие фото при хорошем освещении!
        """
    
    async def handle_photo(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle photo messages."""
        user_id = str(update.effective_user.id)
        
        try:
            # Send typing indicator
            await update.message.chat.send_action("typing")
            
            # Get the largest photo
            photo_file = await update.message.photo[-1].get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            
            # Validate image
            processor = ImageProcessor()
            is_valid, error_msg = await processor.validate_plant_image(bytes(photo_bytes))
            
            if not is_valid:
                await update.message.reply_text(
                    f"❌ Не удалось обработать изображение:\n{error_msg}\n\n"
                    "Пожалуйста, убедитесь, что:\n"
                    "• На фото есть растение\n"
                    "• Изображение четкое и не слишком темное\n"
                    "• Размер файла не превышает 10MB"
                )
                return
            
            # Process image
            processed_image, metadata = await processor.process_image(bytes(photo_bytes))
            
            # Save image for user
            image_path = await processor.save_image(
                processed_image,
                user_id=user_id
            )
            
            # Get caption if any
            caption = update.message.caption or ""
            
            # Notify about processing
            await update.message.reply_text(
                "🔍 Анализирую фотографию...\n"
                "Это может занять несколько секунд."
            )
            
            # Process with agent
            response = await self.agent.analyze_plant_image(
                image_data=processed_image,
                user_id=user_id,
                additional_info=caption,
            )
            
            # Send response with action buttons
            plant_keyboard = [
                [
                    InlineKeyboardButton("💧 График полива", callback_data="plant_water_new"),
                    InlineKeyboardButton("📊 Сохранить диагноз", callback_data="plant_save_new")
                ],
                [
                    InlineKeyboardButton("🔄 Новое фото", callback_data="action_photo"),
                    InlineKeyboardButton("📚 Главное меню", callback_data="action_menu")
                ]
            ]
            
            await update.message.reply_text(
                response,
                reply_markup=InlineKeyboardMarkup(plant_keyboard),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error handling photo: {e}", exc_info=True)
            await update.message.reply_text(
                "😔 Произошла ошибка при обработке фотографии.\n"
                "Пожалуйста, попробуйте еще раз или обратитесь в поддержку."
            )
    
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
