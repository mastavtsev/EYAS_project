import logging
import os
import asyncio

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from jinja2 import Environment, Template
from yandex_cloud_ml_sdk import YCloudML
from typing import Dict, Any
from openai import OpenAI

from report_client import AuthenticatedClient
from report_client.api.default import update_report_api_v1_report_service_report_id_put, \
    update_service_status_api_v1_report_service_report_id_service_status_post, \
    get_report_api_v1_report_report_id_get
from report_client.models import ReportServiceStatusInDto, ReportStatusType, ReportUpdateInDto
from whitebox.auth import create_service_token, CurrentServiceData
from whitebox.service import Service
from names_lib.names import KEY_MAPPING, VALUE_MAPPING
from .dtos import TextInDTO, TextGenerationOutDTO, TextCorrectInDTO
from model_lib.utils import logger

app = FastAPI(title='llm')
if os.environ.get("DISABLE_CORS"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

report_client = AuthenticatedClient(
    os.environ.get("REPORT_SERVICE_URL"),
    create_service_token(Service.LLM)
)

async def call_llm(prompt: str, temperature: float = 0.5) -> str:
    """
    Uses OpenAI API to call LLM with specified prompt.
    """

    chat_template = r"""
    {%- for message in messages %}
        {%- if message['role'] == 'system' %}
    Система: {{ message['content'] }}

        {%- elif message['role'] == 'user' %}
    Пользователь: {{ message['content'] }}

        {%- endif %}
    {%- endfor %}
    Ассистент:[SEP]
    """

    # Ваши промты
    DEFAULT_SYSTEM_PROMPT = (
        "Ты — русскоязычный автоматический ассистент офтальмолога. "
        "Ты создаешь текстовые описания глазного дна по его параметрам."
    )

    USER_PROMPT = prompt

    # Список сообщений
    messages = [
        {'role': 'system', 'content': DEFAULT_SYSTEM_PROMPT},
        {'role': 'user', 'content': USER_PROMPT},
    ]

    # Рендеринг шаблона
    env = Environment(trim_blocks=True, lstrip_blocks=True)
    template = env.from_string(chat_template)
    prompt = template.render(messages=messages)

    client = OpenAI(base_url="https://du761p-94-29-24-84.ru.tuna.am/v1", api_key="lm-studio")

    completion = client.completions.create(
        model="yandexgpt-5-lite-8b-instruct",
        prompt=prompt,
        max_tokens=256,
        temperature=0.7,
    )

    return completion.choices[0].text

    # messages = [
    #     {
    #         "role": "system",
    #         "text": "Ты ИИ ассистент врача офтальмолога",
    #     },
    #     {
    #         "role": "user",
    #         "text": prompt,
    #     },
    # ]
    #
    # sdk = YCloudML(
    #     folder_id="b1goe5po366bkpcovo87",
    #     auth="AQVNxWV2RLIrfOA-C3QDnI_yZdPCD492XCy4E3Ej",
    # )
    #
    # result = await asyncio.to_thread(
    #     lambda: sdk.models.completions("yandexgpt").configure(temperature=temperature).run(messages)
    # )
    #
    # return result.text


async def get_json_prompt(params: Dict[str, Any]) -> str:
    json_text = f"""
        {{
        "ДЗН": {{
            "{KEY_MAPPING["od_color"]}": "{VALUE_MAPPING[params["od_color"]]}",
            "{KEY_MAPPING["od_monotone"]}": "{VALUE_MAPPING[params["od_monotone"]]}",
            "{KEY_MAPPING["od_size"]}": "{VALUE_MAPPING[params["od_size"]]}",
            "{KEY_MAPPING["od_shape"]}": "{VALUE_MAPPING[params["od_shape"]]}",
            "{KEY_MAPPING["od_border"]}": "{VALUE_MAPPING[params["od_border"]]}",
            "Экскавация": {{
                "{KEY_MAPPING["od_excavation_size"]}": {VALUE_MAPPING[params["od_excavation_size"]]},
                "{KEY_MAPPING["od_excavation_location"]}": {VALUE_MAPPING[params["od_excavation_location"]]}
            }},
            "{KEY_MAPPING["od_excavation_ratio"]}": {params["od_excavation_ratio"]},
            "{KEY_MAPPING["od_vessels_location"]}": {VALUE_MAPPING[params["od_vessels_location"]]},
        }},
        "Сосуды": {{
            "Артерии": {{
                "{KEY_MAPPING["vessels_art_course"]}": {VALUE_MAPPING[params["vessels_art_course"]]},
                "{KEY_MAPPING["vessels_art_turtuosity"]}": {VALUE_MAPPING[params["vessels_art_turtuosity"]]},
                "{KEY_MAPPING["vessels_art_bifurcation"]}": {VALUE_MAPPING[params["vessels_art_bifurcation"]]},
                "{KEY_MAPPING["vessels_art_caliber"]}": {VALUE_MAPPING[params["vessels_art_caliber"]]}
            }},
            "Вены": {{
                "{KEY_MAPPING["vessels_vein_course"]}": {VALUE_MAPPING[params["vessels_vein_course"]]},
                "{KEY_MAPPING["vessels_vein_turtuosity"]}": {VALUE_MAPPING[params["vessels_vein_turtuosity"]]},
                "{KEY_MAPPING["vessels_vein_bifurcation"]}": {VALUE_MAPPING[params["vessels_vein_bifurcation"]]},
                "{KEY_MAPPING["vessels_vein_caliber"]}": {VALUE_MAPPING[params["vessels_vein_caliber"]]}
            }},
            "{KEY_MAPPING["vessels_ratio"]}": {params["vessels_ratio"]},
        }},
        "Макула": {{
            "{KEY_MAPPING["macula_macular_reflex"]}": {VALUE_MAPPING[params["macula_macular_reflex"]]},
            "{KEY_MAPPING["macula_foveal_reflex"]}": {VALUE_MAPPING[params["macula_foveal_reflex"]]},
        }},
        }}
        """

    return json_text

    # fundus_params_lines = []
    # for key in category_mapping:
    #     fundus_params_lines.append(f"{key}:")
    #     for param in category_mapping[key]:
    #         if param in params:
    #             param_translated = VALUE_MAPPING[param]
    #
    #             value = params[param]
    #             value_translated = VALUE_MAPPING[value] if value in VALUE_MAPPING else value
    #
    #             fundus_params_lines.append(f"{param_translated} : {value_translated}")
    #     fundus_params_lines.append("\n")
    #
    # fundus_params = "\n".join(fundus_params_lines)
    #
    # return fundus_params


async def create_generation_prompt(params: Dict[str, Any]) -> str:
    json_text = await get_json_prompt(params)

    prompt_tmp = f"""**Задача:**
    На основе приведённого JSON-документа, содержащего описание глазного дна, сгенерируй полное текстовое описание, придерживаясь стилистики и формата примера.

    **Формат:**
    - Описание должно быть текстовым, структурированным и последовательным, как в приведённом примере.
    - Допускается совместное описание артерий и вен, если у них одинаковые параметры (Пример 1). Если параметры разные, их необходимо описывать отдельно (Пример 2).

    **Данные:**
    JSON-документ:
    {json_text}

    **Пример 1:**

    ДЗН серый, границы четкие, форма правильная, размер нормальный. Экскавация нормальная, в центре. Сосудистый пучок расположен центрально.  
    Артерии и Вены имеют нормальный ход, нормальную извитость, бифуркация в норме и калибр нормальный.  
    Макулярный рефлекс отсутствует, фовеальный рефлекс нормальный.

    **Пример 2:**

    ДЗН серый, границы четкие, форма правильная, размер нормальный. Экскавация нормальная, в центре. Сосудистый пучок расположен центрально.  
    Артерии: ход смещён наружу, извитость нормальная, бифуркация под острым углом, калибр нормальный.
    Вены: ход нормальный, извитость нормальная, бифуркация нормальная, калибр суженный.
    Макулярный рефлекс отсутствует, фовеальный рефлекс нормальный.

    **Твоя задача:**  
    Создай полное текстовое описание глазного дна по JSON-документу, следуй телеграфному стилю и примеру выше.
    """

    return prompt_tmp


@app.post("/api/v1/generation", response_model=TextGenerationOutDTO)
async def generation(
        current_service: CurrentServiceData,
        in_dto: TextInDTO
):
    """
    Generates textual fundus description based on estimated parameters.
    """
    logger.info(f"Process service={current_service.id}")

    prompt = await create_generation_prompt(in_dto.params)

    # logger.info(f"Generation PROMPT: {prompt}")

    generated_text = await call_llm(prompt)

    # TODO Разобраться с тем, почему тут и в других svc синхронный вызов
    update_report_api_v1_report_service_report_id_put.sync(
        client=report_client,
        report_id=in_dto.report_id,
        body=ReportUpdateInDto(
            title=None,
            text=generated_text
        )
    )

    update_service_status_api_v1_report_service_report_id_service_status_post.sync(
        client=report_client,
        body=ReportServiceStatusInDto(
            status=ReportStatusType.GENERATION
        ),
        report_id=in_dto.report_id,
    )

    return TextGenerationOutDTO(success=True)


async def create_correction_prompt(old_text: str, new_params: Dict[str, Any]) -> str:
    fundus_params = await get_json_prompt(new_params)

    prompt = f"""Задача:
    В существующем тексте, не изменяя его подправь только некоторые значения параметров согласно списку для замены.
    
    Требования к формату:
    - Описание должно быть структурированным, естественным и последовательным.
    - Итоговый текст должен быть в телеграфном стиле, без лишних слов, но с медицинской терминологией.
    - Ответ должен содержат только текстовое описание глазного дна. Нельзя вставлять вводные конструкции.
    - Не надо форматировать элементы текста, например, делать их жирным шрифтом.

    Список для замены параметров:
    {fundus_params}
    Текущий текст, в котором надо заменить параметры:
    {old_text}
    
    
    Пример выполнения задачи:
    
    Список для замены параметров:
    Цвет: Розовый
    Монотонность: Неравномерная
    Размер: Больше нормы
    Форма: Правильная
    Границы: Четкие
    
    Экскавация:
    Размер: Нормальный
    Сектор: В центре
    
    Сосудистый пучок: Центральное
    
    Сосуды:
    
    Артерии:
    Ход: Нормальный
    Извитость: Нормальная
    Бифуркация: Нормальная
    Калибр: Нормальный
    
    Вены:
    Ход: Нормальный
    Извитость: Нормальная
    Бифуркация: Нормальная
    Калибр: Нормальный
    
    Макула:
    Макулярный рефлекс: Нормальный
    Фовеальный рефлекс: Нормальный
    
    Периферия:
    Патология: Не выявлена
    
    Текущий текст, в котором надо заменить параметры:
    ДЗН серого цвета с чёткими границами, правильной формы, нормального размера. Сосудистый пучок расположен центрально. Ход артерий извитой, калибр и бифуркация нормальные. Вены имеют нормальный ход, извитость и бифуркацию, калибр нормальный. Макулярный рефлекс отсутствует, фовеальный рефлекс нормальный. Патологии на периферии не выявлены.

    Итоговый ответ:
    ДЗН розового цвета с чёткими границами, форма больше нормы, нормального размера. Сосудистый пучок расположен центрально. Ход артерий извитой, калибр и бифуркация нормальные. Вены имеют нормальный ход, извитость и бифуркацию, калибр нормальный. Макулярный рефлекс сохранён, фовеальный рефлекс снижен. Патология макулы: отёк. Патология на периферии: дегенерация.
    """

    return prompt


@app.post("/api/v1/correct", response_model=TextGenerationOutDTO)
async def correct(
        current_service: CurrentServiceData,
        in_dto: TextCorrectInDTO
):
    """
    Corrects given parameters in the existing text
    """
    logger.info(f"Process service={current_service.id}")

    prompt = await create_correction_prompt(in_dto.text, in_dto.params)

    # logger.info(f"PROMPT: {prompt}")

    generated_text = await call_llm(prompt)

    update_report_api_v1_report_service_report_id_put.sync(
        client=report_client,
        report_id=in_dto.report_id,
        body=ReportUpdateInDto(
            title=None,
            text=generated_text
        )
    )

    update_service_status_api_v1_report_service_report_id_service_status_post.sync(
        client=report_client,
        body=ReportServiceStatusInDto(
            status=ReportStatusType.GENERATION
        ),
        report_id=in_dto.report_id,
    )

    return TextGenerationOutDTO(success=True)


@app.post("/api/v1/paraphrasing", response_model=TextGenerationOutDTO)
async def paraphrasing(
        current_service: CurrentServiceData,
        in_dto: TextCorrectInDTO
):
    """
    Paraphrases existing textual fundus description.
    """

    logging.info(f"Process service={current_service.id}")


    prompt = f"Перефразируй текстовое описание : \n {in_dto.text}"

    generated_text = await call_llm(prompt)

    update_report_api_v1_report_service_report_id_put.sync(
        client=report_client,
        report_id=in_dto.report_id,
        body=ReportUpdateInDto(
            title=None,
            text=generated_text
        )
    )

    update_service_status_api_v1_report_service_report_id_service_status_post.sync(
        client=report_client,
        body=ReportServiceStatusInDto(
            status=ReportStatusType.GENERATION
        ),
        report_id=in_dto.report_id,
    )

    return TextGenerationOutDTO(success=True)
