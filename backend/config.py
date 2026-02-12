import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Settings:
    """
    Application-wide settings loaded from environment variables.
    """
    # Project Information
    PROJECT_NAME: str = "CyberSentinel"
    PROJECT_VERSION: str = "1.0.0"

    # Database Configuration (PostgreSQL)
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "cybersentinel")
    DATABASE_URL: str = (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

    # API Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS (Cross-Origin Resource Sharing)
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(',')

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    # Tool paths (assuming they are in the system's PATH)
    NMAP_PATH: str = os.getenv("NMAP_PATH", "nmap")
    SSLSCAN_PATH: str = os.getenv("SSLSCAN_PATH", "sslscan")
    NIKTO_PATH: str = os.getenv("NIKTO_PATH", "nikto")
    WHOIS_PATH: str = os.getenv("WHOIS_PATH", "whois")
    DIG_PATH: str = os.getenv("DIG_PATH", "dig")
    NSLOOKUP_PATH: str = os.getenv("NSLOOKUP_PATH", "nslookup")
    DIRSEARCH_PATH: str = os.getenv("DIRSEARCH_PATH", "dirsearch")
    GOBUSTER_PATH: str = os.getenv("GOBUSTER_PATH", "gobuster")

settings = Settings()
