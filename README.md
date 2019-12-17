# piface-mqtt

## requirements

`sudo apt-get install screen python-pip python-pifacedigitalio`

`pip install paho-mqtt`

## patch for old pifaces

change `/usr/lib/python2.7/dist-packages/pifacecommon/spi.py` to 15000 HZ (see https://github.com/piface/pifacedigitalio/issues/36)

	# create the spi transfer struct
    transfer = spi_ioc_transfer(
        tx_buf=ctypes.addressof(wbuffer),
        rx_buf=ctypes.addressof(rbuffer),
        len=ctypes.sizeof(wbuffer),
        speed_hz=ctypes.c_uint32(15000)
    )
	
## checkout

```
cd /home/pi/
wget -O mqtt.py "https://raw.githubusercontent.com/ckarrie/piface-mqtt/master/mqtt_client.py"
```

## make permanent

as user pi:

`crontab -e`

`@reboot  sleep 60 && /usr/bin/screen -dmS py_mqtt python /home/pi/mqtt.py`


## MQTT structure

```
winden/
  <hostname>/
    piface/
      in/
        <port>		Values: "ON" or "OFF"
      out/
        <port>		Values: "ON" or "OFF"
```

## settings in iobroker:

**Instanzen** -> mqtt-client.0 -> zusätzl. Subscriptions: `winden/#`

Damit der Weg iobroker -> piface funktioniert, muss unter **Objekte** `mqtt-client.0.winden.<hostname>.piface.out` unter Einstellung der Haken bei **publish** gesetzt werden.

[Imgur](https://imgur.com/R0b1sYs)
![Instanzen](https://i.imgur.com/R0b1sYs.png)
