"""
Support for Netgear routers.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.netgear_enhanced/
"""
import logging

import voluptuous as vol
from datetime import timedelta

from homeassistant.components.switch import SwitchDevice, PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD,
    CONF_SSL, CONF_SCAN_INTERVAL
    )

import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['https://github.com/roblandry/pynetgear_enhanced/archive/master.zip#pynetgear_enhanced']  # noqa

_LOGGER = logging.getLogger(__name__)

DEFAULT_HOST = '192.168.1.1'
DEFAULT_PORT = '5000'

SCAN_INTERVAL = timedelta(minutes=5)
# Name, onoffFunction, Checkfunction, checkNode
SWITCH_TYPES = {
    'traffic_meter': [
        'Traffic Meter', 'enable_traffic_meter',
        'get_traffic_meter_enabled', 'NewTrafficMeterEnable'],
    'parental_control': [
        'Parental Control', 'enable_parental_control',
        'get_parental_control_enable_status', 'ParentalControl'],
    'qos': [
        'QOS', 'set_qos_enable_status',
        'getQoSEnableStatus', 'NewQoSEnableStatus'],
    'guest_wifi': [
        'Guest Wifi', 'set_guest_access_enabled',
        'get_guest_access_enabled', 'NewGuestAccessEnabled'],
    'guest_wifi_5g': [
        '5G Guest Wifi', 'set_5g_guest_access_enabled',
        'get_5g_guest_access_enabled', 'NewGuestAccessEnabled'],
}


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({

    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_SSL, default=False): cv.boolean,
})


def setup_platform(hass, config, add_entities_callback, discovery_info=None):
    """Set up the netgear_enhanced switches."""
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    ssl = config[CONF_SSL]
    scan_interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)

    _LOGGER.debug("NETGEAR: Setup Switches")

    switches = []
    for kind in SWITCH_TYPES:
        switches.append(NetgearEnhancedSwitch(
            host, ssl, username, password, port, kind, scan_interval)
        )

    add_entities_callback(switches)


class NetgearEnhancedSwitch(SwitchDevice):
    """Representation of a netgear enhanced switch."""

    def __init__(
        self, host, ssl, username, password, port, kind, scan_interval
    ):
        """Initialize the netgear enhanced switch."""
        self._name = f"NG {SWITCH_TYPES[kind][0]}"
        self._nfFunction = SWITCH_TYPES[kind][1]
        self._cFunction = SWITCH_TYPES[kind][2]
        self._cNode = SWITCH_TYPES[kind][3]
        self._state = None
        self._icon = None
        self._scan_interval = scan_interval

        from pynetgear_enhanced import Netgear
        self._api = Netgear(password, host, username, port, ssl)

    @property
    def should_poll(self):
        """Poll enabled for the netgear enhanced switch."""
        return True

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def icon(self):
        """Return the icon to use for device if any."""
        return self._icon

    @property
    def is_on(self):
        """Return true if switch is on."""
        self.response = getattr(self._api, self._cFunction)()

        if self.response:
            toCheck = self.response[self._cNode]
            if toCheck == '1':
                self._state = True
        else:
            self._state = False

        return self._state

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self.response = getattr(self._api, self._nfFunction)('True')

        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self.response = getattr(self._api, self._nfFunction)('False')

        self._state = False
        self.schedule_update_ha_state()
