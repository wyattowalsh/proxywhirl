# API Contracts: Automated Reporting System

**Feature**: 010-automated-report  
**Date**: 2025-11-02  
**Status**: Complete

## Overview

This document defines REST API endpoints for the automated reporting system. All endpoints extend the existing FastAPI application from 003-rest-api feature. Endpoints follow RESTful conventions and include OpenAPI documentation.

---

## Base URL

```
/api/v1/reports
```

All endpoints are prefixed with `/api/v1/reports` to namespace reporting functionality.

---

## Endpoints

### 1. Generate On-Demand Report

**POST** `/api/v1/reports/generate`

Generate a report immediately with specified parameters.

**Request Body**:
```json
{
  "report_type": "performance",  // "performance" | "health" | "aggregate" | "custom"
  "format": "json",              // "json" | "csv" | "html" | "pdf"
  "time_range_start": "2025-11-01T00:00:00Z",  // ISO 8601 UTC
  "time_range_end": "2025-11-02T00:00:00Z",    // ISO 8601 UTC
  "template_id": "uuid-string",  // Optional: use template
  "filters": {                   // Optional: filter criteria
    "proxy_urls": ["http://proxy1.com:8080"],
    "sources": ["source1", "source2"]
  },
  "parameters": {                // Optional: additional params
    "include_charts": true
  }
}
```

**Response** (202 Accepted):
```json
{
  "report_id": "a1b2c3d4-uuid",
  "status": "generating",
  "estimated_completion_seconds": 5,
  "status_url": "/api/v1/reports/a1b2c3d4-uuid/status",
  "download_url": "/api/v1/reports/a1b2c3d4-uuid/download"
}
```

**Error Responses**:
- 400 Bad Request: Invalid time range or parameters
- 404 Not Found: Template not found (if template_id specified)
- 429 Too Many Requests: Concurrent generation limit reached
- 500 Internal Server Error: Generation failed

**Rate Limit**: 50 requests/minute per client

---

### 2. Get Report Status

**GET** `/api/v1/reports/{report_id}/status`

Check generation status of a report.

**Path Parameters**:
- `report_id`: Report UUID

**Response** (200 OK - Generating):
```json
{
  "report_id": "a1b2c3d4-uuid",
  "status": "generating",
  "progress_percent": 45,
  "started_at": "2025-11-02T09:30:00Z"
}
```

**Response** (200 OK - Completed):
```json
{
  "report_id": "a1b2c3d4-uuid",
  "status": "completed",
  "started_at": "2025-11-02T09:30:00Z",
  "completed_at": "2025-11-02T09:30:03Z",
  "generation_time_ms": 3245,
  "file_size_bytes": 524288,
  "download_url": "/api/v1/reports/a1b2c3d4-uuid/download"
}
```

**Response** (200 OK - Failed):
```json
{
  "report_id": "a1b2c3d4-uuid",
  "status": "failed",
  "started_at": "2025-11-02T09:30:00Z",
  "completed_at": "2025-11-02T09:30:01Z",
  "error_message": "Insufficient metrics data for time range"
}
```

**Error Responses**:
- 404 Not Found: Report ID not found

**Rate Limit**: 100 requests/minute per client

---

### 3. Download Report

**GET** `/api/v1/reports/{report_id}/download`

Download the generated report file.

**Path Parameters**:
- `report_id`: Report UUID

**Response** (200 OK):
- Content-Type: `application/json` | `text/csv` | `text/html` | `application/pdf`
- Content-Disposition: `attachment; filename="report_{timestamp}.{ext}"`
- Body: Report file content

**Error Responses**:
- 404 Not Found: Report ID not found or report failed
- 409 Conflict: Report still generating (not ready)
- 410 Gone: Report file deleted (retention period expired)

**Rate Limit**: 100 requests/minute per client

---

### 4. List Reports

**GET** `/api/v1/reports`

List all reports with optional filtering.

**Query Parameters**:
- `status`: Filter by status (`generating` | `completed` | `failed`)
- `report_type`: Filter by type (`performance` | `health` | `aggregate` | `custom`)
- `format`: Filter by format (`json` | `csv` | `html` | `pdf`)
- `start_date`: Filter by generation date (ISO 8601)
- `end_date`: Filter by generation date (ISO 8601)
- `limit`: Max results (default 50, max 500)
- `offset`: Pagination offset (default 0)

