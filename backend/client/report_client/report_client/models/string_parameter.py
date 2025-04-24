from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.string_parameter_data import StringParameterData


T = TypeVar("T", bound="StringParameter")


@_attrs_define
class StringParameter:
    """
    Attributes:
        name (str):
        data (StringParameterData):
        type_ (Union[Literal['string'], Unset]):  Default: 'string'.
    """

    name: str
    data: "StringParameterData"
    type_: Union[Literal["string"], Unset] = "string"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        data = self.data.to_dict()

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "data": data,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.string_parameter_data import StringParameterData

        d = dict(src_dict)
        name = d.pop("name")

        data = StringParameterData.from_dict(d.pop("data"))

        type_ = cast(Union[Literal["string"], Unset], d.pop("type", UNSET))
        if type_ != "string" and not isinstance(type_, Unset):
            raise ValueError(f"type must match const 'string', got '{type_}'")

        string_parameter = cls(
            name=name,
            data=data,
            type_=type_,
        )

        string_parameter.additional_properties = d
        return string_parameter

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
