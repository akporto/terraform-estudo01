import importlib
import os
import sys
from unittest.mock import MagicMock

import pytest

os.environ["DYNAMODB_TABLE_NAME"] = "mock-table"

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../lambda_market_list/add_item/src")
    )
)

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../lambda_market_list/get_items/src")
    )
)

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../lambda_market_list/update_item/src")
    )
)

import get_items
import update_market_item
from add_market_item import lambda_handler


@pytest.fixture(scope="function")
def mock_table():
    table = MagicMock()
    return table


@pytest.fixture(autouse=True)
def patch_boto3_mock_table(monkeypatch, mock_table):
    """
    Aplica patch em boto3.resource para retornar mock_table,
    e recarrega o módulo get_items para que a variável table seja atualizada.
    """
    mock_dynamodb = MagicMock()
    mock_dynamodb.resource.return_value.Table.return_value = mock_table

    # Patch boto3.resource para sempre retornar mock_dynamodb.resource()
    monkeypatch.setattr(
        "boto3.resource", lambda service_name=None: mock_dynamodb.resource()
    )

    # Recarrega o módulos para aplicar o patch no objeto table
    importlib.reload(get_items)
    importlib.reload(update_market_item)

    yield
