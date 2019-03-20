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

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=1)

SENSOR_TYPES = {
    'info': [
        'Info', 'ModelName',
        'mdi:router-wireless', 'getInfo'],
    'check_fw': [
        'Firmware', 'CurrentVersion',
        'mdi:cellphone-link', 'check_new_firmware'],
    'attached_devices': [
        'Attached Devices', '',
        'mdi:cellphone-link', 'get_attached_devices'],
    'attached_devices2': [
        'Attached Devices2', '',
        'mdi:cellphone-link', 'get_attached_devices_2'],
    'traffic_meter': [
        'Traffic Meter', 'NewTodayConnectionTime',
        'mdi:chart-areaspline', 'get_traffic_meter_statistics'],
    'support_feature': [
        'Supported Features', '',
        'mdi:router-wireless-settings', 'getSupportFeatureListXML'],
    'bw_control': [
        'Bandwidth Control', '',
        'mdi:router-wireless-settings', 'get_bandwidth_control_options'],
    'qos_enabled': [
        'QOS Enabled', 'NewQoSEnableStatus',
        'mdi:router-wireless-settings', 'getQoSEnableStatus'],
    'mac_address': [
        'All MAC Addresses', '',
        'mdi:router-wireless-settings' 'get_all_mac_addresses'],
    'dns_masq': [
        'DNS Masq', '',
        'mdi:router-wireless-settings', 'get_dns_masq_device_id'],
    'traffic_meter_enabled': [
        'Traffic Meter Enabled', 'NewTrafficMeterEnable',
        'mdi:chart-areaspline', 'get_traffic_meter_enabled'],
    'traffic_meter_options': [
        'Traffic Meter Opt', 'NewControlOption',
        'mdi:chart-areaspline', 'get_traffic_meter_options'],
    'guest_access': [
        'Guest Access', 'NewGuestAccessEnabled',
        'mdi:account-group', 'get_guest_access_enabled'],
    'guest_access_5g': [
        '5G1 Guest Access', 'NewGuestAccessEnabled',
        'mdi:account-group', 'get_5g1_guest_access_enabled'],
    'guest_access_5g1': [
        '5G1 Guest Access2', 'NewGuestAccessEnabled',
        'mdi:account-group', 'get_5g1_guest_access_enabled_2'],
    'guest_access_5g2': [
        '5G1 Guest Access2', 'NewGuestAccessEnabled',
        'mdi:account-group', 'get_5g_guest_access_enabled_2'],
    'wpa_key': [
        'WPA Security Key', 'NewWPAPassphrase',
        'mdi:security', 'get_wpa_security_keys'],
    'wpa_key_5g': [
        '5G WPA Security Key', 'NewWPAPassphrase',
        'mdi:security', 'get_5g_wpa_security_keys'],
    'get_5g_info': [
        '5G Info', 'NewSSID',
        'mdi:signal-5g', 'get_5g_info'],
    'get_2g_info': [
        '2G Info', 'NewSSID',
        'mdi:signal-2g', 'get_2g_info'],
    'guest_access_net': [
        'Guest Network Info', 'NewSSID',
        'mdi:signal-2g', 'get_guest_access_network_info'],
    'guest_access_net_5g': [
        '5G Guest Network Info', 'NewSSID',
        'mdi:signal-5g', 'get_5g_guest_access_network_info'],
    'speed_test_result': [
        'Speed Test Result', 'NewOOKLADownlinkBandwidth',
        'mdi:speedometer', 'get_speed_test_result'],
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


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the sensor platform."""
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    ssl = config[CONF_SSL]
    resources = config[CONF_RESOURCES]

    _LOGGER.info("NETGEAR: setup_platform")

    sensors = []
    for kind in resources:
        sensors.append(NetgearEnhancedSensor(host, ssl, username, password, port, kind))

    add_devices(sensors, True)


class NetgearEnhancedSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, host, ssl, username, password, port, kind):  # noqa
        """Initialize the sensor."""
        # self._entity_id = ("ng_enhanced_%s", kind)
        self._name = SENSOR_TYPES[kind][0]
        self._state = None
        self._unit_of_measurement = ''
        self._state_key = SENSOR_TYPES[kind][1]
        self._attrs = None
        self._icon = SENSOR_TYPES[kind][2]
        self._function = SENSOR_TYPES[kind][3]

        from pynetgear_enhanced import Netgear
        self._api = Netgear(password, host, username, port, ssl)

    # def entity_id(self):
       # """Return the entity_id of the sensor."""
       # return self._entity_id

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

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Fetch new state and attributes for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self.response = getattr(self._api, self._function)()

        self._attrs = self.response
        if self._state_key:
            self._state = self.response[self._state_key]
        else:
            self._state = None
