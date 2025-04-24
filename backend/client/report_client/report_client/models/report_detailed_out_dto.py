import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.report_parameter import ReportParameter
    from ..models.report_status import ReportStatus
    from ..models.report_text import ReportText


T = TypeVar("T", bound="ReportDetailedOutDto")


@_attrs_define
class ReportDetailedOutDto:
    """
    Attributes:
        status (str):
        created_at (datetime.datetime):
        id (int):
        author_id (Union[Unset, int]):
        title (Union[Unset, str]):
        params (Union[Unset, list['ReportParameter']]):
        texts (Union[Unset, list['ReportText']]):
        statuses (Union[Unset, list['ReportStatus']]):
    """

    status: str
    created_at: datetime.datetime
    id: int
    author_id: Union[Unset, int] = UNSET
    title: Union[Unset, str] = UNSET
    params: Union[Unset, list["ReportParameter"]] = UNSET
    texts: Union[Unset, list["ReportText"]] = UNSET
    statuses: Union[Unset, list["ReportStatus"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        created_at = self.created_at.isoformat()

        id = self.id

        author_id = self.author_id

        title = self.title

        params: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.params, Unset):
            params = []
            for params_item_data in self.params:
                params_item = params_item_data.to_dict()
                params.append(params_item)

        texts: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.texts, Unset):
            texts = []
            for texts_item_data in self.texts:
                texts_item = texts_item_data.to_dict()
                texts.append(texts_item)

        statuses: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.statuses, Unset):
            statuses = []
            for statuses_item_data in self.statuses:
                statuses_item = statuses_item_data.to_dict()
                statuses.append(statuses_item)

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
        if params is not UNSET:
            field_dict["params"] = params
        if texts is not UNSET:
            field_dict["texts"] = texts
        if statuses is not UNSET:
            field_dict["statuses"] = statuses

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.report_parameter import ReportParameter
        from ..models.report_status import ReportStatus
        from ..models.report_text import ReportText

        d = dict(src_dict)
        status = d.pop("status")

        created_at = isoparse(d.pop("created_at"))

        id = d.pop("id")

        author_id = d.pop("author_id", UNSET)

        title = d.pop("title", UNSET)

        params = []
        _params = d.pop("params", UNSET)
        for params_item_data in _params or []:
            params_item = ReportParameter.from_dict(params_item_data)

            params.append(params_item)

        texts = []
        _texts = d.pop("texts", UNSET)
        for texts_item_data in _texts or []:
            texts_item = ReportText.from_dict(texts_item_data)

            texts.append(texts_item)

        statuses = []
        _statuses = d.pop("statuses", UNSET)
        for statuses_item_data in _statuses or []:
            statuses_item = ReportStatus.from_dict(statuses_item_data)

            statuses.append(statuses_item)

        report_detailed_out_dto = cls(
            status=status,
            created_at=created_at,
            id=id,
            author_id=author_id,
            title=title,
            params=params,
            texts=texts,
            statuses=statuses,
        )

        report_detailed_out_dto.additional_properties = d
        return report_detailed_out_dto

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
