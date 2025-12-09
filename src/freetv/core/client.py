"""
Freebox API Client Wrapper.
"""
from typing import Optional, Dict

from freebox_api import Freepybox
from rich.console import Console
from rich.panel import Panel
from rich import box

from ..config import FREEBOX_HOST, FREEBOX_PORT
from ..models import PlayerStatus, VolumeState

console = Console()

class FreeboxClient:
    """Wrapper pour l'API Freebox."""
    
    def __init__(self, host: str = FREEBOX_HOST, port: str = FREEBOX_PORT):
        self.host = host
        self.port = port
        self.fbx: Optional[Freepybox] = None
        self._last_player_status: Optional[PlayerStatus] = None

    async def connect(self) -> None:
        """Connecte à la Freebox."""
        self.fbx = Freepybox(api_version="v4")
        await self.fbx.open(self.host, port=self.port)
        await self._check_permissions()
    
    async def disconnect(self) -> None:
        """Déconnecte de la Freebox."""
        if self.fbx:
            await self.fbx.close()

    async def _check_permissions(self) -> None:
        """Vérifie les permissions."""
        if not hasattr(self.fbx, '_access') or not self.fbx._access:
            console.print("[yellow]⚠️  Impossible de vérifier les permissions[/yellow]")
            return
        
        perms = await self.fbx._access.get_permissions()
        if not perms:
            console.print("[yellow]⚠️  Impossible de récupérer les permissions[/yellow]")
            return
        
        if not perms.get('player', False):
            self._print_permission_error()
            raise PermissionError("Permission 'Contrôle du Freebox Player' manquante.")

    def _print_permission_error(self):
        console.print()
        console.print(Panel(
            "[bold red]⚠️  PERMISSION MANQUANTE[/bold red]\n\n"
            "L'application n'a pas la permission [yellow]'Contrôle du Freebox Player'[/yellow].\n\n"
            "[bold]📋 SOLUTION :[/bold]\n\n"
            "1. Ouvrez votre navigateur : [cyan]http://192.168.1.254[/cyan]\n"
            "   (ou http://mafreebox.freebox.fr)\n\n"
            "2. Connectez-vous avec votre mot de passe Freebox\n\n"
            "3. Allez dans :\n"
            "   • Paramètres de la Freebox\n"
            "   • Gestion des accès\n"
            "   • Onglet 'Applications'\n\n"
            "4. Trouvez l'application [cyan]'Freepybox'[/cyan] et activez :\n"
            "   [green]✅ Contrôle du Freebox Player[/green]\n\n"
            "5. Sauvegardez et relancez l'application\n\n"
            "[dim]💡 Ou utilisez l'assistant : [cyan]./setup.sh[/cyan][/dim]",
            title="[bold]Configuration requise[/bold]",
            border_style="red",
            box=box.DOUBLE
        ))
        console.print()

    async def get_player_status(self) -> Optional[PlayerStatus]:
        """Récupère le statut du lecteur."""
        try:
            status_data = await self.fbx.player.get_player_status()
            self._last_player_status = PlayerStatus.from_api_response(status_data)
            return self._last_player_status
        except Exception as e:
            console.print(f"[red]❌ Erreur statut: {e}[/red]")
            return None

    async def get_volume_state(self) -> Optional[VolumeState]:
        """Récupère l'état du volume."""
        try:
            volume_data = await self.fbx.player.get_player_volume()
            return VolumeState(
                mute=volume_data.get('mute', False),
                volume=volume_data.get('volume', 0)
            )
        except Exception as e:
            console.print(f"[red]❌ Erreur volume: {e}[/red]")
            return None
    
    async def set_mute(self, mute: bool) -> bool:
        """Active/désactive le mute."""
        try:
            await self.fbx.player.set_player_volume({"mute": mute})
            return True
        except Exception as e:
            console.print(f"[red]❌ Erreur mute: {e}[/red]")
            return False
