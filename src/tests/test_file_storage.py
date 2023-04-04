import os
from pathlib import Path

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


async def test_add_user(
    async_client: AsyncClient,
    async_session: AsyncSession,
    user_test_data: dict,
    prefix_user_url: str,
):
    user = await async_client.post(
        f"{prefix_user_url}/register", json=user_test_data
    )
    assert user.status_code == status.HTTP_201_CREATED


async def test_get_token_user(
    async_client: AsyncClient,
    async_session: AsyncSession,
    user_test_data: dict,
    prefix_user_url: str,
):
    await async_client.post(f"{prefix_user_url}/register", json=user_test_data)
    response = await async_client.post(
        f"{prefix_user_url}/auth", json=user_test_data
    )
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"


async def test_token(
    async_client: AsyncClient,
    async_session: AsyncSession,
    user_test_data: dict,
    prefix_user_url: str,
):
    await async_client.post(f"{prefix_user_url}/register", json=user_test_data)
    response = await async_client.post(
        f"{prefix_user_url}/auth", json=user_test_data
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get(f"{prefix_user_url}/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert "name" in json_response
    assert json_response["name"] == user_test_data["name"]


async def test_file_storage_empty(
    async_client: AsyncClient,
    async_session: AsyncSession,
    user_test_data: dict,
    prefix_user_url: str,
    prefix_file_url: str,
):
    await async_client.post(f"{prefix_user_url}/register", json=user_test_data)
    response = await async_client.post(
        f"{prefix_user_url}/auth", json=user_test_data
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get(prefix_file_url, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert "account" in json_response
    assert json_response["account"] == user_test_data["name"]
    assert "files" in json_response
    assert json_response["files"] == []


async def test_upload_file(
    async_client: AsyncClient,
    async_session: AsyncSession,
    user_test_data: dict,
    prefix_user_url: str,
    prefix_file_url: str,
    test_file: Path,
):
    await async_client.post(f"{prefix_user_url}/register", json=user_test_data)
    response = await async_client.post(
        f"{prefix_user_url}/auth", json=user_test_data
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    path_value = "my_folder"
    with open(test_file, "rb") as open_file:
        response = await async_client.post(
            f"{prefix_file_url}/upload?path={path_value}",
            headers=headers,
            files={"in_file": open_file},
        )
        assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert "id" in json_response
    file_id = json_response["id"]
    assert "path" in json_response
    assert json_response["path"] == path_value
    assert "size" in json_response
    assert int(json_response["size"]) > 0
    static_path = f"static/{file_id}"
    assert os.path.exists(static_path) is True

    os.remove(static_path)
    assert os.path.exists(static_path) is False


async def test_increasing_count_after_upload_file(
    async_client: AsyncClient,
    async_session: AsyncSession,
    user_test_data: dict,
    prefix_user_url: str,
    prefix_file_url: str,
    test_file: Path,
):
    await async_client.post(f"{prefix_user_url}/register", json=user_test_data)
    response = await async_client.post(
        f"{prefix_user_url}/auth", json=user_test_data
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    path_value = "my_folder"
    with open(test_file, "rb") as open_file:
        response = await async_client.post(
            f"{prefix_file_url}/upload?path={path_value}",
            headers=headers,
            files={"in_file": open_file},
        )
    json_response = response.json()
    file_id = json_response["id"]
    static_path = f"static/{file_id}"
    response = await async_client.get(prefix_file_url, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert "files" in json_response
    assert len(json_response["files"]) == 1

    os.remove(static_path)
    assert os.path.exists(static_path) is False
