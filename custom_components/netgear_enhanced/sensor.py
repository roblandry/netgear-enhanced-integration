"""
Support for Netgear routers.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.netgear_enhanced/
"""
import logging

import voluptuous as vol
from datetime import timedelta

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD,
    CONF_SSL, CONF_RESOURCES, CONF_SCAN_INTERVAL
    )

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

VERSION = '0.2.0'

REQUIREMENTS = ['pynetgear-enhanced==0.2.2']

_LOGGER = logging.getLogger(__name__)

DEFAULT_HOST = '192.168.1.1'
DEFAULT_PORT = '5000'
DEFAULT_PREFIX = 'ng_enhanced'

SCAN_INTERVAL = timedelta(minutes=5)

SENSOR_TYPES = {
    'firmware': [
        'Firmware', 'CurrentVersion',
        'mdi:cellphone-link', 'check_new_firmware'],
    'check_app_fw': [
        'App Firmware', 'BlankState',
        'mdi:cellphone-link', 'check_app_new_firmware'],
    'get_device_config_info': [
        'Device Config', 'BlankState',
        'mdi:router-wireless-settings', 'get_device_config_info'],
    'access_control_on': [
        'Access Control Status', 'NewBlockDeviceEnable',
        'mdi:router-wireless-settings', 'get_block_device_enable_status'],
    'traffic_meter': [
        'Traffic Meter', 'NewTodayConnectionTime',
        'mdi:chart-areaspline', 'get_traffic_meter_statistics'],
    'traffic_meter_on': [
        'Traffic Meter Enabled', 'NewTrafficMeterEnable',
        'mdi:chart-areaspline', 'get_traffic_meter_enabled'],
    'traffic_meter_options': [
        'Traffic Meter Opt', 'NewControlOption',
        'mdi:chart-areaspline', 'get_traffic_meter_options'],
    # ---------------------
    # SERVICE_LAN_CONFIG_SECURITY
    # ---------------------
    'get_lan_config_info': [
        'LAN Config', 'NewLANIP',
        'mdi:router-wireless-settings', 'get_lan_config_sec_info'],
    # ---------------------
    # SERVICE_WAN_IP_CONNECTION
    # ---------------------
    'get_wan_ip_info': [
        'WAN Info', 'NewExternalIPAddress',
        'mdi:router-wireless-settings', 'get_wan_ip_con_info'],
    # ---------------------
    # SERVICE_PARENTAL_CONTROL
    # ---------------------
    'parental_control_on': [
        'Parental Control Enabled', 'ParentalControl',
        'mdi:router-wireless-settings', 'get_parental_control_enable_status'],
    'mac_address': [
        'All MAC Addresses', '',
        'mdi:router-wireless-settings', 'get_all_mac_addresses'],
    'dns_masq': [
        'DNS Masq', '',
        'mdi:router-wireless-settings', 'get_dns_masq_device_id'],
    # ---------------------
    # SERVICE_DEVICE_INFO
    # ---------------------
    'info': [
        'Info', 'ModelName',
        'mdi:router-wireless', 'get_info'],
    'supported_features': [
        'Supported Features', '',
        'mdi:router-wireless-settings', 'get_support_feature_list_XML'],
    #'attached_devices': [
    #    '', '',
    #    'mdi:', 'get_attached_devices'],
    #'attached_devices2': [
    #    '', '',
    #    'mdi:', 'get_attached_devices2'],
    # ---------------------
    # SERVICE_ADVANCED_QOS
    # ---------------------
    'speed_test_result': [
        'Speed Test Result', 'NewOOKLADownlinkBandwidth',
        'mdi:speedometer', 'get_speed_test_result', 'Mbps'],
    'qos_enabled': [
        'QOS Enabled', 'NewQoSEnableStatus',
        'mdi:router-wireless-settings', 'get_qos_enable_status'],
    'bw_control': [
        'Bandwidth Control', '',
        'mdi:router-wireless-settings', 'get_bandwidth_control_options'],
    # ---------------------
    # SERVICE_WLAN_CONFIGURATION
    # ---------------------
    '2g_guest_wifi_on': [
        '2G Guest Wifi', 'NewGuestAccessEnabled',
        'mdi:account-group', 'get_guest_access_enabled'],
    '5g_guest_wifi_on': [
        '5G Guest Wifi', 'NewGuestAccessEnabled',
        'mdi:account-group', 'get_5g_guest_access_enabled'],
    '2g_wpa_key': [
        'WPA Security Key', 'NewWPAPassphrase',
        'mdi:security', 'get_wpa_security_keys'],
    '5g_wpa_key': [
        '5G WPA Security Key', 'NewWPAPassphrase',
        'mdi:security', 'get_5g_wpa_security_keys'],
    '2g_wifi_info': [
        '2G Info', 'NewSSID',
        'mdi:signal-2g', 'get_2g_info'],
    '5g_wifi_info': [
        '5G Info', 'NewSSID',
        'mdi:signal-5g', 'get_5g_info'],
    'get_channel': [
        'Channel', 'NewChannel',
        'mdi:router-wireless-settings', 'get_available_channel'],
    '2g_guest_wifi_info': [
        '2G Guest Wifi Info', 'NewSSID',
        'mdi:signal-2g', 'get_guest_access_network_info'],
    '5g_guest_wifi_info': [
        '5G Guest Wifi Info', 'NewSSID',
        'mdi:signal-5g', 'get_5g_guest_access_network_info'],
    'get_smart_conn': [
        'Smart Connect', '',
        'mdi:router-wireless-settings', 'get_smart_connect_enabled'],
}


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({

    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_SSL, default=False): cv.boolean,
    vol.Optional(CONF_RESOURCES, default=['info']):
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
    scan_interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)

    _LOGGER.debug("NETGEAR: Setup Sensors")

    args = [password, host, username, port, ssl]
    sensors = []
    for kind in resources:
        sensors.append(NetgearEnhancedSensor(
            args, kind, scan_interval)
        )

    add_devices(sensors, True)


class NetgearEnhancedSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, args, kind, scan_interval):
        """Initialize the sensor."""
        self._name = SENSOR_TYPES[kind][0]
        self.entity_id = f"sensor.{DEFAULT_PREFIX}_{kind}"
        self._state = None
        self._state_key = SENSOR_TYPES[kind][1]
        self._attrs = None
        self._icon = SENSOR_TYPES[kind][2]
        self._function = SENSOR_TYPES[kind][3]
        self._scan_interval = scan_interval
        if len(SENSOR_TYPES[kind]) > 4:
            self._unit_of_measurement = SENSOR_TYPES[kind][4]
        else:
            self._unit_of_measurement = ''

        from pynetgear_enhanced import NetgearEnhanced
        self._api = NetgearEnhanced(
            args[0], args[1], args[2], args[3], args[4]
            )

        self.update()

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

    def update(self):
        """Fetch new state and attributes for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self.response = getattr(self._api, self._function)()

        if self.response:
            if len(self.response) > 1:
                self._attrs = self.response

            if self._state_key:
                self._state = self.response[self._state_key]
        else:
            self._state = None
