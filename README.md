## Setup ##
* Create the netgear_enhanced folder in custom_components.
* Place the sensor.py in the netgear_enhanced folder.
* Place the following code in your config under sensor:
  * Make sure to modify the parameters to fit your needs. It may cause some strain to have too many sensors polling data.

## Currently supported sensors ##
```yaml
  - platform: netgear_enhanced
    host: !secret my_secret_ip
    username: !secret my_secret_netgear_user
    password: !secret my_secret_netgear_pass
    resources:
      - check_fw
      - traffic_meter
      - traffic_meter_enabled
      - traffic_meter_options
      - parental_control_status
      - mac_address
      #- dns_masq
      - info
      - support_feature
      - speed_test_result
      - qos_enabled
      - bw_control
      - guest_access
      - guest_access_5g
      - wpa_key
      - wpa_key_5g
      - get_2g_info
      - get_5g_info
      - guest_access_net
      - guest_access_net_5g
```