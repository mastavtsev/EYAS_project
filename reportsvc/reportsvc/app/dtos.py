from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from models.report_models import Report, ReportBase, ReportParameter, ReportStatus, \
    ReportStatusType, ReportText
from param_lib.params import Parameter, ParameterBase
from whitebox.service import Service


@dataclass
class ReportRequestInDto:
    title: str
    source_image: str


@dataclass
class ReportUpdateInDto:
    title: Optional[str]
    params: Optional[List[Parameter]] = None
    text: Optional[str] = None


def serialize_params(value: ReportParameter):
    return ParameterBase.model_validate(value.dict())


class ReportOutDto(ReportBase):
    id: int

    class Config:
        json_encoders = {datetime: lambda v: int(v.timestamp())}


class ReportDetailedOutDto(ReportBase):
    id: int
    params: List[ReportParameter] = []
    text: Optional[ReportText] = None
    statuses: List[ReportStatus] = []

    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp()),
            ReportParameter: serialize_params,
            List[ReportStatus]: lambda sts: {
                Service(v.service_id).name: v.status
                for v in sts
            },
        }

    @staticmethod
    async def from_report(session: AsyncSession, db_report: Report):
        return ReportDetailedOutDto(
            author_id=db_report.author_id,
            id=db_report.id,
            params=await ReportParameter.select_latest(session, report_id=db_report.id),
            text=await ReportText.select_active(session, report_id=db_report.id),
            title=db_report.title,
            status=db_report.status,
            statuses=db_report.statuses,
            created_at=db_report.created_at
        )


class ReportDeletedOutDto(BaseModel):
    success: bool = True


class ReportUploadImageInDto(BaseModel):
    image: str


class ReportUploadImageOutDto(BaseModel):
    success: bool = True


class ReportServiceStatusInDto(BaseModel):
    status: ReportStatusType


class ReportServiceStatusOutDto(BaseModel):
    success: bool = True

class ReportTextUpdateInDto(BaseModel):
    text: str

class ReportTextUpdateOutDto(BaseModel):
    success: bool = True
