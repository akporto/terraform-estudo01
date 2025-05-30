import json


def test_update_success(mock_table):
    from update_market_item import lambda_handler

    event = {
        "pathParameters": {"item_id": "123"},
        "body": json.dumps({"name": "Arroz", "status": "DONE", "date": "2025-06-01"}),
    }

    sample_item_to_update = {
        "PK": "LIST#20250530",
        "SK": "ITEM#123",
        "name": "Feijão",
        "status": "TODO",
        "date": "2025-05-30",
    }

    # Mock do retorno do query
    mock_table.query.return_value = {"Items": [sample_item_to_update]}

    # Mock do retorno do update_item
    mock_table.update_item.return_value = {
        "Attributes": {
            "PK": "LIST#20250530",
            "SK": "ITEM#123",
            "name": "Arroz",
            "status": "DONE",
            "date": "2025-06-01",
        }
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["success"] is True
    assert body["item"]["name"] == "Arroz"
    assert body["item"]["status"] == "DONE"


def test_update_invalid_status(mock_table):
    from update_market_item import lambda_handler

    event = {
        "pathParameters": {"item_id": "123"},
        "body": json.dumps({"status": "INVALID"}),
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["success"] is False
    assert "Status deve ser TODO ou DONE" in body["message"]


def test_update_item_not_found(mock_table):
    from update_market_item import lambda_handler

    event = {
        "pathParameters": {"item_id": "999"},
        "body": json.dumps({"name": "Feijão"}),
    }

    # Mock do retorno do query para simular item não encontrado
    mock_table.query.return_value = {"Items": []}

    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 404
    assert body["success"] is False
    assert "Item não encontrado" in body["message"]


def test_update_no_fields(mock_table):
    from update_market_item import lambda_handler

    event = {"pathParameters": {"item_id": "123"}, "body": json.dumps({})}
    mock_table.query.return_value = {
        "Items": [
            {
                "PK": "LIST#20250530",
                "SK": "ITEM#123",
                "name": "Feijão",
                "status": "TODO",
                "date": "2025-05-30",
            }
        ]
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert body["success"] is False
    assert "Nenhum campo válido para atualização" in body["message"]


def test_update_exception(mock_table):
    from update_market_item import lambda_handler

    event = {
        "pathParameters": {"item_id": "123"},
        "body": json.dumps({"name": "Arroz"}),
    }

    # Simula uma exceção no DynamoDB
    mock_table.query.side_effect = Exception("DB error")

    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert body["success"] is False
    assert "Erro interno" in body["message"]
