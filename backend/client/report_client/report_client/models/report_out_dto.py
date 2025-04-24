import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportOutDto")


@_attrs_define
class ReportOutDto:
    """
    Attributes:
        status (str):
        created_at (datetime.datetime):
        id (int):
        author_id (Union[Unset, int]):
        title (Union[Unset, str]):
    """

    status: str
    created_at: datetime.datetime
    id: int
    author_id: Union[Unset, int] = UNSET
    title: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        created_at = self.created_at.isoformat()

        id = self.id

        author_id = self.author_id

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "created_at": created_at,
                "id": id,
            }
        )
        if author_id is not UNSET:
            field_dict["author_id"] = author_id
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = d.pop("status")

        created_at = isoparse(d.pop("created_at"))

        id = d.pop("id")

        author_id = d.pop("author_id", UNSET)

        title = d.pop("title", UNSET)

        report_out_dto = cls(
            status=status,
            created_at=created_at,
            id=id,
            author_id=author_id,
            title=title,
        )

        report_out_dto.additional_properties = d
        return report_out_dto

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
