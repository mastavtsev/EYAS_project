import asyncio
import base64
import logging
import os
from typing import Any, List, Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status as http_status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

import av_client.api.default as av_client_handles
import av_client.api.default.classification_api_v1_classification_post
import av_client.api.default.segmentation_api_v1_segmentation_post
from av_client.models import AvSegmentationInDto
import mac_client.api.default as mac_client_handles
import mac_client.api.default.classification_api_v1_classification_post
import mac_client.api.default.localization_api_v1_localization_post
from mac_client.models import MacLocalizeDto
from model_lib.inference.od.image_preprocessing import \
    transform_square_original_fundus
from model_lib.utils import cv2_to_img_bytes, img_from_base64
from models.report_models import (Report, ReportImage, ReportImageType, ReportParameter,
                                  ReportStatus, ReportStatusType, ReportText)
from od_client import AuthenticatedClient
import od_client.api.default as od_client_handles
import od_client.api.default.classification_api_v1_classification_post
import od_client.api.default.localization_api_v1_localization_post
from od_client.models import OdLocalizeDto
import llm_client.api.default as llm_client_handles
import llm_client.api.default.generation_api_v1_generation_post
import llm_client.api.default.correct_api_v1_correct_post
from llm_client.models import TextInDTO, TextInDTOParams, TextCorrectInDTO
from reportsvc.app.db import get_session
from reportsvc.app.dtos import (ReportDeletedOutDto, ReportDetailedOutDto,
                                ReportOutDto,
                                ReportRequestInDto, ReportServiceStatusInDto,
                                ReportServiceStatusOutDto, ReportUpdateInDto,
                                ReportUploadImageInDto,
                                ReportUploadImageOutDto, ReportTextUpdateInDto, ReportTextUpdateOutDto)
from whitebox.auth import create_service_token, CurrentAuthData, CurrentServiceData
from whitebox.service import ANALYSIS_SERVICES, Service

logger = logging.getLogger("uvicorn")
file_handler = logging.FileHandler('application.log')
logger.addHandler(file_handler)

