import logging
from typing import Optional

from agents import Agent, RunConfig
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
        image_data: Optional[bytes] = None,
    ) -> str:
        """
        Основной метод: принимает ID пользователя, текстовое сообщение и (опционально) raw-данные изображения.
        Возвращает ответ агента (текст).
        """
        try:
            # Добавляем в контекст информацию о юзере
            context = {"user_id": user_id}

            # Если пользователь отправляет изображение, добавим флаг
            if image_data:
                context["has_image"] = True
                # Концентрируемся на том, что текстовое поле message останется пустым,
                # а агент поймёт, что есть картинка.
                user_message = "[ПОЛЬЗОВАТЕЛЬ ЗАГРУЗИЛ ИЗОБРАЖЕНИЕ]"
                # Передадим картинку как дополнительный аргумент
                response = await self.agent.run(
                    inputs=user_message,
                    context={"user_id": user_id, "image": image_data},
                    run_config=RunConfig(max_function_calls=3),
                )
            else:
                context["has_image"] = False
                response = await self.agent.run(
                    inputs=message,
                    context=context,
                    run_config=RunConfig(max_function_calls=3),
                )

            # Обычно .run возвращает объект с атрибутом .output — конечным текстовым ответом агента.
            # Если вдруг .output отсутствует, попытаемся читать из .messages[-1].content
            if hasattr(response, "output"):
                return response.output
            elif hasattr(response, "messages") and response.messages:
                return response.messages[-1].content
            else:
                return "Извините, я не смог обработать ваш запрос."

        except Exception as e:
            logger.error(f"Ошибка в process_message: {e}", exc_info=True)
            return "Извините, произошла внутренняя ошибка при обработке вашего запроса. Попробуйте ещё раз."

    
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