**Response** (200 OK):
```json
{
  "reports": [
    {
      "report_id": "a1b2c3d4-uuid",
      "name": "Performance Report 2025-11-02",
      "report_type": "performance",
      "format": "json",
      "status": "completed",
      "generated_at": "2025-11-02T09:30:03Z",
      "file_size_bytes": 524288,
      "download_url": "/api/v1/reports/a1b2c3d4-uuid/download"
    }
  ],
  "total": 123,
  "limit": 50,
  "offset": 0
}
```

**Rate Limit**: 100 requests/minute per client

---

### 5. Delete Report

**DELETE** `/api/v1/reports/{report_id}`

Delete a report and its associated file.

**Path Parameters**:
- `report_id`: Report UUID

**Response** (204 No Content): Report deleted successfully

**Error Responses**:
- 404 Not Found: Report ID not found
- 409 Conflict: Cannot delete system-generated report

**Rate Limit**: 100 requests/minute per client

---

## Report Templates

### 6. Create Template

**POST** `/api/v1/reports/templates`

Create a new custom report template.

**Request Body**:
```json
{
  "name": "daily-performance-summary",
  "description": "Daily summary of proxy performance metrics",
  "report_type": "performance",
  "metrics": ["requests_total", "success_rate", "avg_response_time"],
  "filters": {
    "sources": ["source1", "source2"]
  },
  "thresholds": {
    "success_rate": 95.0,
    "avg_response_time": 500
  },
  "output_format": "json"
}
```

**Response** (201 Created):
```json
{
  "template_id": "t1t2t3t4-uuid",
  "name": "daily-performance-summary",
  "description": "Daily summary of proxy performance metrics",
  "created_at": "2025-11-02T09:30:00Z"
}
```

