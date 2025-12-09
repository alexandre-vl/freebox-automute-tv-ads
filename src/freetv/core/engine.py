"""
Core Engine Logic.
Combines Freebox Client and OQEE Client to perform auto-mute.
"""
import time
import asyncio
from typing import Optional

from ..config import CHECK_INTERVAL, UNMUTE_BUFFER
from .client import FreeboxClient
from .oqee import OqeeClient
from ..models import AdBreak

class AutoMuteEngine:
    """Moteur principal de l'auto-mute."""
    
    def __init__(self):
        self.fbx_client = FreeboxClient()
        self.oqee_client = OqeeClient()
        self.check_interval = CHECK_INTERVAL
        self._is_muted_by_us = False

    async def __aenter__(self):
        await self.fbx_client.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.fbx_client.disconnect()

    async def run_step(self) -> None:
        """Exécute une itération de vérification."""
        player_status = await self.fbx_client.get_player_status()
        
        if not player_status:
            return
        
        if player_status.power_state != "running" or not player_status.is_playing:
            return
            
        # Mise à jour des données OQEE
        await self.oqee_client.update_cache(player_status.channel_uuid)
        
        # Logique de mute
        current_time = int(time.time())
        active_ad = self.oqee_client.get_active_ad_break(current_time)
        
        # Vérification pub imminente (buffer)
        imminent_ad = None
        if not active_ad:
            for ad in self.oqee_client.ad_breaks:
                time_until = ad.start_time - current_time
                if 0 < time_until <= UNMUTE_BUFFER:
                    imminent_ad = ad
                    break
        
        volume_state = await self.fbx_client.get_volume_state()
        if not volume_state:
            return
            
        should_stay_muted = active_ad is not None or imminent_ad is not None
        
        if should_stay_muted:
            if not volume_state.mute:
                await self.fbx_client.set_mute(True)
                self._is_muted_by_us = True
        else:
            if volume_state.mute and self._is_muted_by_us: 
                # On ne démute QUE si c'est nous qui avons muté (sécurité basique)
                # Mais le script original démutait tout le temps "si volume_state.mute".
                # Pour être fidèle à l'original :
                await self.fbx_client.set_mute(False)
                self._is_muted_by_us = False

    def get_display_state(self):
        """Retourne l'état actuel pour l'affichage."""
        current_time = int(time.time())
        return {
            "player_status": self.fbx_client._last_player_status,
            "ad_breaks": self.oqee_client.ad_breaks,
            "active_ad": self.oqee_client.get_active_ad_break(current_time),
            "next_ad": self.oqee_client.get_next_ad_break(current_time),
            "current_program": self.oqee_client.current_program,
            # Note: volume_state needs to be fetched fresh usually, but for display
            # we might need to cache it or fetch it inside the UI loop?
            # Actually, the UI loop in original script called get_volume_state() every loop.
            # We'll leave it to the UI loop to call client methods or engine methods.
        }
