import importlib
import json
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# Ajusta o caminho para importar corretamente o módulo da Lambda
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../lambda_market_list/get_items/src")
    )
)

# Importa o módulo onde estão as funções da Lambda
import get_items


def test_lambda_handler_success(mock_table):
    mock_table.query.return_value = {
        "Items": [{"itemId": "123", "name": "banana", "status": "todo"}]
    }

    event = {"queryStringParameters": {"date": "20250526"}}
    response = get_items.lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["success"] is True
    assert "banana" in response["body"]
    assert f"{len(body['items'])} item(s)" in body["message"]


def test_lambda_handler_no_date_parameter(mock_table):
    mock_table.query.return_value = {
        "Items": [{"itemId": "456", "name": "apple", "status": "todo"}]
    }

    event = {"queryStringParameters": None}
    response = get_items.lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["success"] is True
    assert "apple" in response["body"]
    today = datetime.now().strftime("%Y%m%d")
    assert f"lista de {today}" in body["message"]


def test_lambda_handler_empty_items(mock_table):
    mock_table.query.return_value = {"Items": []}

    event = {"queryStringParameters": {"date": "20250526"}}
    response = get_items.lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["success"] is True
    assert body["items"] == []


def test_lambda_handler_exception(mock_table):
    mock_table.query.side_effect = Exception("DynamoDB falhou")

    event = {"queryStringParameters": {"date": "20250526"}}
    response = get_items.lambda_handler(event, None)

    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert body["success"] is False
    assert "DynamoDB falhou" in body["message"]
