"""
Data models for Freebox Auto-Mute.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class PlayerStatus:
    """État du lecteur Freebox."""
    power_state: str
    playback_state: str
    channel_uuid: str
    channel_number: int
    channel_name: str
    is_playing: bool
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'PlayerStatus':
        """Crée une instance depuis la réponse API."""
        player = data.get('player', {})
        foreground = data.get('foreground_app', {})
        context = foreground.get('context', {})
        channel = context.get('channel', {})
        player_state = player.get('state', {})
        
        return cls(
            power_state=data.get('power_state', 'unknown'),
            playback_state=player_state.get('playback_state', 'stopped'),
            channel_uuid=channel.get('channelUuid', ''),
            channel_number=channel.get('channelNumber', 0),
            channel_name=channel.get('channelName', ''),
            is_playing=player_state.get('playback_state') == 'playing'
        )


@dataclass
class AdBreak:
    """Période de publicité."""
    start_time: int  # Unix timestamp
    end_time: int    # Unix timestamp
    
    def is_active(self, current_time: int) -> bool:
        """Vérifie si la pub est active maintenant."""
        return self.start_time <= current_time <= self.end_time
    
    def duration_seconds(self) -> int:
        """Durée de la pub en secondes."""
        return self.end_time - self.start_time
    
    def time_until_start(self, current_time: int) -> int:
        """Secondes avant le début (négatif si déjà commencé)."""
        return self.start_time - current_time
    
    def time_until_end(self, current_time: int) -> int:
        """Secondes avant la fin (négatif si déjà fini)."""
        return self.end_time - current_time
    
    def __repr__(self) -> str:
        start = datetime.fromtimestamp(self.start_time).strftime('%H:%M:%S')
        end = datetime.fromtimestamp(self.end_time).strftime('%H:%M:%S')
        return f"AdBreak({start} -> {end})"


@dataclass
class VolumeState:
    """État du volume Freebox."""
    mute: bool
    volume: int


@dataclass
class TVProgram:
    """Programme TV actuel (EPG)."""
    title: str
    category: str
    sub_category: str
    start_time: int
    end_time: int
    duration_seconds: int
    description: str = ""
    
    def is_active(self, current_time: int) -> bool:
        """Vérifie si le programme est actif maintenant."""
        return self.start_time <= current_time <= self.end_time
    
    def time_remaining(self, current_time: int) -> int:
        """Secondes restantes du programme."""
        return max(0, self.end_time - current_time)
    
    def progress_percentage(self, current_time: int) -> float:
        """Pourcentage de progression (0-100)."""
        if self.duration_seconds == 0:
            return 0
        elapsed = current_time - self.start_time
        return min(100, max(0, (elapsed / self.duration_seconds) * 100))
