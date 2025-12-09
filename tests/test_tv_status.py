#!/usr/bin/env python3
"""
Script de test pour vérifier les améliorations du module freebox_api.
"""
import sys
sys.path.insert(0, 'src')

from freetv.models import PlayerStatus

def test_is_tv_on():
    """Test de la propriété is_tv_on."""
    
    print("🧪 Test de la propriété is_tv_on\n")
    
    # Test 1: TV allumée avec une chaîne
    print("Test 1: TV allumée avec une chaîne")
    player1 = PlayerStatus(
        power_state="running",
        playback_state="playing",
        channel_uuid="uuid-webtv-612",
        channel_number=1,
        channel_name="TF1",
        is_playing=True
    )
    assert player1.is_tv_on == True, "❌ Échec: TV devrait être ON"
    print(f"✅ is_tv_on = {player1.is_tv_on} (attendu: True)\n")
    
    # Test 2: TV éteinte
    print("Test 2: TV éteinte (power_state != running)")
    player2 = PlayerStatus(
        power_state="standby",
        playback_state="stopped",
        channel_uuid="",
        channel_number=0,
        channel_name="",
        is_playing=False
    )
    assert player2.is_tv_on == False, "❌ Échec: TV devrait être OFF"
    print(f"✅ is_tv_on = {player2.is_tv_on} (attendu: False)\n")
    
    # Test 3: TV allumée mais pas en lecture
    print("Test 3: TV allumée mais pas en lecture")
    player3 = PlayerStatus(
        power_state="running",
        playback_state="paused",
        channel_uuid="uuid-webtv-612",
        channel_number=1,
        channel_name="TF1",
        is_playing=False
    )
    assert player3.is_tv_on == False, "❌ Échec: TV devrait être OFF (pas en lecture)"
    print(f"✅ is_tv_on = {player3.is_tv_on} (attendu: False)\n")
    
    # Test 4: TV allumée mais aucune chaîne
    print("Test 4: TV allumée mais aucune chaîne (channel_uuid vide)")
    player4 = PlayerStatus(
        power_state="running",
        playback_state="playing",
        channel_uuid="",
        channel_number=0,
        channel_name="",
        is_playing=True
    )
    assert player4.is_tv_on == False, "❌ Échec: TV devrait être OFF (pas de chaîne)"
    print(f"✅ is_tv_on = {player4.is_tv_on} (attendu: False)\n")
    
    # Test 5: TV avec toutes les bonnes conditions
    print("Test 5: TV avec toutes les bonnes conditions")
    player5 = PlayerStatus(
        power_state="running",
        playback_state="playing",
        channel_uuid="uuid-webtv-201",
        channel_number=2,
        channel_name="France 2",
        is_playing=True
    )
    assert player5.is_tv_on == True, "❌ Échec: TV devrait être ON"
    print(f"✅ is_tv_on = {player5.is_tv_on} (attendu: True)\n")
    
    print("=" * 60)
    print("✅ Tous les tests sont passés avec succès !")
    print("=" * 60)

if __name__ == "__main__":
    test_is_tv_on()
