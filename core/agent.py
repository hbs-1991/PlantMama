"""PlantCare Agent implementation."""

import logging
from typing import Optional

from agents import Agent, RunConfig, ToolResult
from openai import AsyncOpenAI

from config.settings import settings
from tools.plant_diagnosis import diagnose_plant_photo, identify_plant_species
from tools.care_recommendations import (
    generate_care_instructions,
    recommend_fertilizers,
    recommend_tools,
)
from tools.user_management import (
    save_user_session,
    get_user_plant_history,
    schedule_reminder,
)

logger = logging.getLogger(__name__)


class PlantCareAgent:
    """Main PlantCare AI Agent."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the PlantCare Agent.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default from settings)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # System prompt
        self.system_prompt = ("Ты — PlantMama AI, эксперт-ботаник и специалист по уходу за растениями."
                              "Ты помогаешь пользователям выявлять проблемы с растениями, определять виды и давать персональные советы по уходу."
                              "Твои ответы должны быть:"
                              "* Дружелюбными и поддерживающими"
                              "* Научно точными"
                              "* Практичными и легко выполнимыми"
                              "* Адаптированными под уровень опыта пользователя"
                              "При анализе фото растений отвечай подробно, но кратко. "
                              "Всегда давай чёткие и конкретные рекомендации по дальнейшим действиям.")

* Дружелюбными и поддерживающими
* Научно точными
* Практичными и легко выполнимыми
* Адаптированными под уровень опыта пользователя

При анализе фото растений отвечай подробно, но кратко. Всегда давай чёткие и конкретные рекомендации по дальнейшим действиям.
"""
        
        # Initialize agent with tools
        self.agent = Agent(
            name="PlantCare Agent",
            instructions=self.system_prompt,
            tools=[
                diagnose_plant_photo,
                identify_plant_species,
                generate_care_instructions,
                recommend_fertilizers,
                recommend_tools,
                save_user_session,
                get_user_plant_history,
                schedule_reminder,
            ],
        )
        
        logger.info("PlantCare Agent initialized successfully")
    
    async def process_message(
        self,
        message: str,
        user_id: str,
        image_data: Optional[bytes] = None,
        context: Optional[dict] = None,
    ) -> str:
        """
        Process a user message and return agent response.
        
        Args:
            message: User's text message
            user_id: Unique user identifier
            image_data: Optional image data for plant analysis
            context: Optional context data
            
        Returns:
            Agent's response text
        """
        try:
            # Prepare run configuration
            run_config = RunConfig(
                max_turns=5,
                tools_choice="auto",
            )
            
            # Prepare context
            full_context = {
                "user_id": user_id,
                "has_image": image_data is not None,
                **(context or {}),
            }
            
            # Run the agent
            logger.info(f"Processing message from user {user_id}")
            
            # If there's an image, we need to handle it specially
            if image_data:
                # For now, we'll add image handling in the message
                message = f"{message}\n\n[User has uploaded an image for analysis]"
            
            response = await self.agent.run(
                messages=[{"role": "user", "content": message}],
                config=run_config,
                context=full_context,
            )
            
            # Extract the final message
            final_message = response.messages[-1].content if response.messages else ("Извините, я не смог обработать ваш запрос."
                                                                                     "Пожалуйста, попробуйте ещё раз — например, отправьте фото растения или уточните, "
                                                                                     "в чём нужна помощь. Я здесь, чтобы помочь! 🌿.")
            
            logger.info(f"Successfully processed message for user {user_id}")
            return final_message
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return "I'm sorry, I encountered an error processing your request. Please try again."
    
    async def analyze_plant_image(
        self,
        image_data: bytes,
        user_id: str,
        additional_info: Optional[str] = None,
    ) -> str:
        """
        Analyze a plant image and provide diagnosis.
        
        Args:
            image_data: Image bytes
            user_id: User identifier
            additional_info: Optional additional context
            
        Returns:
            Analysis results
        """
        message = "Please analyze this plant image and provide a diagnosis."
        if additional_info:
            message += f"\n\nAdditional information: {additional_info}"
        
        return await self.process_message(
            message=message,
            user_id=user_id,
            image_data=image_data,
        )
