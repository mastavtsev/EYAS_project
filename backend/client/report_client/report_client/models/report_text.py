from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportText")


@_attrs_define
class ReportText:
    """
    Attributes:
        id (Union[Unset, int]):
        report_id (Union[Unset, int]):
        text (Union[Unset, str]):
        num_word (Union[Unset, int]):
        num_symbols (Union[Unset, int]):
        active (Union[Unset, bool]):
        version (Union[Unset, int]):
        params_version (Union[Unset, int]):
    """

    id: Union[Unset, int] = UNSET
    report_id: Union[Unset, int] = UNSET
    text: Union[Unset, str] = UNSET
    num_word: Union[Unset, int] = UNSET
    num_symbols: Union[Unset, int] = UNSET
    active: Union[Unset, bool] = UNSET
    version: Union[Unset, int] = UNSET
    params_version: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        report_id = self.report_id

        text = self.text

        num_word = self.num_word

        num_symbols = self.num_symbols

        active = self.active

        version = self.version

        params_version = self.params_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if report_id is not UNSET:
            field_dict["report_id"] = report_id
        if text is not UNSET:
            field_dict["text"] = text
        if num_word is not UNSET:
            field_dict["num_word"] = num_word
        if num_symbols is not UNSET:
            field_dict["num_symbols"] = num_symbols
        if active is not UNSET:
            field_dict["active"] = active
        if version is not UNSET:
            field_dict["version"] = version
        if params_version is not UNSET:
            field_dict["params_version"] = params_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        report_id = d.pop("report_id", UNSET)

        text = d.pop("text", UNSET)

        num_word = d.pop("num_word", UNSET)

        num_symbols = d.pop("num_symbols", UNSET)

        active = d.pop("active", UNSET)

        version = d.pop("version", UNSET)

        params_version = d.pop("params_version", UNSET)

        report_text = cls(
            id=id,
            report_id=report_id,
            text=text,
            num_word=num_word,
            num_symbols=num_symbols,
            active=active,
            version=version,
            params_version=params_version,
        )

        report_text.additional_properties = d
        return report_text

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
