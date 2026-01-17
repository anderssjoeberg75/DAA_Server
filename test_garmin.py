from app.tools.garmin_core import GarminCoach
import json

print("--- TESTAR GARMIN-KOPPLING ---")
try:
    gc = GarminCoach()
    print("1. Inloggning initierad.")
    
    data = gc.get_health_report()
    
    if data:
        print("\nSUCCÉ! HÄMTADE DATA:")
        print(json.dumps(data, indent=4))
    else:
        print("\nFEL: Fick ingen data (None).")

except Exception as e:
    print(f"\nKRASCH: {e}")
