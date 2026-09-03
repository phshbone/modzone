from pathlib import Path
import re

path = Path('index.html')
text = path.read_text()

old_decl = 'let GPS_ICON_NORMAL, GPS_ICON_DRAG, INCIDENT_ICON, ENTRANCE_FLAG_ICON;'
new_decl = '''let GPS_ICON_NORMAL,
        GPS_ICON_DRAG,
        INCIDENT_ICON,
        LEGACY_INCIDENT_ICON,
        CAMPAIGN_SIGN_ICON,
        ENTRANCE_FLAG_ICON;'''
if old_decl not in text:
    raise SystemExit('Expected incident icon declaration not found')
text = text.replace(old_decl, new_decl, 1)

pattern = re.compile(
    r"        INCIDENT_ICON = L\.divIcon\(\{\n          className: '',\n          html: INCIDENT_STAKE_SVG,\n          iconSize: \[15, 46\],\n          iconAnchor: \[7, 44\],\n          popupAnchor: \[0, -44\],\n        \}\);"
)
replacement = '''        LEGACY_INCIDENT_ICON = L.divIcon({
          className: '',
          html: INCIDENT_STAKE_SVG,
          iconSize: [15, 46],
          iconAnchor: [7, 44],
          popupAnchor: [0, -44],
        });

        CAMPAIGN_SIGN_ICON = L.icon({
          iconUrl: 'assets/campaign-sign-marker.svg',
          iconSize: [58, 82],
          iconAnchor: [29, 82],
          popupAnchor: [0, -80],
        });

        // Preferred incident marker. Revert to LEGACY_INCIDENT_ICON here if needed.
        INCIDENT_ICON = CAMPAIGN_SIGN_ICON;'''
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit('Expected legacy incident icon block not found')

path.write_text(text)
