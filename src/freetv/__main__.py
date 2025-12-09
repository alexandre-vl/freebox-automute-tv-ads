"""
Main Entry Point.
"""
import sys
import asyncio
from rich.live import Live

from .core.engine import AutoMuteEngine
from .ui.console import console
from .ui.display import StatusDisplay

async def main():
    """Point d'entrée principal."""
    try:
        async with AutoMuteEngine() as engine:
            console.clear()
            console.print("[bold green]🚀 Démarrage du moteur Auto-Mute...[/bold green]\n")
            
            with Live(console=console, refresh_per_second=2, screen=True) as live:
                while True:
                    await engine.run_step()
                    
                    # Update Display
                    state = engine.get_display_state()
                    panel = StatusDisplay.create_panel(
                        player_status=state["player_status"],
                        volume_state=await engine.fbx_client.get_volume_state(), # Note: Double fetch? Engine could cache it.
                        ad_breaks=state["ad_breaks"],
                        active_ad=state["active_ad"],
                        next_ad=state["next_ad"],
                        current_program=state["current_program"],
                        ad_last_fetch=engine.oqee_client._ad_breaks_last_fetch
                    )
                    
                    live.update(panel)
                    await asyncio.sleep(engine.check_interval)
                    
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Au revoir ![/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Erreur fatale: {e}[/red]")
        # import traceback
        # traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
