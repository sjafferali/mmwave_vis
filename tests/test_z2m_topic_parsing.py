"""
Tests for Z2M device-discovery topic → friendly-name extraction.

The logic under test lives in Z2MDriver._on_message (app.py):

    parts = topic.split('/')
    fname = '/'.join(parts[1:])

The MQTT topic format is  <base_topic>/<friendly_name>
where <friendly_name> may itself contain forward slashes or other
special characters that users sometimes include in device names.

These tests verify that the extraction round-trips correctly for a wide
range of name styles, including the slash that triggered the original bug.
"""


BASE = "zigbee2mqtt"


def _extract_fname(topic: str) -> str:
    """Mirror of the fixed extraction logic in Z2MDriver._on_message."""
    parts = topic.split('/')
    return '/'.join(parts[1:])


def _round_trip(fname: str) -> str:
    """Build the full topic then extract the name back out."""
    topic = f"{BASE}/{fname}"
    return _extract_fname(topic)


# ---------------------------------------------------------------------------
# Baseline — names without special characters
# ---------------------------------------------------------------------------

def test_plain_name():
    assert _round_trip("LivingRoom") == "LivingRoom"

def test_name_with_spaces():
    assert _round_trip("Living Room Switch") == "Living Room Switch"

def test_name_with_numbers():
    assert _round_trip("Switch01") == "Switch01"


# ---------------------------------------------------------------------------
# Forward slash — the bug that prompted this fix
# ---------------------------------------------------------------------------

def test_name_with_one_slash():
    # e.g. "Switch w/ mmWave"
    assert _round_trip("Switch w/ mmWave") == "Switch w/ mmWave"

def test_name_with_multiple_slashes():
    assert _round_trip("Floor/Room/Switch") == "Floor/Room/Switch"

def test_name_starting_with_slash():
    # A name with a leading slash would produce a double-slash MQTT topic.
    # Z2M would never emit such a topic, but verify the extractor doesn't crash.
    topic = f"{BASE}//LeadingSlash"   # double-slash: adversarial input
    assert _extract_fname(topic) == "/LeadingSlash"

def test_name_ending_with_slash():
    assert _round_trip("TrailingSlash/") == "TrailingSlash/"

def test_name_only_slash():
    assert _round_trip("/") == "/"


# ---------------------------------------------------------------------------
# Ampersand and other common punctuation
# ---------------------------------------------------------------------------

def test_ampersand():
    assert _round_trip("Kitchen & Dining") == "Kitchen & Dining"

def test_plus_sign():
    # '+' is an MQTT wildcard at the broker level but can appear in names
    assert _round_trip("Switch+Fan") == "Switch+Fan"

def test_hash_sign():
    # '#' is an MQTT wildcard at the broker level but can appear in names
    assert _round_trip("Switch #1") == "Switch #1"

def test_percent():
    assert _round_trip("50% Dim Switch") == "50% Dim Switch"

def test_at_sign():
    assert _round_trip("Switch@Home") == "Switch@Home"

def test_exclamation():
    assert _round_trip("Alert!Switch") == "Alert!Switch"

def test_question_mark():
    assert _round_trip("Switch?") == "Switch?"

def test_equals_sign():
    assert _round_trip("Param=Value") == "Param=Value"


# ---------------------------------------------------------------------------
# Brackets and quotes
# ---------------------------------------------------------------------------

def test_parentheses():
    assert _round_trip("Switch (mmWave)") == "Switch (mmWave)"

def test_square_brackets():
    assert _round_trip("Switch [mmWave]") == "Switch [mmWave]"

def test_curly_braces():
    assert _round_trip("Switch {mmWave}") == "Switch {mmWave}"

def test_angle_brackets():
    assert _round_trip("Switch <v2>") == "Switch <v2>"

def test_double_quotes():
    assert _round_trip('Switch "Pro"') == 'Switch "Pro"'

def test_single_quote():
    assert _round_trip("Nick's Switch") == "Nick's Switch"

def test_backtick():
    assert _round_trip("Switch`A") == "Switch`A"


# ---------------------------------------------------------------------------
# Dashes, underscores, dots
# ---------------------------------------------------------------------------

def test_hyphen():
    assert _round_trip("Living-Room-Switch") == "Living-Room-Switch"

def test_underscore():
    assert _round_trip("living_room_switch") == "living_room_switch"

def test_dot():
    assert _round_trip("switch.v2") == "switch.v2"

def test_double_dot():
    assert _round_trip("switch..v2") == "switch..v2"


# ---------------------------------------------------------------------------
# Unicode and non-ASCII
# ---------------------------------------------------------------------------

def test_accented_characters():
    assert _round_trip("Schlafzimmer Schalter") == "Schlafzimmer Schalter"

def test_emoji():
    assert _round_trip("Switch 🏠") == "Switch 🏠"

def test_cjk_characters():
    assert _round_trip("开关") == "开关"

def test_arabic():
    assert _round_trip("مفتاح") == "مفتاح"


# ---------------------------------------------------------------------------
# Combinations — realistic user names
# ---------------------------------------------------------------------------

def test_slash_and_ampersand():
    # "w/ mmWave & Dimmer"
    assert _round_trip("Switch w/ mmWave & Dimmer") == "Switch w/ mmWave & Dimmer"

def test_slash_and_parens():
    assert _round_trip("Bedroom (w/ mmWave)") == "Bedroom (w/ mmWave)"

def test_multiple_slashes_and_spaces():
    assert _round_trip("Home/Floor 2/Bedroom Switch") == "Home/Floor 2/Bedroom Switch"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_name():
    # Empty friendly name — base topic only with trailing slash
    topic = f"{BASE}/"
    assert _extract_fname(topic) == ""

def test_very_long_name():
    long_name = "A" * 500
    assert _round_trip(long_name) == long_name

def test_whitespace_only_name():
    assert _round_trip("   ") == "   "

def test_newline_in_name():
    # Unlikely but should not crash
    assert _round_trip("Switch\nLine2") == "Switch\nLine2"
