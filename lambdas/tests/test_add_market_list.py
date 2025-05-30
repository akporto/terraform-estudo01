import json
import os
import sys
from unittest.mock import MagicMock

import pytest

# Ajusta o caminho para importar corretamente o módulo da Lambda
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../lambda_market_list/add_item/src")
    )
)

# Importa o módulo onde estão as funções da Lambda
import add_market_item


def test_create_item_success(mock_table):
    item = {"name": "Comprar pão"}
    response = add_market_item.create_item(item, mock_table)

    body = json.loads(response["body"])
    assert response["statusCode"] == 201
    assert body["success"] is True
    assert body["item"]["name"] == "Comprar pão"
    assert body["item"]["status"] == "todo"
    assert "PK" in body["item"]
    assert "SK" in body["item"]
    mock_table.put_item.assert_called_once()


def test_create_item_failure_missing_name(mock_table):
    item = {"name": " "}
    response = add_market_item.create_item(item, mock_table)

    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["success"] is False
    assert "obrigatório" in body["message"]
    mock_table.put_item.assert_not_called()


def test_lambda_handler_invalid_json(monkeypatch):
    event = {"body": "{invalid json"}
    context = {}

    # Corrigido: chamada correta ao handler da Lambda
    response = add_market_item.lambda_handler(event, context)
    body = json.loads(response["body"])

    assert response["statusCode"] == 500
    assert body["success"] is False
    assert "Erro ao processar" in body["message"]
