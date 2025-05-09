package com.example;


import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.model.AttributeValue;
import com.amazonaws.services.dynamodbv2.model.PutItemRequest;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class FuncaoDoisHandler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    private final AmazonDynamoDB dynamoDbClient;
    private final ObjectMapper objectMapper;
    private final String tableName;

    public FuncaoDoisHandler() {
        this.dynamoDbClient = AmazonDynamoDBClientBuilder.standard().build();
        this.objectMapper = new ObjectMapper();
        this.tableName = System.getenv("DYNAMODB_TABLE_NAME");
    }

    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent input, Context context) {
        context.getLogger().log("Processando requisição para adicionar item à lista de mercado");
        APIGatewayProxyResponseEvent response = new APIGatewayProxyResponseEvent();

        try {
          
            MarketItem item = objectMapper.readValue(input.getBody(), MarketItem.class);

            if (item.getName() == null || item.getName().trim().isEmpty()) {
                return createErrorResponse(400, "O nome do item é obrigatório");
            }

            String itemId = UUID.randomUUID().toString();

            // Gera chave de partição baseada na data atual (YYYYMMDD)
            String pk = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));

            // Cria mapa de atributos para o DynamoDB
            Map<String, AttributeValue> itemAttributes = new HashMap<>();
            itemAttributes.put("PK", new AttributeValue(pk));
            itemAttributes.put("itemId", new AttributeValue(itemId));
            itemAttributes.put("name", new AttributeValue(item.getName()));
            itemAttributes.put("date", new AttributeValue(LocalDate.now().toString()));
            itemAttributes.put("status", new AttributeValue("todo"));

            // Salva no DynamoDB
            PutItemRequest putItemRequest = new PutItemRequest()
                    .withTableName(tableName)
                    .withItem(itemAttributes);

            context.getLogger().log("Salvando item no DynamoDB: " + pk + " - " + itemId);
            dynamoDbClient.putItem(putItemRequest);

            // Cria objeto de resposta
            Map<String, Object> responseBody = new HashMap<>();
            responseBody.put("success", true);
            responseBody.put("message", "Item adicionado com sucesso à lista de mercado");
            responseBody.put("item", Map.of(
                    "pk", pk,
                    "itemId", itemId,
                    "name", item.getName(),
                    "date", LocalDate.now().toString(),
                    "status", "todo"
            ));

            context.getLogger().log("Resposta: " + objectMapper
                    .writerWithDefaultPrettyPrinter()
                    .writeValueAsString(responseBody));

            // Retorna resposta
            response.setStatusCode(201); // Created
            response.setBody(objectMapper.writeValueAsString(responseBody));
            response.setHeaders(Map.of("Content-Type", "application/json"));

            context.getLogger().log("Item adicionado com sucesso: " + itemId);
            return response;

        } catch (Exception e) {
            context.getLogger().log("Erro ao processar a solicitação: " + e.getMessage());
            return createErrorResponse(500, "Erro ao processar a solicitação: " + e.getMessage());
        }
    }

    private APIGatewayProxyResponseEvent createErrorResponse(int statusCode, String message) {
        APIGatewayProxyResponseEvent response = new APIGatewayProxyResponseEvent();
        try {
            Map<String, Object> errorBody = Map.of(
                    "success", false,
                    "message", message
            );
            response.setStatusCode(statusCode);
            response.setBody(objectMapper.writeValueAsString(errorBody));
            response.setHeaders(Map.of("Content-Type", "application/json"));
        } catch (Exception e) {
            response.setStatusCode(500);
            response.setBody("{\"success\":false,\"message\":\"Erro interno\"}");
        }
        return response;
    }


     // Classe para deserializar JSON

    public static class MarketItem {
        private String name;

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }
    }
}
