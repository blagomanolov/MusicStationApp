from pathlib import Path

class Config:
    def __init__(self):
        self.database_path: Path = Path(__file__).resolve().parents[2] / "database" / "stations.db"
        self.station_api_url: str = "https://de1.api.radio-browser.info/json/stations"
        