app = FastAPI(title='report')
if os.environ.get("DISABLE_CORS"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

report_not_found_exception = HTTPException(
    status_code=http_status.HTTP_404_NOT_FOUND, detail="ERR_REPORT_NOT_FOUND",
)

image_not_found_exception = HTTPException(
    status_code=http_status.HTTP_404_NOT_FOUND, detail="ERR_IMAGE_NOT_FOUND",
)

report_access_forbidden_exception = HTTPException(
    status_code=http_status.HTTP_403_FORBIDDEN, detail="ERR_REPORT_FORBIDDEN",
)

od_client = AuthenticatedClient(
    os.environ.get("OD_SERVICE_URL"),
    create_service_token(Service.REPORT)
)
mac_client = AuthenticatedClient(
    os.environ.get("MAC_SERVICE_URL"),
    create_service_token(Service.REPORT)
)
av_client = AuthenticatedClient(
    os.environ.get("AV_SERVICE_URL"),
    create_service_token(Service.REPORT)
)

llm_client = AuthenticatedClient(
    os.environ.get("LLM_SERVICE_URL"),
    create_service_token(Service.REPORT)
)


@app.post("/api/v1/report", response_model=ReportDetailedOutDto)
async def request_report(
        report_in_dto: ReportRequestInDto,
        current_user_data: CurrentAuthData,
        session: AsyncSession = Depends(get_session),
):
    if current_user_data.service:
        raise report_access_forbidden_exception

    source_image_mat = transform_square_original_fundus(
        img_from_base64(
            report_in_dto.source_image
        )
    )

    source_image = cv2_to_img_bytes(source_image_mat)
    source_image_bytes = source_image
    source_image_b64 = base64.b64encode(source_image_bytes)

    report = Report(
        author_id=current_user_data.id,
        title=report_in_dto.title,
        status=ReportStatusType.PENDING.value,
        images=[
            ReportImage(
                image_type=ReportImageType.SOURCE,
                data=source_image_bytes,
            )
        ],
        statuses=[
                     ReportStatus(
                         service_id=service,
                         status=ReportStatusType.PENDING
                     )
                     for service in ANALYSIS_SERVICES
                 ] + [
                     ReportStatus(
                         service_id=-6,
                         status=ReportStatusType.PENDING
                     )
                 ],
        params=[
            ReportParameter(
                name=name,
                type="string",
                data={"value": ""},
                version=0,
            )
            for name in [
                "peripheral_pathology",
                "other_diagnosis",
                "other_notes",
            ]
        ]
    )
    session.add(report)
    await session.commit()
    await session.refresh(report)

    async def send_localization():
        logger.info("Sending report to OD...")
        await od_client_handles.localization_api_v1_localization_post.asyncio_detailed(
            client=od_client,
            body=OdLocalizeDto(
                image=source_image_b64.decode('ascii'),
                report_id=report.id
            ),
        )
        logger.info("Sending report to MAC...")
        await mac_client_handles.localization_api_v1_localization_post.asyncio_detailed(
            client=mac_client,
            body=MacLocalizeDto(
                image=source_image_b64.decode('ascii'),
                report_id=report.id
            ),
        )
        logger.info("Sending report to AV...")
        await av_client_handles.segmentation_api_v1_segmentation_post.asyncio_detailed(
            client=av_client,
            body=AvSegmentationInDto(
                image=source_image_b64.decode('ascii'),
                report_id=report.id
            ),
        )

    asyncio.ensure_future(send_localization())
    return await ReportDetailedOutDto.from_report(session, report)


@app.put("/api/v1/report/{report_id}", response_model=ReportDetailedOutDto)
async def update_report(
        report_in_dto: ReportUpdateInDto,
        report_id: int,
        current_user: CurrentAuthData,
        session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Report).where(Report.id == report_id))
    db_report: Report = result.scalar_one_or_none()
    if not db_report or db_report.soft_deleted:
        raise report_not_found_exception
    if (db_report.author_id != current_user.id and
            not current_user.service and
            not current_user.superuser):
        raise report_access_forbidden_exception

    if report_in_dto.title:
        db_report.title = report_in_dto.title

    if report_in_dto.params:
        final_params = []
        params_dict = {}
        for new_param in report_in_dto.params:
            final_params.append(
                ReportParameter(
                    name=new_param.name,
                    type=new_param.type.value,
                    data=new_param.data.dict(),
                )
            )
            params_dict[new_param.name] = new_param.type.value

        max_version = (await ReportParameter.get_max_version(session, report_id)) or 0
        for param in final_params:
            param.version = max_version + 1
            param.report_id = report_id
        session.add_all(final_params)

        # TODO Возможно нужна проверка на NULL result
        result = await session.execute(
            select(ReportText).where((ReportText.report_id == report_id) & (ReportText.active == True)))
        report_text: ReportText = result.scalar_one_or_none()

        async def send_correction():
            logger.info("Sending text to LLM for correction")

            await llm_client_handles.correct_api_v1_correct_post.asyncio_detailed(
                client=llm_client,
                body=TextCorrectInDTO(
                    report_id=report_id,
                    params=TextInDTOParams.from_dict(params_dict),
                    text=report_text.text
                )
            )

        asyncio.ensure_future(send_correction())

        # if report_in_dto.text:
        #     #TODO Может тут нужна проверка на null
        #     active_text = await ReportText.select_active(session, report_id)
        #     active_text.text = report_in_dto.text
        #     session.add(active_text)

        await session.commit()
        await session.refresh(db_report)

    return await ReportDetailedOutDto.from_report(session, db_report)


@app.get("/api/v1/report/{report_id}", response_model=ReportDetailedOutDto)
async def get_report(
        report_id: int,
        current_user: CurrentAuthData,
        session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Report).where(Report.id == report_id))
    report: Report = result.scalar_one_or_none()
    if report is None or report.soft_deleted:
        raise report_not_found_exception
    if (report.author_id != current_user.id and
            not current_user.service and
            not current_user.superuser):
        raise report_access_forbidden_exception
    return await ReportDetailedOutDto.from_report(session, report)


@app.delete("/api/v1/report/{report_id}", response_model=ReportDeletedOutDto)
async def delete_report(
        report_id: int,
        current_user: CurrentAuthData,
        session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Report).where(Report.id == report_id))
    report: Report = result.scalar_one_or_none()
    if report is None or report.soft_deleted:
        raise report_not_found_exception
    if report.author_id != current_user.id and not current_user.superuser:
        raise report_access_forbidden_exception
    report.soft_deleted = True
    await session.commit()
    await session.refresh(report)
    return ReportDeletedOutDto()


