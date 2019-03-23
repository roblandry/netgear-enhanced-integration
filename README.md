# Supported #
**The supported sensors are:**
* Check Firmware
* Access Control Status
* Traffic Meter Statistics
* Traffic Meter Status
* Traffic Meter Options
* Parental Control Enabled
* MAC Addresses
* DNS Masq # Not currently working correctly
* Get Router Info
* Supported Features
* Speed Test Resluts
* QOS Enabled
* Bandwidth Control
* 2.4g Guest Access Status
* 5g Guest Access Status
* 2.4g WPA Key
* 5g WPA Key
* 2.4g Wifi Info
* 5g Wifi Info
* 2.4g Guest Wifi Info
* 5g Guest Wifi Info


**The supported switches are:**
* Access Control
* Traffic Meter
* Parental Control
* QOS
* 2.4g Guest WiFi
* 5g Guest WiFi
* Run Speed Test (switch will always toggle to off)


# Setup #
* Create the netgear_enhanced folder in custom_components.
* Copy the sensor.py and switch.py files to the netgear_enhanced folder.

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
      - access_control_on
      - traffic_meter
      - traffic_meter_on
      - traffic_meter_options
      - parental_control_on
      - mac_address
      #- dns_masq
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
      - 2g_guest_wifi_info
      - 5g_guest_wifi_info
```

## For switches ##
* Place the following code in your config under switch:
  * Make sure to modify the parameters to fit your needs. There may be some delay in updating the switch due to the router changing configuration.

```yaml
  - platform: netgear_enhanced
    host: !secret my_secret_ip
    username: !secret my_secret_netgear_user
    password: !secret my_secret_netgear_pass
```