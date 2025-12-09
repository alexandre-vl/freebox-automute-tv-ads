"""
Configuration module for Freebox Auto-Mute.
Loads settings from environment variables with defaults.
"""
import os

# Freebox Connection
FREEBOX_HOST = os.getenv("FREEBOX_HOST", "mafreebox.freebox.fr")
FREEBOX_PORT = os.getenv("FREEBOX_PORT", "443")

# Application Settings
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "1"))
CHECK_INTERVAL_TV_OFF = int(os.getenv("CHECK_INTERVAL_TV_OFF", "5"))  # Délai plus long quand TV éteinte
AD_BREAKS_CACHE_TTL = int(os.getenv("AD_BREAKS_CACHE_TTL", "3"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Unmute buffer in seconds (avoid unmuting between close ads)
UNMUTE_BUFFER = int(os.getenv("UNMUTE_BUFFER", "10"))

# Max gap between ads to merge them (avoid unmuting for 10s of jingle)
AD_MERGE_MAX_GAP = int(os.getenv("AD_MERGE_MAX_GAP", "60"))

# Channel Mapping (OQEE UUID -> API ID)
# Default mapping (can be extended via config file later if needed)
CHANNEL_MAPPING = {
    "uuid-webtv-612": "536", # TF1
    "uuid-webtv-201": "270", # France 2
    "uuid-webtv-202": "363", # France 3
    "uuid-webtv-376": "412", # France 4
    "uuid-webtv-203": "272", # France 5
    "uuid-webtv-613": "537", # M6
    "uuid-webtv-204": "273", # Arte
    "uuid-webtv-226": "294", # LCP
    "uuid-webtv-373": "409", # W9
    "uuid-webtv-497": "517", # TMC
    "uuid-webtv-374": "410", # TFX
    "uuid-webtv-677": "557", # Gulli
    "uuid-webtv-400": "429", # BFMTV
    "uuid-webtv-679": "559", # CNEWS
    "uuid-webtv-1145": "107", # LCI
    "uuid-webtv-1173": "124", # FranceInfo
    "uuid-webtv-678": "558", # CSTAR

    "uuid-webtv-995": "845", # 6ter

    "uuid-webtv-998": "848", # RMC Life

    # Ajouter d'autres chaînes ici selon vos besoins
    # Exemples:
    # "uuid-webtv-XXX": "YYY",  # TF1
    # "uuid-webtv-XXX": "YYY",  # France 2
}
