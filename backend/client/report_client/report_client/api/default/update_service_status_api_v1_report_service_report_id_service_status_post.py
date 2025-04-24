from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.report_service_status_in_dto import ReportServiceStatusInDto
from ...models.report_service_status_out_dto import ReportServiceStatusOutDto
from ...types import Response


def _get_kwargs(
    report_id: int,
    *,
    body: ReportServiceStatusInDto,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/report/service/{report_id}/service_status",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ReportServiceStatusOutDto]]:
    if response.status_code == 200:
        response_200 = ReportServiceStatusOutDto.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[HTTPValidationError, ReportServiceStatusOutDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    report_id: int,
    *,
    client: AuthenticatedClient,
    body: ReportServiceStatusInDto,
) -> Response[Union[HTTPValidationError, ReportServiceStatusOutDto]]:
    """Update Service Status

    Args:
        report_id (int):
        body (ReportServiceStatusInDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ReportServiceStatusOutDto]]
    """

    kwargs = _get_kwargs(
        report_id=report_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    report_id: int,
    *,
    client: AuthenticatedClient,
    body: ReportServiceStatusInDto,
) -> Optional[Union[HTTPValidationError, ReportServiceStatusOutDto]]:
    """Update Service Status

    Args:
        report_id (int):
        body (ReportServiceStatusInDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ReportServiceStatusOutDto]
    """

    return sync_detailed(
        report_id=report_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    report_id: int,
    *,
    client: AuthenticatedClient,
    body: ReportServiceStatusInDto,
) -> Response[Union[HTTPValidationError, ReportServiceStatusOutDto]]:
    """Update Service Status

    Args:
        report_id (int):
        body (ReportServiceStatusInDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ReportServiceStatusOutDto]]
    """

    kwargs = _get_kwargs(
        report_id=report_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    report_id: int,
    *,
    client: AuthenticatedClient,
    body: ReportServiceStatusInDto,
) -> Optional[Union[HTTPValidationError, ReportServiceStatusOutDto]]:
    """Update Service Status

    Args:
        report_id (int):
        body (ReportServiceStatusInDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ReportServiceStatusOutDto]
    """

    return (
        await asyncio_detailed(
            report_id=report_id,
            client=client,
            body=body,
        )
    ).parsed
