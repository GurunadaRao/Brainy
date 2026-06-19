# API Design Template

- **Service Name**: [e.g., Ingestion API]
- **Protocol**: [REST / gRPC / WebSockets]

## 1. Endpoints Overview
List routes and operations.

### Endpoints
#### `POST /v1/ingest`
- **Description**: Trigger video ingestion.
- **Request Body**:
```json
{
  "url": "string"
}
```
- **Response Headers & Body (202 Accepted)**:
```json
{
  "task_id": "string",
  "status": "queued"
}
```

## 2. Error Responses
Define status codes and error payloads (e.g., 400 Bad Request, 422 Validation Error).
