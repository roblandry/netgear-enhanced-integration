# Supported #
**The supported sensors are:**
* Firmware
* App Firmware :new:
* Device Config :new:
* Access Control Status
* Traffic Meter
* Traffic Meter Enabled
* Traffic Meter Opt
* LAN Config :new:
* WAN Info :new:
* Parental Control Enabled
* All MAC Addresses
* DNS Masq
* Info
* Supported Features
* Speed Test Result
* QOS Enabled
* Bandwidth Control
* 2G Guest Wifi
* 5G Guest Wifi
* WPA Security Key
* 5G WPA Security Key
* 2G Info
* 5G Info
* Channel :new:
* 2G Guest Wifi Info
* 5G Guest Wifi Info
* Smart Connect :new:


**The supported switches are:**
* Access Control
* Traffic Meter
* Parental Control
* QOS
* 2.4g Guest WiFi
* 5g Guest WiFi
* Run Speed Test (switch will always toggle to off)
* Reboot Router (switch will always toggle to off)


# Setup #
* Create the netgear_enhanced folder in custom_components.
* Copy the files to the netgear_enhanced folder.

## For sensors ##
* Place the following code in your config under sensor:
  * Make sure to modify the parameters to fit your needs. It may cause some strain to have too many sensors polling data.

```yaml
  - platform: netgear_enhanced
    host: !secret my_secret_ip
    username: !secret my_secret_netgear_user
    password: !secret my_secret_netgear_pass
    resources:
      - firmware
      - check_app_fw
      - get_device_config_info
      - access_control_on
      - traffic_meter
      - traffic_meter_on
      - traffic_meter_options
      - get_lan_config_info
      - get_wan_ip_info
      - parental_control_on
      - mac_address
      - dns_masq
      - info
      - supported_features
      - speed_test_result
      - qos_enabled
      - bw_control
      - 2g_guest_wifi_on
      - 5g_guest_wifi_on
      - 2g_wpa_key
      - 5g_wpa_key
      - 2g_wifi_info
      - 5g_wifi_info
      - get_channel
      - 2g_guest_wifi_info
      - 5g_guest_wifi_info
      - get_smart_conn
```

## For switches ##
* Place the following code in your config under switch:
  * Make sure to modify the parameters to fit your needs. There may be some delay in updating the switch due to the router changing configuration.

```yaml
  - platform: netgear_enhanced
    host: !secret my_secret_ip
    username: !secret my_secret_netgear_user
    password: !secret my_secret_netgear_pass
    resources:
      - 'access_control'
      - 'traffic_meter'
      - 'parental_control'
      - 'qos'
      - '2g_guest_wifi'
      - '5g_guest_wifi'
      - 'run_speed_test'
      - 'reboot'
```