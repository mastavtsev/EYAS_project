from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportParameter")


@_attrs_define
class ReportParameter:
    """
    Attributes:
        type_ (str):
        id (Union[Unset, int]):
        report_id (Union[Unset, int]):
        version (Union[Unset, int]):
        name (Union[Unset, str]):
        data (Union[Unset, str]):
    """

    type_: str
    id: Union[Unset, int] = UNSET
    report_id: Union[Unset, int] = UNSET
    version: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    data: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        id = self.id

        report_id = self.report_id

        version = self.version

        name = self.name

        data = self.data

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if report_id is not UNSET:
            field_dict["report_id"] = report_id
        if version is not UNSET:
            field_dict["version"] = version
        if name is not UNSET:
            field_dict["name"] = name
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = d.pop("type")

        id = d.pop("id", UNSET)

        report_id = d.pop("report_id", UNSET)

        version = d.pop("version", UNSET)

        name = d.pop("name", UNSET)

        data = d.pop("data", UNSET)

        report_parameter = cls(
            type_=type_,
            id=id,
            report_id=report_id,
            version=version,
            name=name,
            data=data,
        )

        report_parameter.additional_properties = d
        return report_parameter

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
