# MES API Specification (Draft)

Base URL: `/api/v1`

## Manufacturing Orders

### POST /manufacturing-orders

Create a new manufacturing order.

- Request body:
  - `productId` (string, required)
  - `quantity` (number > 0, required)
  - `orderNumber` (string, required)
  - `dueDate` (string, ISO date, required)

- Response:
  - `201 Created`
  - Body:
    ```json
    {
      "success": true,
      "data": {
        "id": "uuid",
        "orderNumber": "MO-2026-0001",
        "status": "PLANNED"
      }
    }
    ```

### GET /manufacturing-orders/{id}

Get a manufacturing order with associated tasks.

- Response:
  - `200 OK`
  - `404 Not Found` if missing.

### GET /manufacturing-orders

List orders.

- Query parameters:
  - `status` (optional)
  - `limit` (optional)
  - `offset` (optional)

## Production Tasks

### GET /production-tasks

List production tasks with filters.

- Query parameters:
  - `status`
  - `workCenterId`
  - `orderId`

### PATCH /production-tasks/{id}/start

Mark a task as started.

### PATCH /production-tasks/{id}/complete

Complete a task and optionally add notes.

### PATCH /production-tasks/{id}/fail

Mark a task as failed with a reason.

## Work Centers

### POST /work-centers

Create a work center.

### GET /work-centers/{id}

Get work center details.

### PATCH /work-centers/{id}/status

Update status (AVAILABLE, BUSY, MAINTENANCE, DOWN).

## Quality

### POST /quality-inspections

Create a quality inspection for a task.

### PATCH /quality-inspections/{id}/pass

Mark inspection as passed.

### PATCH /quality-inspections/{id}/fail

Mark inspection as failed / requires rework.

(Extend this spec as endpoints are added.)
