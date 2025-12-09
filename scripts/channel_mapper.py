"""
Script interactif pour créer le mapping des chaînes Freebox -> OQEE.

Ce script :
1. Se connecte à la Freebox
2. Liste toutes les chaînes disponibles
3. Pour chaque chaîne, demande l'ID OQEE
4. Teste l'API OQEE pour valider
5. Sauvegarde le mapping dans un fichier
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Optional, Dict, List

import aiohttp
from freebox_api import Freepybox
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from rich.progress import track

console = Console()


class ChannelMapper:
    """Outil de mapping des chaînes."""
    
    def __init__(self):
        self.fbx: Optional[Freepybox] = None
        self.mappings: Dict[str, str] = {}
        self.channels_info: List[Dict] = []
        
    async def connect(self):
        """Connecte à la Freebox."""
        console.print("[cyan]📡 Connexion à la Freebox...[/cyan]")
        self.fbx = Freepybox(api_version="v4")
        await self.fbx.open("mafreebox.freebox.fr", port="443")
        console.print("[green]✅ Connecté ![/green]\n")
    
    async def disconnect(self):
        """Déconnecte de la Freebox."""
        if self.fbx:
            await self.fbx.close()
            console.print("\n[green]✅ Déconnecté de la Freebox[/green]")
    
    async def get_all_channels(self) -> List[Dict]:
        """
        Récupère toutes les chaînes disponibles.
        
        Returns:
            Liste des infos de chaînes
        """
        console.print("[cyan]📺 Récupération de la liste des chaînes...[/cyan]")
        
        try:
            # Récupérer le statut actuel pour avoir un exemple de structure
            status = await self.fbx.player.get_player_status()
            foreground = status.get('foreground_app', {})
            context = foreground.get('context', {})
            current_channel = context.get('channel', {})
            
            # Pour l'instant, on va utiliser la technique de parcourir les chaînes
            # en changeant de chaîne et en récupérant les infos
            console.print("[yellow]ℹ️  Mode interactif : on va parcourir les chaînes[/yellow]")
            
            return []  # On va le remplir de manière interactive
            
        except Exception as e:
            console.print(f"[red]❌ Erreur: {e}[/red]")
            return []
    
    async def get_current_channel(self) -> Optional[Dict]:
        """
        Récupère les infos de la chaîne actuelle.
        
        Returns:
            Infos de la chaîne ou None
        """
        try:
            # Récupérer le statut
            status = await self.fbx.player.get_player_status()
            foreground = status.get('foreground_app', {})
            context = foreground.get('context', {})
            channel = context.get('channel', {})
            
            return {
                'number': channel.get('channelNumber'),
                'name': channel.get('channelName'),
                'uuid': channel.get('channelUuid'),
                'type': channel.get('channelType'),
            }
            
        except Exception as e:
            console.print(f"[red]❌ Erreur récupération chaîne: {e}[/red]")
            return None
    
    async def test_oqee_api(self, channel_id: str) -> Optional[Dict]:
        """
        Teste l'API OQEE pour un channel_id.
        
        Args:
            channel_id: ID OQEE à tester
            
        Returns:
            Infos de l'API ou None si erreur
        """
        url = f"https://api.oqee.net/api/v1/live/anti_adskipping/{channel_id}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    
                    if not data.get('success'):
                        return None
                    
                    periods = data.get('result', {}).get('periods', [])
                    ad_breaks = [p for p in periods if p.get('type') == 'ad_break']
                    
                    return {
                        'total_periods': len(periods),
                        'ad_breaks': len(ad_breaks),
                        'success': True
                    }
        except Exception:
            return None
    
    def display_channel_info(self, channel_info: Dict):
        """Affiche les infos d'une chaîne."""
        table = Table(show_header=False, box=box.ROUNDED, padding=(0, 2))
        table.add_column("Label", style="cyan")
        table.add_column("Value", style="white bold")
        
        table.add_row("📺 Nom", channel_info.get('name', 'N/A'))
        table.add_row("🔢 Numéro", str(channel_info.get('number', 'N/A')))
        table.add_row("🆔 UUID", channel_info.get('uuid', 'N/A'))
        table.add_row("📡 Type", channel_info.get('type', 'N/A'))
        
        panel = Panel(
            table,
            title="[bold]Informations de la chaîne[/bold]",
            border_style="blue"
        )
        
        console.print(panel)
    
    async def map_channel(self, channel_number: int) -> bool:
        """
        Mappe une chaîne individuellement.
        
        Args:
            channel_number: Numéro de la chaîne
            
        Returns:
            True si succès, False sinon
        """
        console.clear()
        console.print(f"\n[bold cyan]═══ Chaîne n°{channel_number} ═══[/bold cyan]\n")
        
        # Demander à l'utilisateur de changer de chaîne
        console.print(Panel(
            f"[yellow]📺 Changez manuellement sur la chaîne {channel_number}[/yellow]\n\n"
            "Utilisez votre télécommande Freebox pour changer de chaîne.",
            border_style="yellow"
        ))
        
        if not Confirm.ask("\n[cyan]Prêt ? (chaîne changée)[/cyan]", default=True):
            console.print("[dim]⏭️  Chaîne ignorée[/dim]")
            return True
        
        # Récupérer les infos de la chaîne actuelle
        console.print("\n[cyan]📡 Récupération des informations...[/cyan]")
        channel_info = await self.get_current_channel()
        
        if not channel_info:
            console.print("[red]❌ Impossible de récupérer les infos de la chaîne[/red]")
            return False
        
        # Afficher les infos
        self.display_channel_info(channel_info)
        
        # Demander si on veut mapper cette chaîne
        if not Confirm.ask(f"\n[yellow]Voulez-vous mapper cette chaîne ?[/yellow]", default=True):
            console.print("[dim]⏭️  Chaîne ignorée[/dim]")
            return True
        
        # Boucle pour saisir et tester l'ID OQEE
        while True:
            oqee_id = Prompt.ask(
                "\n[cyan]Entrez l'ID OQEE[/cyan]",
                default="skip"
            )
            
            if oqee_id.lower() == "skip":
                console.print("[dim]⏭️  Chaîne ignorée[/dim]")
                return True
            
            # Tester l'API
            console.print(f"[yellow]🔍 Test de l'API OQEE avec ID={oqee_id}...[/yellow]")
            
            result = await self.test_oqee_api(oqee_id)
            
            if result:
                console.print(f"[green]✅ API OK ! {result['ad_breaks']} pubs trouvées[/green]")
                
                # Sauvegarder le mapping
                uuid = channel_info['uuid']
                self.mappings[uuid] = oqee_id
                
                # Sauvegarder aussi les infos de la chaîne
                self.channels_info.append({
                    **channel_info,
                    'oqee_id': oqee_id,
                    'tested_at': datetime.now().isoformat()
                })
                
                console.print(f"[green]💾 Mapping sauvegardé : {uuid} -> {oqee_id}[/green]")
                return True
            else:
                console.print("[red]❌ API OQEE invalide ou erreur[/red]")
                
                if not Confirm.ask("[yellow]Réessayer avec un autre ID ?[/yellow]", default=True):
                    console.print("[dim]⏭️  Chaîne ignorée[/dim]")
                    return True
    
    def save_mappings(self, filename: str = "channel_mappings.json"):
        """
        Sauvegarde les mappings dans un fichier JSON.
        
        Args:
            filename: Nom du fichier de sortie
        """
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_channels': len(self.mappings),
            'mappings': self.mappings,
            'channels_details': self.channels_info
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        console.print(f"\n[green]💾 Mappings sauvegardés dans {filename}[/green]")
    
    def save_python_config(self, filename: str = "channel_mappings_generated.py"):
        """
        Génère un fichier Python prêt à copier-coller dans config.py.
        
        Args:
            filename: Nom du fichier de sortie
        """
        lines = [
            '"""',
            'Mappings générés automatiquement',
            f'Généré le : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            f'Nombre de chaînes : {len(self.mappings)}',
            '"""',
            '',
            'CHANNEL_MAPPING = {',
        ]
        
        # Trier par nom de chaîne
        sorted_channels = sorted(
            self.channels_info,
            key=lambda x: x.get('number', 999)
        )
        
        for channel in sorted_channels:
            uuid = channel['uuid']
            oqee_id = channel['oqee_id']
            name = channel['name']
            number = channel['number']
            
            lines.append(f'    "{uuid}": "{oqee_id}",  # {number} - {name}')
        
        lines.append('}')
        lines.append('')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        console.print(f"[green]📝 Fichier Python généré : {filename}[/green]")
    
    async def interactive_mapping(self, start_channel: int = 1, max_channels: int = 50):
        """
        Mode interactif pour mapper les chaînes.
        
        Args:
            start_channel: Chaîne de départ
            max_channels: Nombre maximum de chaînes à parcourir
        """
        console.print(Panel(
            "[bold]🎬 Outil de mapping des chaînes Freebox -> OQEE[/bold]\n\n"
            "Cet outil va vous aider à mapper vos chaînes.\n\n"
            "[yellow]⚠️  Mode manuel :[/yellow]\n"
            "  • Vous devrez changer de chaîne manuellement avec votre télécommande\n"
            "  • Pour chaque chaîne, entrez l'ID OQEE correspondant\n\n"
            "[yellow]Commandes :[/yellow]\n"
            "  • Entrez l'ID OQEE pour mapper la chaîne\n"
            "  • Tapez 'skip' pour ignorer une chaîne\n"
            "  • Utilisez Ctrl+C pour arrêter\n",
            border_style="cyan",
            box=box.DOUBLE
        ))
        
        console.print(f"\n[cyan]🚀 Démarrage à la chaîne {start_channel}[/cyan]\n")
        
        current_channel = start_channel
        
        try:
            while current_channel < start_channel + max_channels:
                success = await self.map_channel(current_channel)
                
                if success:
                    # Demander si on continue
                    if not Confirm.ask(
                        f"\n[yellow]Passer à la chaîne {current_channel + 1} ?[/yellow]",
                        default=True
                    ):
                        break
                    
                    current_channel += 1
                else:
                    # Erreur, demander si on continue quand même
                    if not Confirm.ask(
                        "\n[yellow]Erreur. Continuer quand même ?[/yellow]",
                        default=False
                    ):
                        break
                    
                    current_channel += 1
        
        except KeyboardInterrupt:
            console.print("\n\n[yellow]⏹️  Arrêt demandé[/yellow]")
        
        # Sauvegarder les résultats
        if self.mappings:
            console.print(f"\n[bold green]✅ {len(self.mappings)} chaînes mappées ![/bold green]")
            
            self.save_mappings()
            self.save_python_config()
            
            # Afficher le résumé
            console.print("\n[bold]📊 Résumé :[/bold]")
            
            table = Table(box=box.SIMPLE)
            table.add_column("N°", style="cyan")
            table.add_column("Chaîne", style="white")
            table.add_column("UUID", style="dim")
            table.add_column("ID OQEE", style="green")
            
            for channel in sorted(self.channels_info, key=lambda x: x.get('number', 999)):
                table.add_row(
                    str(channel['number']),
                    channel['name'],
                    channel['uuid'][:20] + '...',
                    channel['oqee_id']
                )
            
            console.print(table)
        else:
            console.print("\n[yellow]⚠️  Aucune chaîne mappée[/yellow]")


async def main():
    """Point d'entrée principal."""
    mapper = ChannelMapper()
    
    try:
        await mapper.connect()
        
        # Demander la chaîne de départ
        start = Prompt.ask(
            "[cyan]Numéro de la première chaîne ?[/cyan]",
            default="1"
        )
        
        max_channels = Prompt.ask(
            "[cyan]Combien de chaînes maximum à parcourir ?[/cyan]",
            default="30"
        )
        
        await mapper.interactive_mapping(
            start_channel=int(start),
            max_channels=int(max_channels)
        )
        
    finally:
        await mapper.disconnect()
    
    console.print("\n[bold green]👋 Terminé ![/bold green]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Au revoir ![/yellow]")
        sys.exit(0)
