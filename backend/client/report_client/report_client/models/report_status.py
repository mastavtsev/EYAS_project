from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportStatus")


@_attrs_define
class ReportStatus:
    """
    Attributes:
        status (str):
        id (Union[Unset, int]):
        report_id (Union[Unset, int]):
        service_id (Union[Unset, int]):
    """

    status: str
    id: Union[Unset, int] = UNSET
    report_id: Union[Unset, int] = UNSET
    service_id: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        id = self.id

        report_id = self.report_id

        service_id = self.service_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if report_id is not UNSET:
            field_dict["report_id"] = report_id
        if service_id is not UNSET:
            field_dict["service_id"] = service_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = d.pop("status")

        id = d.pop("id", UNSET)

        report_id = d.pop("report_id", UNSET)

        service_id = d.pop("service_id", UNSET)

        report_status = cls(
            status=status,
            id=id,
            report_id=report_id,
            service_id=service_id,
        )

        report_status.additional_properties = d
        return report_status

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