@app.post("/api/v1/report/{report_id}/read", response_model=ReportOutDto)
async def read_report(
        report_id: int,
        current_user: CurrentAuthData,
        session: AsyncSession = Depends(get_session),
):
    db_report: Optional[Report] = await session.get(Report, report_id)
    if not db_report or db_report.soft_deleted:
        raise report_not_found_exception
    if db_report.author_id != current_user.id:
        raise report_access_forbidden_exception
    db_report.status = ReportStatusType.READ.value
    await session.commit()
    await session.refresh(db_report)
    return db_report


@app.get("/api/v1/report/{report_id}/image/{image_type}", response_class=Response)
async def get_report_image(
        report_id: int,
        image_type: str,
        current_user: CurrentAuthData,
        session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Report).where(Report.id == report_id))
    report: Report = result.scalar_one_or_none()
    if report is None or report.soft_deleted:
        raise report_not_found_exception
    if (report.author_id != current_user.id and
            not current_user.service and
            not current_user.superuser):
        raise report_access_forbidden_exception
    result = await session.execute(
        select(ReportImage)
        .where(ReportImage.report_id == report_id)
        .where(ReportImage.image_type == image_type)
    )
    image: ReportImage = result.scalar_one_or_none()
    if image is None:
        raise image_not_found_exception
    return Response(content=image.data, media_type="image/png")


@app.get("/api/v1/report", response_model=List[ReportOutDto])
async def list_reports(
        current_user: CurrentAuthData,
        session: AsyncSession = Depends(get_session),
):
    results = await session.execute(
        select(Report)
        .where(Report.author_id == current_user.id)
        .where(Report.soft_deleted == False)
    )
    return results.scalars().all()


@app.post(
    path="/api/v1/report/service/{report_id}/image/{image_type}",
    response_model=ReportUploadImageOutDto
)
async def upload_report_image(
        report_id: int,
        image_type: ReportImageType,
        in_dto: ReportUploadImageInDto,
        current_service: CurrentServiceData,
        session: AsyncSession = Depends(get_session),
):
    assert current_service.service
    result = await session.execute(
        select(Report)
        .where(Report.id == report_id)
        .options(selectinload(Report.images)))
    db_report: Report = result.scalar_one_or_none()
    if not db_report or db_report.soft_deleted:
        raise report_not_found_exception
    db_report.images.append(ReportImage(
        image_type=image_type,
        data=base64.b64decode(in_dto.image)
    ))
    await session.commit()
    await session.refresh(db_report)
    return ReportUploadImageOutDto(success=True)


@app.put("/api/v1/report/service/{report_id}", response_class=Response)
async def update_report(
        report_in_dto: ReportUpdateInDto,
        report_id: int,
        current_user: CurrentServiceData,
        session: AsyncSession = Depends(get_session),
):
    assert current_user.service
    result = await session.execute(select(Report).where(Report.id == report_id))
    db_report: Report = result.scalar_one_or_none()
    if not db_report or db_report.soft_deleted:
        raise report_not_found_exception

    if report_in_dto.params:
        final_params = []
        for new_param in report_in_dto.params:
            final_params.append(
                ReportParameter(
                    name=new_param.name,
                    type=new_param.type.value,
                    data=new_param.data.dict(),
                )
            )

        max_version = (await ReportParameter.get_max_version(session, report_id)) or 0
        for param in final_params:
            param.version = max_version
            param.report_id = report_id
        session.add_all(final_params)

    if report_in_dto.text:

        active_text = await ReportText.select_active(session, report_id)
        if active_text:
            active_text.active = False
            session.add(active_text)

        max_version = (await ReportText.get_max_version(session, report_id)) or 0
        new_text = ReportText(
            report_id=report_id,
            text=report_in_dto.text,
            active=True,
            version=max_version,
            num_word=len(report_in_dto.text.split()),
            num_symbols=len(report_in_dto.text),
        )

        session.add(new_text)

    await session.commit()
    return Response(content="OK")


