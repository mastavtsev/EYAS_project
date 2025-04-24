from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, DateTime, JSON, LargeBinary, String, text, \
    UniqueConstraint
from sqlmodel import Field, Relationship, select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

# noinspection PyUnresolvedReferences
from models.user_models import User


class ReportStatusType(str, Enum):
    PENDING = "pending"
    LOCALIZATION = "localization"
    CLASSIFICATION = "classification"
    GENERATION = "generation"
    UPDATING = "updating"
    COMPLETED = "completed"
    READ = "read"

    def __str__(self) -> str:
        return self.value


class ReportImageType(str, Enum):
    SOURCE = "source"
    MAC_SEGMENTATION = "mac_segmentation"
    MAC_CONTOUR = "mac_contour"
    OD_SEGMENTATION = "od_segmentation"
    OD_CONTOUR = "od_contour"
    AV_SEGMENTATION = "av_segmentation"

    def __str__(self) -> str:
        return self.value


class ReportBase(SQLModel):
    author_id: int = Field(default=None, nullable=False, foreign_key="user.id")
    status: str = Field(sa_column=Column(String, nullable=False))
    title: str = Field(default=None, nullable=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime, default=datetime.now, nullable=False))


class Report(ReportBase, table=True):
    id: int = Field(default=None, nullable=False, primary_key=True)
    soft_deleted: bool = Field(default=False, nullable=False)
    images: List["ReportImage"] = Relationship(back_populates="report")
    params: List["ReportParameter"] = Relationship(back_populates="report")
    statuses: List["ReportStatus"] = Relationship(
        back_populates="report",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    texts: List["ReportText"] = Relationship(back_populates="report")


class ReportImage(SQLModel, table=True):
    id: int = Field(default=None, nullable=False, primary_key=True)
    report_id: int = Field(default=None, nullable=False, foreign_key="report.id")
    image_type: str = Field(sa_column=Column(String, nullable=False))
    data: bytes = Field(default=None, sa_column=Column(LargeBinary, nullable=False))
    report: Report = Relationship(back_populates="images")


class ReportParameter(SQLModel, table=True):
    id: int = Field(default=None, nullable=False, primary_key=True)
    report_id: int = Field(default=None, nullable=False, foreign_key="report.id")
    version: int = Field(default=None, nullable=False)
    name: str = Field(default=None, nullable=False)
    type: str = Field(sa_column=Column(String, nullable=False))
    data: str = Field(default=None, sa_column=Column(JSON, nullable=False))
    report: Report = Relationship(back_populates="params")

    @staticmethod
    async def get_max_version(session: AsyncSession, report_id: int) -> Optional[int]:
        return (
            (
                await session.execute(
                    text(
                        f"SELECT MAX(version) FROM reportparameter rp WHERE rp.report_id={report_id}"
                    )
                )
            )
            .scalars()
            .one_or_none()
        )

    @staticmethod
    async def select_latest(
            session: AsyncSession, report_id: int
    ) -> List["ReportParameter"]:
        # TODO: transaction
        max_version = await ReportParameter.get_max_version(session, report_id)
        if max_version is None:
            return []
        result = await session.exec(
            select(ReportParameter)
            .where(ReportParameter.report_id == report_id)
            .where(ReportParameter.version == max_version)
        )
        return result.all()


class ReportStatus(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("report_id", "service_id", name="report_id_service_id_unique"),
    )
    id: int = Field(default=None, nullable=False, primary_key=True)
    report_id: int = Field(default=None, nullable=False, foreign_key="report.id")
    service_id: int = Field(default=None, nullable=False)
    status: str = Field(sa_column=Column(String, nullable=False))
    report: Report = Relationship(back_populates="statuses")


class ReportText(SQLModel, table=True):
    id: int = Field(default=None, nullable=False, primary_key=True)
    report_id: int = Field(default=None, nullable=False, foreign_key="report.id")
    text: str = Field(default=None, nullable=False)
    num_word: int = Field(default=None, nullable=False)
    num_symbols: int = Field(default=None, nullable=False)
    active: bool = Field(default=None, nullable=False)
    version: int = Field(default=None, nullable=False)
    params_version: int = Field(default=None, nullable=False)  #
    report: Report = Relationship(back_populates="texts")

    @staticmethod
    async def get_max_version(session: AsyncSession, report_id: int) -> Optional[int]:
        return (
            (
                await session.execute(
                    text(
                        f"SELECT MAX(version) FROM reporttext rt WHERE rt.report_id={report_id}"
                    )
                )
            )
            .scalars()
            .one_or_none()
        )

    @staticmethod
    async def select_active(
            session: AsyncSession, report_id: int
    ) -> "ReportText":
        query = select(ReportText).where(
            ReportText.report_id == report_id,
            ReportText.active == True
        )
        result = await session.exec(query)
        active_text = result.one_or_none()
        return active_text

    @staticmethod
    async def select_available(
            session: AsyncSession,
            report_id: int,
    ) -> ["ReportText"]:
        max_version = await ReportParameter.get_max_version(session, report_id)

        query = select(ReportText).where(
            ReportText.report_id == report_id,
            ReportText.params_version == max_version
        ).order_by(ReportText.version)
        result = await session.exec(query)
        texts = result.all()
        return texts

    @staticmethod
    async def select_version(
            session: AsyncSession, report_id: int, version: int
    ) -> "ReportText":
        query = select(ReportText).where(
            ReportText.report_id == report_id,
            ReportText.version == version
        )
        result = await session.exec(query)
        version_text = result.one_or_none()
        return version_text
