import os


class Settings:
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "codellama")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "./data/greenlinter.db")

    # Carbon intensity API configuration
    CARBON_INTENSITY_LOCATION: str = os.getenv("CARBON_INTENSITY_LOCATION", "EU")
    ELECTRICITY_MAPS_API_KEY: str = os.getenv("ELECTRICITY_MAPS_API_KEY", "")

    # Energy estimation defaults
    CO2_PER_KWH: float = 0.385  # kg CO2 per kWh (fallback, overridden by live API)
    COST_PER_KWH: float = 0.25  # EUR per kWh (cloud compute rate)
    ASSUMED_RUNS_PER_DAY: int = 1000


settings = Settings()