@app.post(
    "/api/v1/report/service/{report_id}/service_status",
    response_model=ReportServiceStatusOutDto
)
async def update_service_status(
        in_dto: ReportServiceStatusInDto,
        report_id: int,
        current_user: CurrentServiceData,
        session: AsyncSession = Depends(get_session),
):
    assert current_user.service

    result = await session.execute(select(Report).where(Report.id == report_id))
    db_report: Report = result.scalar_one_or_none()
    if not db_report or db_report.soft_deleted:
        raise report_not_found_exception

    current_service = Service(current_user.id)
    success = False
    for status in db_report.statuses:
        if status.service_id == current_service:
            status.status = in_dto.status
            success = True
            session.add(status)

    if not success:
        raise ValueError(
            f"Unknown service (id={current_service}) tried to update status: {in_dto}")

    logger.info(f"Got ack from {current_service.name}: {in_dto.status}")

    service_report_map = {
        Service(status.service_id): ReportStatusType(status.status)
        for status in db_report.statuses
    }
    service_report_map = {
        analysis_service: service_report_map[analysis_service]
        for analysis_service in ANALYSIS_SERVICES
    }
    if None in service_report_map.values():
        raise ValueError("Service status is NONE!")

    logger.info(f"Statuses: {service_report_map}")

    unique_values = set(service_report_map.values())
    if set(ANALYSIS_SERVICES) == service_report_map.keys() and len(
            unique_values) == 1 and in_dto.status != "generation":
        value = next(iter(unique_values))
        logger.info(f"All services finished {value}")
        if value == ReportStatusType.LOCALIZATION:
            db_report.status = ReportStatusType.LOCALIZATION

            async def send_all_classification():
                logger.info("Sending classification to OD")
                await send_classification(
                    session,
                    db_report,
                    image_type=ReportImageType.OD_SEGMENTATION,
                    where=od_client_handles.classification_api_v1_classification_post,
                    dto_class=OdLocalizeDto,
                    client=od_client,
                )
                logger.info("Sending classification to MAC")
                await send_classification(
                    session,
                    db_report,
                    image_type=ReportImageType.MAC_SEGMENTATION,
                    where=mac_client_handles.classification_api_v1_classification_post,
                    dto_class=MacLocalizeDto,
                    client=mac_client,
                )
                logger.info("Sending classification to AV")
                await send_classification(
                    session,
                    db_report,
                    image_type=ReportImageType.AV_SEGMENTATION,
                    where=av_client_handles.classification_api_v1_classification_post,
                    dto_class=AvSegmentationInDto,
                    client=av_client,
                )

            asyncio.ensure_future(send_all_classification())
        elif value == ReportStatusType.CLASSIFICATION:
            db_report.status = ReportStatusType.CLASSIFICATION

            asyncio.ensure_future(send_text_generation(session, report_id))
        else:
            raise ValueError(f"UNKNOWN '{value}'")

    elif in_dto.status == "generation":
        db_report.status = ReportStatusType.GENERATION
        logger.info(f"DONE! With the report={report_id}")

    await session.commit()
    return ReportServiceStatusOutDto(success=True)


async def send_text_generation(
        session: AsyncSession,
        report_id: int
):
    params_dict = {}

    result = await session.exec(
        select(ReportParameter)
        .where(ReportParameter.report_id == report_id)
        .where(ReportParameter.version == 0)
    )

    for param in result:
        params_dict[param.name] = param.type

    logger.info("Sending report for text generation")

    await llm_client_handles.generation_api_v1_generation_post.asyncio_detailed(
        client=llm_client,
        body=TextInDTO(
            report_id=report_id,
            params=TextInDTOParams.from_dict(params_dict)
        )
    )


async def send_classification(
        session: AsyncSession,
        report: Report,
        image_type: ReportImageType,
        where: Any,
        dto_class: Any,
        client: Any
):
    result = await session.execute(
        select(ReportImage)
        .where(ReportImage.report_id == report.id)
        .where(ReportImage.image_type == image_type)
    )
    image: ReportImage = result.scalar_one_or_none()
    if image is None:
        raise image_not_found_exception
    mask_b64 = base64.b64encode(image.data).decode('ascii')
    await where.asyncio_detailed(
        client=client,
        body=dto_class(
            image=mask_b64,
            report_id=report.id
        )
    )


@app.post("api/v1/report/{report_id}/active/{version}", response_model=ReportDetailedOutDto)
async def update_active_text(
        report_id: int,
        version: int,
        current_user: CurrentAuthData,
        session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Report).where(Report.id == report_id))
    db_report: Report = result.scalar_one_or_none()
    if not db_report or db_report.soft_deleted:
        raise report_not_found_exception
    if (db_report.author_id != current_user.id and
            not current_user.service and
            not current_user.superuser):
        raise report_access_forbidden_exception

    active_text = await ReportText.select_active(session, report_id)
    if active_text:
        active_text.active = False
        session.add(active_text)

    version_text = await ReportText.select_version(session, report_id, version)
    version_text.active = True
    session.add(version_text)

    await session.commit()
    await session.refresh(db_report)

    return await ReportDetailedOutDto.from_report(session, db_report)
