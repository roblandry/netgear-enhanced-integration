"""
Support for Netgear routers.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/device_tracker.netgear_enhanced/
"""
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.device_tracker import (
    DOMAIN, PLATFORM_SCHEMA, DeviceScanner)
from homeassistant.const import (
    CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_PORT, CONF_SSL,
    CONF_DEVICES, CONF_EXCLUDE)

VERSION = '0.2.0'

REQUIREMENTS = ['pynetgear-enhanced==0.2.2']

_LOGGER = logging.getLogger(__name__)

CONF_APS = 'accesspoints'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_HOST, default=''): cv.string,
    vol.Optional(CONF_SSL, default=False): cv.boolean,
    vol.Optional(CONF_USERNAME, default=''): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_PORT, default=None): vol.Any(None, cv.port),
    vol.Optional(CONF_DEVICES, default=[]):
        vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(CONF_EXCLUDE, default=[]):
        vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(CONF_APS, default=[]):
        vol.All(cv.ensure_list, [cv.string]),
})


def get_scanner(hass, config):
    """Validate the configuration and returns a Netgear scanner."""
    info = config[DOMAIN]
    host = info.get(CONF_HOST)
    ssl = info.get(CONF_SSL)
    username = info.get(CONF_USERNAME)
    password = info.get(CONF_PASSWORD)
    port = info.get(CONF_PORT)
    devices = info.get(CONF_DEVICES)
    excluded_devices = info.get(CONF_EXCLUDE)
    accesspoints = info.get(CONF_APS)

    scanner = NetgearDeviceScanner(host, ssl, username, password, port,
                                   devices, excluded_devices, accesspoints)

    return scanner if scanner.success_init else None


class NetgearDeviceScanner(DeviceScanner):
    """Queries a Netgear wireless router using the SOAP-API."""

    def __init__(self, host, ssl, username, password, port, devices,
                 excluded_devices, accesspoints):
        """Initialize the scanner."""
        from pynetgear_enhanced import NetgearEnhanced

        self.tracked_devices = devices
        self.excluded_devices = excluded_devices
        self.tracked_accesspoints = accesspoints

        self.last_results = []
        self._api = NetgearEnhanced(password, host, username, port, ssl)

        _LOGGER.info("Logging in")

        results = self.get_attached_devices()

        self.success_init = results is not None

        if self.success_init:
            self.last_results = results
        else:
            _LOGGER.error("Failed to Login")

    def scan_devices(self):
        """Scan for new devices and return a list with found device IDs."""
        self._update_info()

        devices = []

        for dev in self.last_results:
            tracked = (not self.tracked_devices or
                       dev.mac in self.tracked_devices or
                       dev.name in self.tracked_devices)
            tracked = tracked and (not self.excluded_devices or not(
                dev.mac in self.excluded_devices or
                dev.name in self.excluded_devices))
            if tracked:
                devices.append(dev.mac)
                if (self.tracked_accesspoints and
                        dev.conn_ap_mac in self.tracked_accesspoints):
                    devices.append(dev.mac + "_" + dev.conn_ap_mac)

        return devices

    def get_device_name(self, device):
        """Return the name of the given device or the MAC if we don't know."""
        parts = device.split("_")
        mac = parts[0]
        ap_mac = None
        if len(parts) > 1:
            ap_mac = parts[1]

        name = None
        for dev in self.last_results:
            if dev.mac == mac:
                name = dev.name
                break

        if not name or name == "--":
            name = mac

        if ap_mac:
            ap_name = "Router"
            for dev in self.last_results:
                if dev.mac == ap_mac:
                    ap_name = dev.name
                    break

            return name + " on " + ap_name

        return name

    def _update_info(self):
        """Retrieve latest information from the Netgear router.

        Returns boolean if scanning successful.
        """
        if not self.success_init:
            return

        _LOGGER.info("Scanning")

        results = self.get_attached_devices()

        if results is None:
            _LOGGER.warning("Error scanning devices")

        self.last_results = results or []

    def get_attached_devices(self):
        """
        List attached devices with pynetgear.

        The v2 method takes more time and is more heavy on the router
        so we only use it if we need connected AP info.
        """
        if self.tracked_accesspoints:
            return self._api.get_attached_devices_2()

        return self._api.get_attached_devices()
