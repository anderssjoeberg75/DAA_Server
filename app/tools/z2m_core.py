"""
app/tools/z2m_core.py
---------------------
Handles communication with Zigbee2MQTT via MQTT protocol.
This tool allows the AI to fetch real-time sensor data.
"""

import json
import paho.mqtt.subscribe as subscribe
from config.settings import get_config

# Load configuration
cfg = get_config()

def get_sensor_data(friendly_name: str):
    """
    Fetches real-time data from a Zigbee sensor via MQTT.
    
    Args:
        friendly_name (str): The device ID (e.g., 'sensor_kok', 'vardagsrum_temp').
                             This matches the 'Friendly Name' in Zigbee2MQTT.
    
    Returns:
        str: A human-readable string with sensor values or an error message.
    """
    topic = f"{cfg['MQTT_TOPIC_BASE']}/{friendly_name}"
    print(f"[Z2M] Server reading from topic: {topic}")

    try:
        # Subscribe to the topic and wait for a single message (timeout 2.0s)
        # 'retained' messages usually arrive immediately.
        msg = subscribe.simple(
            topic, 
            hostname=cfg['MQTT_BROKER_IP'], 
            port=cfg['MQTT_PORT'], 
            timeout=2.0
        )

        if msg is None:
            return f"Error: No response from sensor '{friendly_name}' (Timeout)."

        # Parse JSON payload
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        # Format output for the AI (filtering out technical noise)
        readable_output = []
        ignored_keys = ["linkquality", "update_available", "voltage", "device"]
        
        for key, value in data.items():
            if key not in ignored_keys:
                readable_output.append(f"{key}: {value}")

        return f"Current data for {friendly_name}: " + ", ".join(readable_output)

    except Exception as e:
        print(f"[Z2M ERROR] {e}")
        return f"Failed to read sensor: {str(e)}"
