"""
OQEE API Client and Logic.
"""
import time
import aiohttp
from typing import List, Optional
from rich.console import Console

from ..models import AdBreak, TVProgram
from ..config import CHANNEL_MAPPING, AD_BREAKS_CACHE_TTL, AD_MERGE_MAX_GAP

console = Console()

class OqeeClient:
    """Client pour l'API OQEE (Pubs et EPG)."""
    
    def __init__(self, channel_mapping: dict = CHANNEL_MAPPING):
        self.channel_mapping = channel_mapping
        
        # Caches
        self._ad_breaks: List[AdBreak] = []
        self._ad_breaks_last_fetch: float = 0
        self._current_channel_id: Optional[str] = None
        self._all_ads_passed_notified: bool = False
        self._first_run: bool = True
        
        self._current_program: Optional[TVProgram] = None
        self._current_program_last_fetch: float = 0
        self._program_channel_uuid: Optional[str] = None
        
        self.ad_cache_ttl = AD_BREAKS_CACHE_TTL
        self._program_cache_ttl = 30

    async def fetch_ad_breaks(self, channel_id: str) -> List[AdBreak]:
        """Récupère les périodes de publicité."""
        url = f"https://api.oqee.net/api/v1/live/anti_adskipping/{channel_id}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return []
                    
                    data = await response.json()
                    if not data.get('success'):
                        return []
                    
                    periods = data.get('result', {}).get('periods', [])
                    ad_breaks = []
                    
                    for period in periods:
                        if period.get('type') == 'ad_break':
                            start_time = period.get('start_time')
                            # Si end_time manque, on estime à +5 min
                            end_time = period.get('end_time', start_time + 300)
                            
                            if start_time:
                                ad_breaks.append(AdBreak(start_time=start_time, end_time=end_time))
                    return ad_breaks
        except Exception as e:
            console.print(f"[red]❌ Erreur API OQEE: {e}[/red]")
            return []

    async def fetch_current_program(self, channel_id: str) -> Optional[TVProgram]:
        """Récupère le programme TV actuel."""
        current_time = int(time.time())
        # Alignement sur 6h pour l'API
        start_timestamp = (current_time // 21600) * 21600
        
        url = f"https://api.oqee.net/api/v1/epg/by_channel/{channel_id}/{start_timestamp}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    if not data.get('success'):
                        return None
                    
                    entries = data.get('result', {}).get('entries', [])
                    for entry in entries:
                        if entry.get('type') == 'live':
                            live_data = entry.get('live', {})
                            start = live_data.get('start', 0)
                            end = live_data.get('end', 0)
                            
                            if start <= current_time <= end:
                                duration = end - start
                                return TVProgram(
                                    title=live_data.get('title', 'Programme inconnu'),
                                    category=live_data.get('category', ''),
                                    sub_category=live_data.get('sub_category', ''),
                                    start_time=start,
                                    end_time=end,
                                    duration_seconds=duration if duration > 0 else live_data.get('duration_seconds', 0),
                                    description=live_data.get('description', '')
                                )
                    return None
        except Exception as e:
            console.print(f"[dim red]⚠️  Erreur API EPG: {e}[/dim red]")
            return None

    def _merge_close_ad_breaks(self, ad_breaks: List[AdBreak], max_gap: int = AD_MERGE_MAX_GAP) -> List[AdBreak]:
        """Fusionne les ad_breaks proches."""
        if not ad_breaks:
            return []
        
        sorted_ads = sorted(ad_breaks, key=lambda x: x.start_time)
        merged = []
        current = sorted_ads[0]
        
        for next_ad in sorted_ads[1:]:
            gap = next_ad.start_time - current.end_time
            if gap <= max_gap:
                current = AdBreak(
                    start_time=current.start_time,
                    end_time=max(current.end_time, next_ad.end_time)
                )
            else:
                merged.append(current)
                current = next_ad
        
        merged.append(current)
        return merged

    async def update_cache(self, channel_uuid: str):
        """Met à jour les caches (pubs et programme)."""
        current_time = time.time()
        
        # 1. Update Ad Breaks
        if self._current_channel_id != channel_uuid:
            self._all_ads_passed_notified = False
        
        future_ads_count = sum(1 for ad in self._ad_breaks if ad.start_time > current_time)
        all_ads_passed = len(self._ad_breaks) > 0 and future_ads_count == 0
        
        if future_ads_count > 0:
            self._all_ads_passed_notified = False # Reset if new ads appear
            
        need_ad_refresh = (
            self._first_run or
            not self._ad_breaks or
            self._current_channel_id != channel_uuid or
            (current_time - self._ad_breaks_last_fetch) > self.ad_cache_ttl or
            (all_ads_passed and not self._all_ads_passed_notified)
        )
        
        channel_id = self.channel_mapping.get(channel_uuid)
        
        if need_ad_refresh:
            if channel_id:
                raw_ads = await self.fetch_ad_breaks(channel_id)
                self._ad_breaks = self._merge_close_ad_breaks(raw_ads, max_gap=AD_MERGE_MAX_GAP)
                self._ad_breaks_last_fetch = current_time
                self._current_channel_id = channel_uuid
                self._first_run = False
            else:
                self._ad_breaks = []

        # 2. Update Program
        need_prog_refresh = (
            not self._current_program or
            self._program_channel_uuid != channel_uuid or
            (current_time - self._current_program_last_fetch) > self._program_cache_ttl
        )
        
        if need_prog_refresh:
            self._program_channel_uuid = channel_uuid
            if channel_id:
                self._current_program = await self.fetch_current_program(channel_id)
                self._current_program_last_fetch = current_time
            else:
                self._current_program = None

    def get_active_ad_break(self, current_time: int) -> Optional[AdBreak]:
        for ad in self._ad_breaks:
            if ad.is_active(current_time):
                return ad
        return None
    
    def get_next_ad_break(self, current_time: int) -> Optional[AdBreak]:
        future_ads = [ad for ad in self._ad_breaks if ad.start_time > current_time]
        if future_ads:
            return min(future_ads, key=lambda ad: ad.start_time)
        return None

    @property
    def ad_breaks(self) -> List[AdBreak]:
        return self._ad_breaks
    
    @property
    def current_program(self) -> Optional[TVProgram]:
        return self._current_program
