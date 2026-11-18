from abc import ABC, abstractmethod

class DataProvider(ABC):
    """
    Architettura astratta per l'importazione di dati.
    Ogni provider (es. Fantacalcio, CSV manuale, SofaScore) deve implementare questi metodi.
    """
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        pass

    @abstractmethod
    def get_players(self, season: str):
        """Ritorna la lista dei giocatori per la stagione."""
        pass

    @abstractmethod
    def get_matches(self, season: str):
        """Ritorna il calendario e i risultati della stagione."""
        pass

    @abstractmethod
    def get_player_stats(self, season: str):
        """Ritorna le statistiche stagionali aggregate."""
        pass

    @abstractmethod
    def get_lineups(self, season: str):
        """Ritorna i dati tattici, presenze e sostituzioni match per match."""
        pass