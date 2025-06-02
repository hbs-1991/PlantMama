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
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key)

        # Системное описание бота (на русском)
        self.system_prompt = (
            "Ты — PlantMama AI, виртуальный помощник по уходу за растениями. "
            "Отвечай на все вопросы пользователя на русском языке.\n"
            "1. Если в сообщении есть изображение растения, сначала определи вид с помощью инструмента identify_plant_species, "
            "а затем проведи диагностику с помощью инструмента diagnose_plant_photo.\n"
            "2. Если нужно дать общие рекомендации по уходу, используй инструменты generate_care_instructions, recommend_fertilizers, recommend_tools.\n"
            "3. Если необходимо сохранить или получить историю пользователя, используй save_user_session или get_user_plant_history.\n"
            "4. Если нужно поставить напоминание, используй schedule_reminder.\n"
            "5. В каждом ответе стремись быть максимально понятным и полезным, не выходя за рамки упомянутых инструментов."
        )

        # Регистрируем все доступные инструменты
        tools = [
            diagnose_plant_photo,
            identify_plant_species,
            generate_care_instructions,
            recommend_fertilizers,
            recommend_tools,
            save_user_session,
            get_user_plant_history,
            schedule_reminder,
        ]

        # Создаём агента, передавая в него наш AsyncOpenAI
        self.agent = Agent(
            name="PlantCare Agent",
            llm=self.client,
            instructions=self.system_prompt,
            tools=tools,
        )

    async def process_message(
        self,
        user_id: str,
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
