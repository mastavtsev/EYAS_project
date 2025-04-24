from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.text_in_dto_params import TextInDTOParams


T = TypeVar("T", bound="TextInDTO")


@_attrs_define
class TextInDTO:
    """
    Attributes:
        report_id (int):
        params (TextInDTOParams):
    """

    report_id: int
    params: "TextInDTOParams"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        report_id = self.report_id

        params = self.params.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "report_id": report_id,
                "params": params,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.text_in_dto_params import TextInDTOParams

        d = src_dict.copy()
        report_id = d.pop("report_id")

        params = TextInDTOParams.from_dict(d.pop("params"))

        text_in_dto = cls(
            report_id=report_id,
            params=params,
        )

        text_in_dto.additional_properties = d
        return text_in_dto

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
