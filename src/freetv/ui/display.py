"""
TUI Display Logic.
Preserves the exact visual style of the original script.
"""
import time
from datetime import datetime
from typing import Optional, List

from rich.panel import Panel
from rich import box

from ..models import PlayerStatus, VolumeState, AdBreak, TVProgram
from ..config import AD_BREAKS_CACHE_TTL

def fmt_dur(s):
    """Format duration in seconds to human readable string."""
    if s >= 3600: return f"{s//3600}h{(s%3600)//60:02d}"
    return f"{s//60}m{s%60:02d}" if s >= 60 else f"{s}s"

class StatusDisplay:
    """Gère l'affichage du statut."""
    
    @staticmethod
    def create_panel(
        player_status: Optional[PlayerStatus],
        volume_state: Optional[VolumeState],
        ad_breaks: List[AdBreak],
        active_ad: Optional[AdBreak],
        next_ad: Optional[AdBreak],
        current_program: Optional[TVProgram],
        ad_last_fetch: float
    ) -> Panel:
        """
        Crée un panneau d'affichage intuitif avec timeline verticale.
        """
        current_time = int(time.time())
        content_parts = []
        
        # 1. EN-TÊTE : Chaîne & Programme
        # ────────────────────────────────────────────────────────
        # Vérifier d'abord si la TV est OFF
        if player_status and not player_status.is_tv_on:
            content_parts.append(f"[bold dim]📺 Freebox Player[/bold dim]")
            content_parts.append(f"[yellow]⏸️  TV OFF[/yellow] [dim]• Aucune chaîne regardée[/dim]")
            content_parts.append("")
            content_parts.append(f"[dim italic]En attente d'activité...[/dim italic]")
            
            return Panel(
                "\n".join(content_parts),
                title="🎬 Freebox Auto-Mute",
                border_style="dim",
                box=box.ROUNDED,
                padding=(0, 2)
            )
        
        if current_program and player_status:
            # Ligne 1 : Chaîne + Badge Live
            channel_info = f"[bold white]📺 {player_status.channel_name}[/bold white] [dim]• Chaîne {player_status.channel_number}[/dim]"
            status_badge = "[bold green]● EN DIRECT[/bold green]"
            content_parts.append(f"{channel_info} {status_badge:>35}") 
            
            # Ligne 2 : Titre Programme
            content_parts.append(f"[bold cyan size=14]{current_program.title}[/bold cyan size=14]")
            
            # Ligne 3 : Catégorie & Temps
            prog_meta = f"[dim]{current_program.category}"
            if current_program.sub_category:
                prog_meta += f" › {current_program.sub_category}"
            prog_meta += f" • Fin {datetime.fromtimestamp(current_program.end_time).strftime('%H:%M')}[/dim]"
            content_parts.append(prog_meta)
            
            # Ligne 4 : Barre de progression continue
            pct = current_program.progress_percentage(current_time)
            width = 60
            filled = int((pct/100) * width)
            # Style visuel fluide
            bar = f"[cyan]{'━'*filled}[/cyan][dim]{'─'*(width-filled)}[/dim]"
            content_parts.append(f"{bar} [cyan]{pct:.0f}%[/cyan]")
            content_parts.append("")
            
        elif player_status:
            content_parts.append(f"[bold]📺 {player_status.channel_name}[/bold] [dim]• #{player_status.channel_number}[/dim]")
            content_parts.append("")

        # 2. STATUS & VOLUME
        # ────────────────────────────────────────────────────────
        vol_state = "🔊 ACTIF"
        vol_color = "green"
        if volume_state and volume_state.mute:
            vol_state = "🔇 MUTÉ"
            vol_color = "red"
            
        vol_level = f"({volume_state.volume})" if volume_state else ""
        
        # Compteurs pubs
        total_ads = len(ad_breaks)
        future_ads = sum(1 for ad in ad_breaks if ad.start_time > current_time)
        past_ads = total_ads - future_ads
        
        # Message d'état principal
        if active_ad:
            remaining = active_ad.time_until_end(current_time)
            duration = active_ad.duration_seconds()
            elapsed = duration - remaining
            
            # Détecter estimation
            is_estimated = (duration == 300)
            
            status_msg = "[bold red blink]🚨 PUBLICITÉ EN COURS[/bold red blink]"
            
            if is_estimated:
                # Stratégie intelligente : viser la fin du programme si proche
                prog_remaining = current_program.time_remaining(current_time) if current_program else 9999
                
                if 0 < prog_remaining < 900:  # Si fin du programme dans moins de 15 min
                    # On se cale sur la fin du programme
                    target_time = datetime.fromtimestamp(current_program.end_time).strftime('%H:%M')
                    sub_msg = f"Jusqu'à la fin du programme ({target_time})"
                    
                    # Recalculer la barre sur cette base
                    total_window = elapsed + prog_remaining
                    progress = (elapsed / total_window) * 100
                else:
                    # Sinon on affiche juste le temps écoulé (moins anxiogène qu'un décompte faux)
                    mins = elapsed // 60
                    secs = elapsed % 60
                    sub_msg = f"Temps écoulé: {mins}m {secs:02d}s"
                    progress = 100 # On remplit la barre pour dire "on attend"
            else:
                progress = (elapsed / duration) * 100 if duration > 0 else 0
                sub_msg = f"Reste {remaining}s / {duration}s"
        elif next_ad:
            t_until = next_ad.time_until_start(current_time)
            status_msg = f"[bold yellow]⚠️ Prochaine pub dans {fmt_dur(t_until)}[/bold yellow]"
            sub_msg = f"Prévue à {datetime.fromtimestamp(next_ad.start_time).strftime('%H:%M:%S')}"
        elif future_ads == 0 and total_ads > 0:
            status_msg = "[bold green]✅ Zone calme[/bold green]"
            sub_msg = "Plus de publicités détectées pour ce programme"
        elif total_ads == 0:
            status_msg = "[dim green]ℹ️ Aucune info pub[/dim green]"
            sub_msg = "En attente de données..."
        else:
            status_msg = "[bold green]✅ Pas de pub[/bold green]"
            sub_msg = "Programme en cours"

        # Affichage Grid
        content_parts.append(f"[dim]─────── 🔎 État du sytème ───────[/dim]")
        content_parts.append(f"🔊 Volume : [{vol_color}]{vol_state}[/{vol_color}] {vol_level}")
        content_parts.append(f"📊 Pubs   : {total_ads} détectées ({past_ads} passées, [bold]{future_ads} à venir[/bold])")
        content_parts.append(f"🎯 Statut : {status_msg} • [dim]{sub_msg}[/dim]")
        
        # Barre de progression spéciale si pub active
        if active_ad:
            # Réutiliser la logique de calcul de progress
            remaining = active_ad.time_until_end(current_time)
            duration = active_ad.duration_seconds()
            elapsed = duration - remaining
            
            is_estimated = (duration == 300)
            
            if is_estimated:
                prog_remaining = current_program.time_remaining(current_time) if current_program else 9999
                if 0 < prog_remaining < 900:
                    total_window = elapsed + prog_remaining
                    progress = (elapsed / total_window) * 100
                else:
                    progress = 100
            else:
                progress = (elapsed / duration) * 100 if duration > 0 else 0
                
            bar_length = 60
            filled = int((progress / 100) * bar_length)
            
            color = "yellow" if is_estimated else "red"
            
            # Animation pour 'Temps écoulé' (progress=100)
            if is_estimated and progress == 100:
                bar = f"[{color}]" + "▓" * bar_length + f"[/{color}]"
            else:
                bar = f"[{color}]" + "█" * filled + "░" * (bar_length - filled) + f"[/{color}]"
                
            content_parts.append(f"{bar} {progress:.0f}%")

        content_parts.append("")

        # 3. AGENDA VERTICAL (La Timeline Intuitive)
        # ────────────────────────────────────────────────────────
        content_parts.append(f"[dim]─────── 📅 À venir (Agenda) ───────[/dim]")
        
        agenda_items = []
        
        # Item 1: Maintenant
        now_str = datetime.now().strftime('%H:%M')
        agenda_items.append(f"[cyan bold]{now_str}[/cyan bold]  📍 [cyan]Maintenant[/cyan]")
        
        # Items: Pubs futures (Max 3)
        future_ads_list = [ad for ad in ad_breaks if ad.start_time > current_time]
        for ad in future_ads_list[:3]:
            t_start = datetime.fromtimestamp(ad.start_time).strftime('%H:%M')
            dur = fmt_dur(ad.duration_seconds())
            
            # Calculer si c'est loin
            wait = ad.start_time - current_time
            color = "yellow" if wait < 300 else "white"
            icon = "⚡" if wait < 60 else "🔸"
            
            agenda_items.append(f"[dim]{t_start}[/dim]  {icon} [dim]Publicité[/dim] [{color}]dans {fmt_dur(wait)}[/{color}] [dim]({dur})[/dim]")

        # Item: Fin du programme
        if current_program:
            t_end = datetime.fromtimestamp(current_program.end_time).strftime('%H:%M')
            agenda_items.append(f"[dim]{t_end}[/dim]  🏁 [dim]Fin : {current_program.title}[/dim]")
            
        # Affichage avec ligne verticale
        for i, item in enumerate(agenda_items):
            # On utilise un style simple aligné
            parts = item.split("  ", 1)
            time_part = parts[0]
            rest = parts[1] if len(parts) > 1 else ""
            content_parts.append(f" {time_part} [dim]│[/dim] {rest}")

        content_parts.append("")
        
        # Footer compact
        if not active_ad and future_ads == 0:
             ttl_wait = max(0, AD_BREAKS_CACHE_TTL - int(current_time - ad_last_fetch))
             content_parts.append(f"[dim italic]Refresh auto dans {ttl_wait}s...[/dim italic]")

        content = "\n".join(content_parts)
        
        # Titre dynamique
        title = "🎬 Freebox Auto-Mute"
        border_style = "blue"
        if active_ad:
             title += " [bold red]● REC[/bold red]"
             border_style = "red"
        
        return Panel(
            content,
            title=title,
            border_style=border_style,
            box=box.ROUNDED,
            padding=(0, 2)
        )
