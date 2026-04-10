#!/bin/sh
# Generate options.json from environment variables for standalone Docker usage.

cat > /data/options.json <<EOF
{
  "zigbee_stack": "${ZIGBEE_STACK:-z2m}",
  "debug": ${DEBUG:-false},
  "mqtt_broker": "${MQTT_BROKER:-localhost}",
  "mqtt_port": ${MQTT_PORT:-1883},
  "mqtt_username": "${MQTT_USERNAME:-}",
  "mqtt_password": "${MQTT_PASSWORD:-}",
  "mqtt_base_topic": "${MQTT_BASE_TOPIC:-zigbee2mqtt}",
  "ha_url": "${HA_URL:-http://localhost:8123}",
  "ha_token": "${HA_TOKEN:-}"
}
EOF

exec python app.py
