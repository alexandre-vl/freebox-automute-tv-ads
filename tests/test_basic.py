"""
Script de test pour vérifier la configuration et les connexions.
"""

import asyncio
import sys

try:
    from freebox_api import Freepybox
    import aiohttp
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("   Installez les dépendances avec: pip install -r requirements.txt")
    sys.exit(1)

try:
    from config import FREEBOX_HOST, FREEBOX_PORT, CHANNEL_MAPPING
    print("✅ Fichier config.py trouvé")
except ImportError:
    print("⚠️  Fichier config.py non trouvé, utilisation des valeurs par défaut")
    FREEBOX_HOST = "mafreebox.freebox.fr"
    FREEBOX_PORT = "443"
    CHANNEL_MAPPING = {"uuid-webtv-497": "517"}


async def test_freebox_connection():
    """Test de connexion à la Freebox."""
    print("\n🔌 Test de connexion à la Freebox...")
    print(f"   Host: {FREEBOX_HOST}:{FREEBOX_PORT}")
    
    try:
        fbx = Freepybox(api_version="v4")
        await fbx.open(FREEBOX_HOST, port=FREEBOX_PORT)
        print("✅ Connexion Freebox réussie")
        
        # Test de récupération du statut
        print("\n📺 Récupération du statut du lecteur...")
        status = await fbx.player.get_player_status()
        
        power_state = status.get('power_state', 'unknown')
        print(f"   État: {power_state}")
        
        if power_state == "running":
            foreground = status.get('foreground_app', {})
            context = foreground.get('context', {})
            channel = context.get('channel', {})
            
            channel_name = channel.get('channelName', 'N/A')
            channel_number = channel.get('channelNumber', 'N/A')
            channel_uuid = channel.get('channelUuid', 'N/A')
            
            print(f"   Chaîne: {channel_name} (#{channel_number})")
            print(f"   UUID: {channel_uuid}")
            
            # Vérifier le mapping
            if channel_uuid in CHANNEL_MAPPING:
                oqee_id = CHANNEL_MAPPING[channel_uuid]
                print(f"   ✅ Mapping trouvé -> ID OQEE: {oqee_id}")
            else:
                print(f"   ⚠️  Pas de mapping pour ce channel_uuid dans config.py")
        
        # Test du volume
        print("\n🔊 Récupération du volume...")
        volume = await fbx.player.get_player_volume()
        print(f"   Volume: {volume.get('volume', 0)}")
        print(f"   Mute: {volume.get('mute', False)}")
        
        await fbx.close()
        print("\n✅ Tous les tests Freebox ont réussi!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


async def test_oqee_api():
    """Test de l'API OQEE."""
    print("\n🌐 Test de l'API OQEE...")
    
    # Test avec TMC (ID 517)
    test_channel_id = "517"
    url = f"https://api.oqee.net/api/v1/live/anti_adskipping/{test_channel_id}"
    print(f"   URL: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        periods = data.get('result', {}).get('periods', [])
                        ad_breaks = [p for p in periods if p.get('type') == 'ad_break']
                        
                        print(f"✅ API OQEE accessible")
                        print(f"   Périodes totales: {len(periods)}")
                        print(f"   Publicités: {len(ad_breaks)}")
                        
                        if ad_breaks:
                            print(f"\n   Exemple de pub:")
                            from datetime import datetime
                            first_ad = ad_breaks[0]
                            start = datetime.fromtimestamp(first_ad['start_time']).strftime('%H:%M:%S')
                            end = datetime.fromtimestamp(first_ad['end_time']).strftime('%H:%M:%S')
                            print(f"   - {start} -> {end}")
                        
                        return True
                    else:
                        print(f"❌ API retourne success=false")
                        return False
                else:
                    print(f"❌ Erreur HTTP {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


async def main():
    """Point d'entrée principal."""
    print("=" * 60)
    print("🧪 TEST DE CONFIGURATION FREEBOX AUTO-MUTE")
    print("=" * 60)
    
    freebox_ok = await test_freebox_connection()
    oqee_ok = await test_oqee_api()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    print(f"   Freebox: {'✅ OK' if freebox_ok else '❌ ERREUR'}")
    print(f"   API OQEE: {'✅ OK' if oqee_ok else '❌ ERREUR'}")
    
    if freebox_ok and oqee_ok:
        print("\n🎉 Tout fonctionne ! Vous pouvez lancer: python main.py")
        return 0
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
