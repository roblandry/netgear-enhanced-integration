"""
Support for Netgear routers.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.netgear_enhanced/
"""
import logging

import voluptuous as vol
from datetime import timedelta

from homeassistant.components.switch import SwitchEntity, PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD,
    CONF_SSL, CONF_RESOURCES, CONF_SCAN_INTERVAL
    )

import homeassistant.helpers.config_validation as cv

VERSION = '0.2.0'
REQUIREMENTS = ['pynetgear-enhanced==0.2.2']
_LOGGER = logging.getLogger(__name__)

DEFAULT_HOST = '192.168.1.1'
DEFAULT_PORT = '5000'
DEFAULT_PREFIX = 'ng_enhanced'

SCAN_INTERVAL = timedelta(minutes=5)
# Name, onoffFunction, Checkfunction, checkNode
SWITCH_TYPES = {
    'access_control': [
        'Access Control', 'set_block_device_enable',
        'get_block_device_enable_status', 'NewBlockDeviceEnable'],
    'traffic_meter': [
        'Traffic Meter', 'enable_traffic_meter',
        'get_traffic_meter_enabled', 'NewTrafficMeterEnable'],
    'parental_control': [
        'Parental Control', 'enable_parental_control',
        'get_parental_control_enable_status', 'ParentalControl'],
    'qos': [
        'QOS', 'set_qos_enable_status',
        'get_qos_enable_status', 'NewQoSEnableStatus'],
    '2g_guest_wifi': [
        'Guest Wifi', 'set_guest_access_enabled',
        'get_guest_access_enabled', 'NewGuestAccessEnabled'],
    '5g_guest_wifi': [
        '5G Guest Wifi', 'set_5g_guest_access_enabled',
        'get_5g_guest_access_enabled', 'NewGuestAccessEnabled'],
    'run_speed_test': [
        'Run a Speed Test', 'set_speed_test_start',
        '', ''],
    'reboot': [
        'Reboot Router', 'reboot',
        '', ''],
}


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({

    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_SSL, default=False): cv.boolean,
    vol.Optional(CONF_RESOURCES, default=['access_control', 'traffic_meter', 'parental_control', 'qos', '2g_guest_wifi', '5g_guest_wifi', 'run_speed_test', 'reboot']):
        vol.All(cv.ensure_list, [vol.In(SWITCH_TYPES)]),
})


def setup_platform(hass, config, add_entities_callback, discovery_info=None):
    """Set up the netgear_enhanced switches."""
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    ssl = config[CONF_SSL]
    scan_interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
    resources = config[CONF_RESOURCES]

    _LOGGER.debug("NETGEAR: Setup Switches")

    args = [password, host, username, port, ssl]
    switches = []
    for kind in resources:
        switches.append(NetgearEnhancedSwitch(
            args, kind, scan_interval)
        )

    add_entities_callback(switches)


class NetgearEnhancedSwitch(SwitchEntity):
    """Representation of a netgear enhanced switch."""

    def __init__(self, args, kind, scan_interval):
        """Initialize the netgear enhanced switch."""
        self._name = SWITCH_TYPES[kind][0]
        self.entity_id = f"switch.{DEFAULT_PREFIX}_{kind}"
        self._nfFunction = SWITCH_TYPES[kind][1]
        self._cFunction = SWITCH_TYPES[kind][2]
        self._cNode = SWITCH_TYPES[kind][3]
        self._is_on = None
        self._icon = None
        self._scan_interval = scan_interval

        from pynetgear_enhanced import NetgearEnhanced
        self._api = NetgearEnhanced(
            args[0], args[1], args[2], args[3], args[4]
            )

        self.update()

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
        _LOGGER.debug("Netgear Switch: check if %s is on.", self._name)
        if self._nfFunction in ('set_speed_test_start', 'reboot'):
            self._is_on = False

        return self._is_on

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        _LOGGER.debug("Netgear Switch: Turning on %s", self._name)
        getattr(self._api, self._nfFunction)('True')

        self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.debug("Netgear Switch: Turning off %s", self._name)
        getattr(self._api, self._nfFunction)('False')

        self._is_on = False
        self.schedule_update_ha_state()

    def update(self):
        """Check if is on."""
        # https://goo.gl/Nvioub
        _LOGGER.debug("Netgear Switch update function")
        toCheck = ''

        self._is_on = False

        if self._cFunction:
            response = getattr(self._api, self._cFunction)()

            if response:
                toCheck = response[self._cNode]

                if toCheck == '1':
                    self._is_on = True

        theLog = f"{self._name}: {toCheck}: {self._is_on}"
        _LOGGER.debug("Netgear Switch %s", theLog)

        return self._is_on
