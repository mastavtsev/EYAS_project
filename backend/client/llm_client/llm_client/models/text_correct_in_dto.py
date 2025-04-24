from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.text_correct_in_dto_params import TextCorrectInDTOParams


T = TypeVar("T", bound="TextCorrectInDTO")


@_attrs_define
class TextCorrectInDTO:
    """
    Attributes:
        report_id (int):
        text (str):
        params (TextCorrectInDTOParams):
    """

    report_id: int
    text: str
    params: "TextCorrectInDTOParams"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        report_id = self.report_id

        text = self.text

        params = self.params.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "report_id": report_id,
                "text": text,
                "params": params,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.text_correct_in_dto_params import TextCorrectInDTOParams

        d = src_dict.copy()
        report_id = d.pop("report_id")

        text = d.pop("text")

        params = TextCorrectInDTOParams.from_dict(d.pop("params"))

        text_correct_in_dto = cls(
            report_id=report_id,
            text=text,
            params=params,
        )

        text_correct_in_dto.additional_properties = d
        return text_correct_in_dto

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
