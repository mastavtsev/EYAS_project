from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.report_image_type import ReportImageType
from ...models.report_upload_image_in_dto import ReportUploadImageInDto
from ...models.report_upload_image_out_dto import ReportUploadImageOutDto
from ...types import Response


def _get_kwargs(
    report_id: int,
    image_type: ReportImageType,
    *,
    body: ReportUploadImageInDto,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/report/service/{report_id}/image/{image_type}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ReportUploadImageOutDto]]:
    if response.status_code == 200:
        response_200 = ReportUploadImageOutDto.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ReportUploadImageOutDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    report_id: int,
    image_type: ReportImageType,
    *,
    client: AuthenticatedClient,
    body: ReportUploadImageInDto,
) -> Response[Union[HTTPValidationError, ReportUploadImageOutDto]]:
    """Upload Report Image

    Args:
        report_id (int):
        image_type (ReportImageType):
        body (ReportUploadImageInDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ReportUploadImageOutDto]]
    """

    kwargs = _get_kwargs(
        report_id=report_id,
        image_type=image_type,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    report_id: int,
    image_type: ReportImageType,
    *,
    client: AuthenticatedClient,
    body: ReportUploadImageInDto,
) -> Optional[Union[HTTPValidationError, ReportUploadImageOutDto]]:
    """Upload Report Image

    Args:
        report_id (int):
        image_type (ReportImageType):
        body (ReportUploadImageInDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ReportUploadImageOutDto]
    """

    return sync_detailed(
        report_id=report_id,
        image_type=image_type,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    report_id: int,
    image_type: ReportImageType,
    *,
    client: AuthenticatedClient,
    body: ReportUploadImageInDto,
) -> Response[Union[HTTPValidationError, ReportUploadImageOutDto]]:
    """Upload Report Image

    Args:
        report_id (int):
        image_type (ReportImageType):
        body (ReportUploadImageInDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ReportUploadImageOutDto]]
    """

    kwargs = _get_kwargs(
        report_id=report_id,
        image_type=image_type,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    report_id: int,
    image_type: ReportImageType,
    *,
    client: AuthenticatedClient,
    body: ReportUploadImageInDto,
) -> Optional[Union[HTTPValidationError, ReportUploadImageOutDto]]:
    """Upload Report Image

    Args:
        report_id (int):
        image_type (ReportImageType):
        body (ReportUploadImageInDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ReportUploadImageOutDto]
    """

    return (
        await asyncio_detailed(
            report_id=report_id,
            image_type=image_type,
            client=client,
            body=body,
        )
    ).parsed
