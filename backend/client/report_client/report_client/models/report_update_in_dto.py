from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.boolean_parameter import BooleanParameter
    from ..models.enum_parameter import EnumParameter
    from ..models.string_parameter import StringParameter


T = TypeVar("T", bound="ReportUpdateInDto")


@_attrs_define
class ReportUpdateInDto:
    """
    Attributes:
        title (Union[None, str]):
        params (Union[None, Unset, list[Union['BooleanParameter', 'EnumParameter', 'StringParameter']]]):
        text (Union[None, Unset, str]):
    """

    title: Union[None, str]
    params: Union[None, Unset, list[Union["BooleanParameter", "EnumParameter", "StringParameter"]]] = UNSET
    text: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.boolean_parameter import BooleanParameter
        from ..models.string_parameter import StringParameter

        title: Union[None, str]
        title = self.title

        params: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.params, Unset):
            params = UNSET
        elif isinstance(self.params, list):
            params = []
            for params_type_0_item_data in self.params:
                params_type_0_item: dict[str, Any]
                if isinstance(params_type_0_item_data, BooleanParameter):
                    params_type_0_item = params_type_0_item_data.to_dict()
                elif isinstance(params_type_0_item_data, StringParameter):
                    params_type_0_item = params_type_0_item_data.to_dict()
                else:
                    params_type_0_item = params_type_0_item_data.to_dict()

                params.append(params_type_0_item)

        else:
            params = self.params

        text: Union[None, Unset, str]
        if isinstance(self.text, Unset):
            text = UNSET
        else:
            text = self.text

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
            }
        )
        if params is not UNSET:
            field_dict["params"] = params
        if text is not UNSET:
            field_dict["text"] = text

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.boolean_parameter import BooleanParameter
        from ..models.enum_parameter import EnumParameter
        from ..models.string_parameter import StringParameter

        d = dict(src_dict)

        def _parse_title(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        title = _parse_title(d.pop("title"))

        def _parse_params(
            data: object,
        ) -> Union[None, Unset, list[Union["BooleanParameter", "EnumParameter", "StringParameter"]]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                params_type_0 = []
                _params_type_0 = data
                for params_type_0_item_data in _params_type_0:

                    def _parse_params_type_0_item(
                        data: object,
                    ) -> Union["BooleanParameter", "EnumParameter", "StringParameter"]:
                        try:
                            if not isinstance(data, dict):
                                raise TypeError()
                            params_type_0_item_type_0 = BooleanParameter.from_dict(data)

                            return params_type_0_item_type_0
                        except:  # noqa: E722
                            pass
                        try:
                            if not isinstance(data, dict):
                                raise TypeError()
                            params_type_0_item_type_1 = StringParameter.from_dict(data)

                            return params_type_0_item_type_1
                        except:  # noqa: E722
                            pass
                        if not isinstance(data, dict):
                            raise TypeError()
                        params_type_0_item_type_2 = EnumParameter.from_dict(data)

                        return params_type_0_item_type_2

                    params_type_0_item = _parse_params_type_0_item(params_type_0_item_data)

                    params_type_0.append(params_type_0_item)

                return params_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[Union["BooleanParameter", "EnumParameter", "StringParameter"]]], data)

        params = _parse_params(d.pop("params", UNSET))

        def _parse_text(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        text = _parse_text(d.pop("text", UNSET))

        report_update_in_dto = cls(
            title=title,
            params=params,
            text=text,
        )

        report_update_in_dto.additional_properties = d
        return report_update_in_dto

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
