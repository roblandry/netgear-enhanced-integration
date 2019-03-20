"""
Support for Netgear routers.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/netgear_enhanced/
"""
import logging

import voluptuous as vol
from datetime import timedelta

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD,
    CONF_SSL, CONF_RESOURCES
    )

# from homeassistant.exceptions import PlatformNotReady
# from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

REQUIREMENTS = ['https://github.com/roblandry/pynetgear_enhanced/archive/master.zip#pynetgear_enhanced']  # noqa

_LOGGER = logging.getLogger(__name__)

DEFAULT_HOST = '192.168.1.1'
DEFAULT_PORT = '5000'

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

SENSOR_TYPES = {
    'getInfo': [
        'Info',
        'ModelName',
        'mdi:router-wireless'],
    'check_new_firmware': [
        'Firmware',
        'CurrentVersion',
        'mdi:cellphone-link'],
    'get_attached_devices': [
        'Attached Devices',
        '',
        'mdi:cellphone-link'],
    'get_attached_devices_2': [
        'Attached Devices2',
        '',
        'mdi:cellphone-link'],
    'get_traffic_meter_statistics': [
        'Traffic Meter',
        'NewTodayConnectionTime',
        'mdi:chart-areaspline'],
    'getSupportFeatureListXML': [
        'Supported Features',
        '',
        'mdi:router-wireless-settings'],
    'get_bandwidth_control_options': [
        'Bandwidth Control',
        '',
        'mdi:router-wireless-settings'],
    'getQoSEnableStatus': [
        'QOS Enabled',
        'NewQoSEnableStatus',
        'mdi:router-wireless-settings'],
    'get_all_mac_addresses': [
        'All MAC Addresses',
        '',
        'mdi:router-wireless-settings'],
    'get_dns_masq_device_id': [
        'DNS Masq',
        '',
        'mdi:router-wireless-settings'],
    'get_traffic_meter_enabled': [
        'Traffic Meter Enabled',
        'NewTrafficMeterEnable',
        'mdi:chart-areaspline'],
    'get_traffic_meter_options': [
        'Traffic Meter Opt',
        'NewControlOption',
        'mdi:chart-areaspline'],
    'get_guest_access_enabled': [
        'Guest Access',
        'NewGuestAccessEnabled',
        'mdi:account-group'],
    'get_5g1_guest_access_enabled': [
        '5G1 Guest Access',
        'NewGuestAccessEnabled',
        'mdi:account-group'],
    'get_5g1_guest_access_enabled_2': [
        '5G1 Guest Access2',
        'NewGuestAccessEnabled',
        'mdi:account-group'],
    'get_5g_guest_access_enabled_2': [
        '5G1 Guest Access2',
        'NewGuestAccessEnabled',
        'mdi:account-group'],
    'get_wpa_security_keys': [
        'WPA Security Key',
        'NewWPAPassphrase',
        'mdi:security'],
    'get_5g_wpa_security_keys': [
        '5G WPA Security Key',
        'NewWPAPassphrase',
        'mdi:security'],
    'get_5g_info': [
        '5G Info',
        'NewSSID',
        'mdi:signal-5g'],
    'get_2g_info': [
        '2G Info',
        'NewSSID',
        'mdi:signal-2g'],
    'get_guest_access_network_info': [
        'Guest Network Info',
        'NewSSID',
        'mdi:signal-2g'],
    'get_5g_guest_access_network_info': [
        '5G Guest Network Info',
        'NewSSID',
        'mdi:signal-5g'],
    'get_speed_test_result': [
        'Speed Test Result',
        'NewOOKLADownlinkBandwidth',
        'mdi:speedometer'],
}


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({

    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_SSL, default=False): cv.boolean,
    vol.Optional(CONF_RESOURCES, default=['getInfo']):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})


async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Setup the sensor platform."""

    host = config[CONF_HOST]
    port = config[CONF_PORT]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    ssl = config[CONF_SSL]
    resources = config[CONF_RESOURCES]

    _LOGGER.info("NETGEAR: async_setup_platform")

    #for kind in resources:
    #    add_devices([
    #        NetgearEnhancedSensor(host, ssl, username, password, port, kind)
    #        ])

    sensors = []
    for kind in resources:
        sensors.append(NetgearEnhancedSensor(host, ssl, username, password, port, kind))

    async_add_devices(sensors, True)

class NetgearEnhancedSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, host, ssl, username, password, port, kind):  # noqa
        """Initialize the sensor."""
        self._kind = kind
        self._name = SENSOR_TYPES[kind][0]
        self._state = None
        self._unit_of_measurement = ''
        self._state_key = SENSOR_TYPES[kind][1]
        self._attrs = None
        self._icon = SENSOR_TYPES[kind][2]

        from pynetgear_enhanced import Netgear

        self.last_results = []
        self._api = Netgear(password, host, username, port, ssl)

        _LOGGER.info("Logging in")

        results = self._get(kind)

        self.success_init = results is not None

        if self.success_init:
            self.last_results = results
        else:
            _LOGGER.error("Failed to Login")

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def device_state_attributes(self):
        """Return the device attributes."""
        return self._attrs

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    def _get(self, kind):
        """Get the data from pynetgear_enhanced based on function."""
        _LOGGER.debug("NETGEAR: _get")
        response = getattr(self._api, kind)()
        return response

    # @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Fetch new state and attributes for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        _LOGGER.debug("NETGEAR: async_update")
        self._attrs = self.last_results
        if self._state_key:
            self._state = self.last_results[self._state_key]
        else:
            self._state = None
