from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.pdf_in_dto_params import PDFInDTOParams


T = TypeVar("T", bound="PDFInDTO")


@_attrs_define
class PDFInDTO:
    """
    Attributes:
        report_id (int):
        params (PDFInDTOParams):
        source_img (str):
        od_img (str):
        av_img (str):
        mac_img (str):
        text (str):
    """

    report_id: int
    params: "PDFInDTOParams"
    source_img: str
    od_img: str
    av_img: str
    mac_img: str
    text: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        report_id = self.report_id

        params = self.params.to_dict()

        source_img = self.source_img

        od_img = self.od_img

        av_img = self.av_img

        mac_img = self.mac_img

        text = self.text

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "report_id": report_id,
                "params": params,
                "source_img": source_img,
                "od_img": od_img,
                "av_img": av_img,
                "mac_img": mac_img,
                "text": text,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pdf_in_dto_params import PDFInDTOParams

        d = dict(src_dict)
        report_id = d.pop("report_id")

        params = PDFInDTOParams.from_dict(d.pop("params"))

        source_img = d.pop("source_img")

        od_img = d.pop("od_img")

        av_img = d.pop("av_img")

        mac_img = d.pop("mac_img")

        text = d.pop("text")

        pdf_in_dto = cls(
            report_id=report_id,
            params=params,
            source_img=source_img,
            od_img=od_img,
            av_img=av_img,
            mac_img=mac_img,
            text=text,
        )

        pdf_in_dto.additional_properties = d
        return pdf_in_dto

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
