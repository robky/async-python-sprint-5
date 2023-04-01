import os
from pathlib import Path

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_file_storage(
        async_client: AsyncClient,
        async_session: AsyncSession,
        user_test_data: dict,
        prefix_user_url: str,
        prefix_file_url: str,
        test_file: Path,
):
    # Добавление пользователя
    user = await async_client.post(
        f"{prefix_user_url}/register", json=user_test_data)
    assert user.status_code == status.HTTP_201_CREATED

    # Получение токена
    response = await async_client.post(
        f"{prefix_user_url}/auth", json=user_test_data)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"
    token = json_response["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Проверка токена
    response = await async_client.get(
        f"{prefix_user_url}/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert "name" in json_response
    assert json_response["name"] == user_test_data["name"]

    # Таблица файлов пуста
    response = await async_client.get(
        prefix_file_url, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert "account" in json_response
    assert json_response["account"] == user_test_data["name"]
    assert "files" in json_response
    assert json_response["files"] == []

    # Добавление файла
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

    # Количество файлов увеличилось
    response = await async_client.get(
        prefix_file_url, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert "files" in json_response
    assert len(json_response["files"]) == 1

    # Перед окончанием теста необходимо удалить тестовый файл из папки static
    os.remove(static_path)
    assert os.path.exists(static_path) is False