**Error Responses**:
- 400 Bad Request: Invalid template (metric doesn't exist, invalid name format)
- 409 Conflict: Template name already exists

**Rate Limit**: 20 requests/minute per client

---

### 7. List Templates

**GET** `/api/v1/reports/templates`

List all available report templates (system + user).

**Query Parameters**:
- `report_type`: Filter by type
- `include_system`: Include system templates (default true)
- `include_user`: Include user templates (default true)

**Response** (200 OK):
```json
{
  "templates": [
    {
      "template_id": "t1t2t3t4-uuid",
      "name": "daily-performance-summary",
      "description": "Daily summary of proxy performance metrics",
      "report_type": "performance",
      "is_system": false,
      "created_at": "2025-11-02T09:30:00Z"
    }
  ],
  "total": 8
}
```

**Rate Limit**: 100 requests/minute per client

---

### 8. Get Template

**GET** `/api/v1/reports/templates/{template_id}`

Get detailed template configuration.

**Path Parameters**:
- `template_id`: Template UUID or name (slug)

**Response** (200 OK):
```json
{
  "template_id": "t1t2t3t4-uuid",
  "name": "daily-performance-summary",
  "description": "Daily summary of proxy performance metrics",
  "report_type": "performance",
  "metrics": ["requests_total", "success_rate", "avg_response_time"],
  "filters": {"sources": ["source1"]},
  "thresholds": {"success_rate": 95.0},
  "output_format": "json",
  "is_system": false,
  "created_at": "2025-11-02T09:30:00Z",
  "updated_at": "2025-11-02T09:30:00Z"
}
```

**Error Responses**:
- 404 Not Found: Template not found

**Rate Limit**: 100 requests/minute per client

---

### 9. Update Template

**PUT** `/api/v1/reports/templates/{template_id}`

Update an existing custom template (system templates cannot be modified).

**Path Parameters**:
- `template_id`: Template UUID

**Request Body**: Same as Create Template

**Response** (200 OK): Updated template object

**Error Responses**:
- 400 Bad Request: Invalid template
- 403 Forbidden: Cannot modify system template
- 404 Not Found: Template not found

**Rate Limit**: 20 requests/minute per client

---

### 10. Delete Template

**DELETE** `/api/v1/reports/templates/{template_id}`

Delete a custom template (system templates cannot be deleted).

**Path Parameters**:
- `template_id`: Template UUID

**Response** (204 No Content): Template deleted

**Error Responses**:
- 403 Forbidden: Cannot delete system template
- 404 Not Found: Template not found
- 409 Conflict: Template is used by active schedules

**Rate Limit**: 20 requests/minute per client

---

## Report Schedules

### 11. Create Schedule

**POST** `/api/v1/reports/schedules`

Create a new scheduled report.

**Request Body**:
```json
{
  "name": "Daily Performance Report",
  "description": "Automated daily report at 9 AM",
  "template_id": "t1t2t3t4-uuid",
  "cron_expression": "0 9 * * *",
  "time_range_spec": "yesterday",
  "output_directory": "/reports/scheduled/daily",
  "enabled": true,
  "max_retries": 3,
  "retry_delay_seconds": 300
}
```

**Response** (201 Created):
```json
{
  "schedule_id": "s1s2s3s4-uuid",
  "name": "Daily Performance Report",
  "next_run_at": "2025-11-03T09:00:00Z",
  "created_at": "2025-11-02T09:30:00Z"
}
```

**Error Responses**:
- 400 Bad Request: Invalid cron expression or output directory
- 404 Not Found: Template not found

**Rate Limit**: 10 requests/minute per client

---

### 12. List Schedules

**GET** `/api/v1/reports/schedules`

List all report schedules.

**Query Parameters**:
- `enabled`: Filter by enabled status (true | false)
- `template_id`: Filter by template

**Response** (200 OK):
```json
{
  "schedules": [
    {
      "schedule_id": "s1s2s3s4-uuid",
      "name": "Daily Performance Report",
      "template_id": "t1t2t3t4-uuid",
      "cron_expression": "0 9 * * *",
      "enabled": true,
      "last_run_at": "2025-11-02T09:00:00Z",
      "next_run_at": "2025-11-03T09:00:00Z",
      "run_count": 15,
      "failure_count": 0
    }
  ],
  "total": 5
}
```

**Rate Limit**: 100 requests/minute per client

---

### 13. Get Schedule

**GET** `/api/v1/reports/schedules/{schedule_id}`

Get detailed schedule configuration and execution history.

**Path Parameters**:
- `schedule_id`: Schedule UUID

**Response** (200 OK):
```json
{
  "schedule_id": "s1s2s3s4-uuid",
  "name": "Daily Performance Report",
  "description": "Automated daily report at 9 AM",
  "template_id": "t1t2t3t4-uuid",
  "cron_expression": "0 9 * * *",
  "time_range_spec": "yesterday",
  "output_directory": "/reports/scheduled/daily",
  "enabled": true,
  "created_at": "2025-11-02T09:30:00Z",
  "last_run_at": "2025-11-02T09:00:00Z",
  "next_run_at": "2025-11-03T09:00:00Z",
  "run_count": 15,
  "failure_count": 0,
  "recent_runs": [
    {
      "report_id": "a1b2c3d4-uuid",
      "started_at": "2025-11-02T09:00:00Z",
      "completed_at": "2025-11-02T09:00:03Z",
      "status": "completed"
    }
  ]
}
```

**Error Responses**:
- 404 Not Found: Schedule not found

**Rate Limit**: 100 requests/minute per client

---

### 14. Update Schedule

**PUT** `/api/v1/reports/schedules/{schedule_id}`

Update an existing schedule.

**Path Parameters**:
- `schedule_id`: Schedule UUID

**Request Body**: Same as Create Schedule

**Response** (200 OK): Updated schedule object

**Error Responses**:
- 400 Bad Request: Invalid schedule
- 404 Not Found: Schedule not found

**Rate Limit**: 10 requests/minute per client

---

### 15. Delete Schedule

**DELETE** `/api/v1/reports/schedules/{schedule_id}`

Delete a report schedule (does not delete historical reports).

**Path Parameters**:
- `schedule_id`: Schedule UUID

**Response** (204 No Content): Schedule deleted

**Error Responses**:
- 404 Not Found: Schedule not found

**Rate Limit**: 10 requests/minute per client

---

### 16. Trigger Schedule Manually

**POST** `/api/v1/reports/schedules/{schedule_id}/trigger`

Manually trigger a scheduled report (does not affect schedule timing).

**Path Parameters**:
- `schedule_id`: Schedule UUID

**Response** (202 Accepted):
```json
{
  "report_id": "a1b2c3d4-uuid",
  "status": "generating",
  "status_url": "/api/v1/reports/a1b2c3d4-uuid/status"
}
```

**Error Responses**:
- 404 Not Found: Schedule not found
- 409 Conflict: Schedule is disabled

**Rate Limit**: 10 requests/minute per client

---

## Available Metrics

### 17. List Available Metrics

**GET** `/api/v1/reports/metrics`

List all available metrics that can be included in reports.

**Response** (200 OK):
```json
{
  "metrics": [
    {
      "name": "requests_total",
      "description": "Total number of requests per proxy",
      "type": "counter",
      "unit": "requests"
    },
    {
      "name": "success_rate",
      "description": "Percentage of successful requests",
      "type": "gauge",
      "unit": "percent"
    },
    {
      "name": "avg_response_time",
      "description": "Average response time in milliseconds",
      "type": "gauge",
      "unit": "milliseconds"
    }
  ],
  "total": 15
}
```

**Rate Limit**: 100 requests/minute per client

---

## Error Response Format

All error responses follow this structure:

```json
{
  "error": {
    "code": "INVALID_TIME_RANGE",
    "message": "End time must be after start time",
    "details": {
      "start_time": "2025-11-02T00:00:00Z",
      "end_time": "2025-11-01T00:00:00Z"
    }
  }
}
```

**Common Error Codes**:
- `INVALID_TIME_RANGE`: Time range validation failed
- `TEMPLATE_NOT_FOUND`: Referenced template doesn't exist
- `METRIC_NOT_FOUND`: Referenced metric doesn't exist
- `GENERATION_LIMIT_REACHED`: Concurrent generation limit exceeded
- `INVALID_CRON_EXPRESSION`: Cron syntax error
- `DIRECTORY_NOT_WRITABLE`: Output directory cannot be written to
- `SYSTEM_TEMPLATE_PROTECTED`: Cannot modify/delete system templates

---

## Authentication

All endpoints use the existing API authentication from 003-rest-api feature:

- **API Key Header**: `X-API-Key: <key>` (if PROXYWHIRL_REQUIRE_AUTH=true)
- **Optional**: Bearer token support for future OAuth integration

---

## Rate Limiting

Rate limits apply per client IP address using slowapi middleware:

| Endpoint Group | Rate Limit |
|---------------|------------|
| Report Generation | 50 req/min |
| Report Download | 100 req/min |
| Template Management | 20 req/min (write), 100 req/min (read) |
| Schedule Management | 10 req/min (write), 100 req/min (read) |
| Status/List | 100 req/min |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1698922800
```

---

## OpenAPI Specification

All endpoints automatically documented at `/docs` (Swagger UI) and `/redoc` (ReDoc).

**Example Tags**:
- `Reports` - Report generation and retrieval
- `Templates` - Template management
- `Schedules` - Scheduled report management
- `Metrics` - Available metrics

---

## Pagination

List endpoints support cursor-based pagination:

**Request**:
```
GET /api/v1/reports?limit=50&offset=100
```

**Response**:
```json
{
  "reports": [...],
  "total": 523,
  "limit": 50,
  "offset": 100,
  "has_more": true,
  "next_url": "/api/v1/reports?limit=50&offset=150"
}
```

---

## Webhooks (Future)

Reserved endpoint for webhook configuration:

**POST** `/api/v1/reports/webhooks` - Configure webhook for report completion events

---

## Summary

- **Total Endpoints**: 17 (16 implemented + 1 reserved)
- **REST Compliance**: Full CRUD for templates and schedules
- **Async Support**: 202 Accepted for long-running operations
- **Standard HTTP Codes**: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 404 Not Found, 409 Conflict, 429 Too Many Requests
- **Rate Limiting**: Per-endpoint limits with header feedback
- **Documentation**: Auto-generated OpenAPI/Swagger
