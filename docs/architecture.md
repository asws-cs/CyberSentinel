# CyberSentinel System Architecture

This document provides a detailed overview of the CyberSentinel platform's architecture, its components, and their interactions.

## High-Level Overview

CyberSentinel is a full-stack web application built with a service-oriented architecture. It consists of five primary, containerized services managed by Docker Compose:

1.  **Frontend**: A React-based single-page application that provides the user interface.
2.  **Backend (API)**: A FastAPI server that exposes a RESTful API for the frontend to interact with.
3.  **Worker**: A separate Python process that consumes tasks from a queue to run long-running security scans.
4.  **Database**: A PostgreSQL instance for persistent storage of scan data, results, and reports.
5.  **Cache/Queue**: A Redis instance that serves as both a message broker (task queue) and a real-time messaging system (pub/sub for live output).

![High-Level Architecture Diagram](https://via.placeholder.com/800x400.png?text=High-Level+Architecture+Diagram)
*(Placeholder for a proper diagram)*

---

## Backend Architecture

The backend is built using FastAPI and is organized into a modular structure to promote separation of concerns.

### Core Modules

-   **`main.py`**: The entry point for the API server and the worker process. It uses `typer` to provide a simple CLI for running either process.
-   **`api/`**: Contains the API routers. Each file corresponds to a different resource (e.g., `routes_scan.py`, `routes_reports.py`). These define the public-facing endpoints.
-   **`core/`**: The brain of the application.
    -   `target_parser.py`: Normalizes and enriches target information (URL, IP, domain).
    -   `decision_engine.py`: Selects which tools to run based on scan mode and depth.
    -   `risk_engine.py`: Calculates a risk score from a collection of scan results.
    -   `queue_manager.py`: Manages the Redis-backed task queue for scan jobs.
-   **`tools/`**: Handles the execution and output of security tools.
    -   `tool_controller.py`: Orchestrates the execution of a tool pipeline from the `DecisionEngine`.
    -   `subprocess_stream.py`: A utility for running external command-line tools and streaming their `stdout`/`stderr` asynchronously.
    -   `live_output.py`: A Redis Pub/Sub manager for broadcasting live tool output to any connected clients.
-   **`scanners/` & `offensive/`**: These modules contain the logic for individual security tools. Each file is a wrapper around a tool (e.g., `nmap_scanner.py`) or a specific test (e.g., `sql_tester.py`), responsible for running the tool and parsing its output into a structured format.
-   **`database/`**: Manages database connectivity and models.
    -   `db_connect.py`: Handles the async database engine and session management.
    -   `models.py` / `schemas.py`: Defines the data structure using `SQLModel`, serving as both database tables and Pydantic validation models.
-   **`security/`**: Implements security-related features.
    -   `legal_guard.py`: Enforces the ethical use policy for offensive scans.
    -   `rate_limiter.py`: Provides API rate limiting to prevent abuse.
-   **`monitoring/`**: Exposes system resource metrics.

## Data Flow: Starting a Scan

1.  **[Frontend]** User fills out the scan form and clicks "Start Scan".
2.  **[Frontend]** An API call is made to `POST /api/scan/` with the target and scan options. For offensive scans, the `X-Legal-Accepted` header is required.
3.  **[Backend API]** The `start_new_scan` endpoint in `routes_scan.py` receives the request.
4.  **[Backend API]** It uses `target_parser` to validate the target and `decision_engine` to build a tool pipeline.
5.  **[Backend API]** A new `Scan` record is created in the PostgreSQL database with a `status` of "queued".
6.  **[Backend API]** A task dictionary containing the scan ID and the pipeline is pushed to the `scan_queue` in Redis.
7.  **[Backend API]** A `202 Accepted` response is immediately returned to the frontend with the new scan's details.

## Data Flow: Processing a Scan

1.  **[Worker]** The worker process is constantly listening to the Redis `scan_queue`. It dequeues the task.
2.  **[Worker]** The worker updates the scan's status in the database to "in_progress".
3.  **[Worker]** It instantiates a `ToolController` for the scan.
4.  **[ToolController]** The controller iterates through the tool pipeline.
    -   For each tool, it calls the appropriate function from the `scanners/` or `offensive/` modules.
    -   If the tool is a command-line utility, `SubprocessStreamer` is used to execute it.
    -   As the tool produces output, `LiveOutputPublisher` broadcasts each line to a unique Redis channel (e.g., `scan_output:<scan_id>`).
5.  **[Frontend]** If the user is viewing the scan page, the `LiveConsole` component connects to the WebSocket endpoint (`/ws/scan/{scan_id}`).
6.  **[Backend API]** The WebSocket endpoint subscribes to the Redis channel for that scan and streams any messages directly to the client.
7.  **[Worker]** After all tools have run, the `ToolController` collects the structured results.
8.  **[Worker]** The `risk_engine` is used to calculate a final risk score.
9.  **[Worker]** The final results, risk score, and generated reports (PDF and JSON) are saved to the database.
10. **[Worker]** The scan's status is updated to "completed".

---

This decoupled architecture ensures that the API remains responsive while long, resource-intensive scans are handled independently in the background. The use of Redis as a message broker allows for easy scaling by simply running more worker containers.
