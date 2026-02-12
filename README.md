# CyberSentinel: Enterprise Cybersecurity Command Platform

CyberSentinel is a comprehensive, enterprise-grade cybersecurity command platform designed for both defensive scanning and controlled, ethical penetration testing. It provides a modular, scalable, and user-friendly web interface to orchestrate a variety of security tools, analyze the results, and generate detailed reports.

## Core Features

- **Dual-Mode System**: Switch between 'Defensive' and 'Offensive' scan profiles.
- **Intelligent Tool Orchestration**: An adaptive decision engine selects the right tools for the job based on the target and scan parameters.
- **Live Scan Output**: View real-time output from running security tools directly in the web UI.
- **Comprehensive Reporting**: Generate detailed PDF and JSON reports summarizing scan findings and risk assessments.
- **Risk Intelligence Engine**: A weighted scoring system calculates a quantifiable risk score for each target.
- **Interactive Dashboard**: A central dashboard provides at-a-glance system monitoring, recent activity, and data visualizations.
- **Ethical & Legal Enforcement**: A built-in legal guard requires user consent before running offensive tools.
- **Asynchronous & Scalable**: Built on a modern, asynchronous architecture using FastAPI, Redis, and a background worker system to handle concurrent scans.

## Tech Stack

- **Backend**: Python, FastAPI, SQLModel (Pydantic + SQLAlchemy), Redis, PostgreSQL
- **Frontend**: React, Vite, Material-UI, `react-query`, `chart.js`
- **Containerization**: Docker, Docker Compose
- **Core Tools**: Nmap, SSLScan, Nikto, Dirsearch, Gobuster, and more.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- A modern web browser

### Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd cybersentinel
    ```

2.  **Environment Variables:**
    Create a `.env` file in the project root by copying the example:
    ```bash
    cp .env.example .env
    ```
    Review and edit the `.env` file. At a minimum, you may want to set the `SECRET_KEY`.

3.  **Install External Tools:**
    The `scripts/install_tools.sh` script can be used to install the necessary command-line tools on a Debian-based system.
    ```bash
    chmod +x scripts/install_tools.sh
    ./scripts/install_tools.sh
    ```
    Alternatively, ensure that `nmap`, `sslscan`, `nikto`, `gobuster`, and `dirsearch` are in your system's PATH.

4.  **Build and Run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```

    This will:
    - Build the `backend`, `frontend`, and `worker` images.
    - Start the PostgreSQL database and Redis services.
    - Run the API server, the background worker, and the frontend development server.

5.  **Access the Application:**
    - **Frontend**: `http://localhost:3000`
    - **Backend API**: `http://localhost:8000/docs`

## Project Structure

The project is organized into a modular structure:

- `backend/`: The FastAPI application source code.
- `frontend/`: The React application source code.
- `scripts/`: Helper scripts for installation and environment setup.
- `docs/`: Project documentation.
- `docker-compose.yml`: Defines the services, networks, and volumes for the application.
- `Dockerfile`: Found in `backend/` and `frontend/` for building the respective images.

Refer to the `docs/architecture.md` file for a more detailed breakdown of the internal architecture.

## Legal Disclaimer

This tool is intended for educational purposes and for authorized security testing only. Running offensive scans against systems without explicit permission is illegal. The user is solely responsible for their actions. The authors of CyberSentinel are not responsible for any misuse or damage.
