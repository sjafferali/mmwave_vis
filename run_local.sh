#!/usr/bin/env bash
# Run mmwave_vis locally without Home Assistant.
#
# Usage:
#   ./run_local.sh              # uses defaults or env vars
#   ./run_local.sh --help       # show configuration options
#
# Configuration is done via environment variables or a .env file in this
# directory. Copy env.example to .env and fill in your values.

set -euo pipefail
cd "$(dirname "$0")"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    cat <<'USAGE'
mmwave_vis local runner

Set configuration via environment variables or a .env file:

  MQTT_BROKER       MQTT broker hostname       (default: localhost)
  MQTT_PORT         MQTT broker port           (default: 1883)
  MQTT_USERNAME     MQTT username              (default: empty)
  MQTT_PASSWORD     MQTT password              (default: empty)
  MQTT_BASE_TOPIC   Zigbee2MQTT base topic     (default: zigbee2mqtt)
  ZIGBEE_STACK      z2m or zha                 (default: z2m)
  DEBUG             true/false                 (default: false)
  HA_URL            Home Assistant URL (ZHA)   (default: http://localhost:8123)
  HA_TOKEN          HA long-lived token (ZHA)  (default: empty)
  PORT              Web UI port                (default: 5000)

Example:
  export MQTT_BROKER=192.168.1.100
  export MQTT_USERNAME=myuser
  export MQTT_PASSWORD=mypass
  ./run_local.sh
USAGE
    exit 0
fi

# Load .env file if present
if [[ -f .env ]]; then
    echo "Loading .env file..."
    set -a
    # shellcheck source=/dev/null
    source .env
    set +a
fi

# Set up virtualenv
VENV_DIR=".venv"
if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating virtualenv..."
    python3 -m venv "$VENV_DIR"
fi

echo "Activating virtualenv..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install -q -r mmwave_vis/requirements.txt

# Write options.json for the app
OPTIONS_DIR="/tmp/mmwave_vis_local"
mkdir -p "$OPTIONS_DIR"

cat > "$OPTIONS_DIR/options.json" <<EOF
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

echo ""
echo "=== mmwave_vis local runner ==="
echo "  Stack:  ${ZIGBEE_STACK:-z2m}"
echo "  Broker: ${MQTT_BROKER:-localhost}:${MQTT_PORT:-1883}"
echo "  Topic:  ${MQTT_BASE_TOPIC:-zigbee2mqtt}"
echo "  Debug:  ${DEBUG:-false}"
echo "  UI:     http://localhost:${PORT:-5000}"
echo "==============================="
echo ""

# Override the config path so the app reads our generated options.json
export MMWAVE_VIS_CONFIG_PATH="$OPTIONS_DIR/options.json"

cd mmwave_vis
exec python app.py
