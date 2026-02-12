# CyberSentinel API Documentation

This document provides a summary of the CyberSentinel REST API endpoints. For a fully interactive API documentation, run the backend server and visit `/docs`.

---

## Base URL

`/api`

---

## Authentication

Currently, the API is open for internal use. Future versions will implement OAuth2 for user authentication and authorization.

---

## Scan Endpoints

### `POST /scan/`

Start a new scan.

-   **Description**: Initiates a new scan for a given target. The request returns immediately with a `202-Accepted` status, and the scan is processed in the background.
-   **Body**:
    ```json
    {
      "target": "string",
      "scan_mode": "string (defensive|offensive)",
      "scan_depth": "string (normal|deep)"
    }
    ```
-   **Headers**:
    -   `X-Legal-Accepted: true`: **Required** if `scan_mode` is `offensive`.
-   **Success Response**: `202 Accepted`
    -   Body: `ScanRead` object with the initial scan details and a status of "queued".
-   **Error Responses**:
    -   `400 Bad Request`: If the target is invalid or a pipeline cannot be generated.
    -   `403 Forbidden`: If `scan_mode` is `offensive` and the `X-Legal-Accepted` header is not provided or is not `true`.

### `GET /scan/`

Retrieve a list of all scans.

-   **Description**: Returns a list of all historical and in-progress scans.
-   **Query Parameters**: `skip` (int, default: 0), `limit` (int, default: 100).
-   **Success Response**: `200 OK`
    -   Body: An array of `ScanRead` objects.

### `GET /scan/{scan_id}`

Retrieve details for a specific scan.

-   **Description**: Returns the full details for a single scan, including its results once completed.
-   **Path Parameters**: `scan_id` (string).
-   **Success Response**: `200 OK`
    -   Body: A `ScanReadWithResults` object.
-   **Error Response**: `404 Not Found`.

### `WS /scan/ws/{scan_id}`

WebSocket endpoint for live scan output.

-   **Description**: Establishes a WebSocket connection to stream real-time output from a running scan.
-   **Path Parameters**: `scan_id` (string).
-   **Messages**: The server will push string messages containing the live output from the tools as they run.

---

## Reports Endpoints

### `GET /reports/`

Retrieve a list of all reports.

-   **Description**: Returns metadata for all generated reports.
-   **Success Response**: `200 OK`
    -   Body: An array of `ReportRead` objects.

### `GET /reports/scan/{scan_id}`

Retrieve reports for a specific scan.

-   **Success Response**: `200 OK`
    -   Body: An array of `ReportRead` objects.
-   **Error Response**: `404 Not Found`.

### `GET /reports/{report_id}/download`

Download a specific report file.

-   **Description**: Downloads the raw report file (PDF or JSON).
-   **Path Parameters**: `report_id` (integer).
-   **Success Response**: `200 OK`
    -   Body: The raw file content (`application/pdf` or `application/json`).
-   **Error Response**: `404 Not Found`.

---

## Tools & System Endpoints

### `GET /tools/`

Get a list of available tools.

-   **Success Response**: `200 OK`
    -   Body: `["nmap_scan", "ssl_scan", ...]`

### `GET /tools/{tool_name}`

Get details for a specific tool.

-   **Success Response**: `200 OK`
-   **Error Response**: `404 Not Found`.

### `GET /tools/legal/disclaimer`

Get the legal disclaimer text.

-   **Success Response**: `200 OK`
    -   Body: `{ "disclaimer": "..." }`

### `GET /tools/monitoring/resources`

Get system resource metrics.

-   **Success Response**: `200 OK`
    -   Body: A JSON object with CPU, memory, and disk usage.
