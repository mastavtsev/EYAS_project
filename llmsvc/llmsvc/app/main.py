import logging
import os
import asyncio

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from yandex_cloud_ml_sdk import YCloudML

from report_client import AuthenticatedClient
from report_client.api.default import update_report_api_v1_report_service_report_id_put, \
    update_service_status_api_v1_report_service_report_id_service_status_post, \
    get_report_api_v1_report_report_id_get
from report_client.models import ReportServiceStatusInDto, ReportStatusType, ReportUpdateInDto
from whitebox.auth import create_service_token, CurrentServiceData
from whitebox.service import Service
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
    messages = [
        {
            "role": "system",
            "text": "Ты ИИ ассистент врача офтальмолога",
        },
        {
            "role": "user",
            "text": prompt,
        },
    ]

    sdk = YCloudML(
        folder_id="b1goe5po366bkpcovo87",
        auth="AQVNxWV2RLIrfOA-C3QDnI_yZdPCD492XCy4E3Ej",
    )

    result = await asyncio.to_thread(
        lambda: sdk.models.completions("yandexgpt").configure(temperature=temperature).run(messages)
    )

    return result.text


@app.post("/api/v1/generation", response_model=TextGenerationOutDTO)
async def generation(
        current_service: CurrentServiceData,
        in_dto: TextInDTO
):
    """
    Generates textual fundus description based on estimated parameters.
    """
    logging.info(f"Process service={current_service.id}")

    prompt_lines = []
    for param_name in in_dto.params:
        prompt_lines.append(f"{param_name}: {in_dto.params[param_name]}")
    prompt = "Сгенерируй текст обследования, используя следующие параметры:\n" + "\n".join(prompt_lines)

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


@app.post("/api/v1/correct", response_model=TextGenerationOutDTO)
async def correct(
        current_service: CurrentServiceData,
        in_dto: TextCorrectInDTO
):
    """
    Corrects given parameters in the existing text
    """
    logging.info(f"Process service={current_service.id}")

    prompt_lines = []
    for param_name in in_dto.params:
        prompt_lines.append(f"{param_name}: {in_dto.params[param_name]}")
    prompt = f"Замени информацию в данном тексте : \n {in_dto.text} \n используя следующие параметры:\n" + "\n".join(
        prompt_lines)

    generated_text = await call_llm(prompt)

    update_report_api_v1_report_service_report_id_put.sync(
        client=report_client,
        report_id=in_dto.report_id,
        body=ReportUpdateInDto(
            title=None,
            text=generated_text
        )
    )

    return TextGenerationOutDTO(success=True)


@app.post("/api/v1/paraphrasing", response_model=TextGenerationOutDTO)
async def paraphrasing(
        current_service: CurrentServiceData,
        in_dto: TextInDTO
):
    """
    Paraphrases existing textual fundus description.
    """
    """
        Corrects given parameters in the existing text
        """
    logging.info(f"Process service={current_service.id}")

    prompt_lines = []
    for param_name in in_dto.params:
        prompt_lines.append(f"{param_name}: {in_dto.params[param_name]}")
    prompt = f"Перефразируй текстовое описание : \n {in_dto.text} \n используя следующие параметры:\n" + "\n".join(
        prompt_lines)

    generated_text = await call_llm(prompt)

    update_report_api_v1_report_service_report_id_put.sync(
        client=report_client,
        report_id=in_dto.report_id,
        body=ReportUpdateInDto(
            title=None,
            text=generated_text
        )
    )

    return TextGenerationOutDTO(success=True)
