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
mkdir ~/src/
cd ~/src/
git clone https://github.com/ckarrie/piface-mqtt
ln -s /home/pi/src/piface-mqtt/mqtt_client.py /home/pi/mqtt.py
```

## update source
```
cd ~/src/
git pull
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

## settings in home-assistant.io

Einstellungen -> Integrationen -> Plus-Button:

- MQTT Borker Daten eingeben
- Haken bei "Suche"

Hinweis: ich habe sämtliche manuelle MQTT-Einträge in der *.homeassistant/configuration.yaml* entfernt

[Imgur](https://imgur.com/CNGcHDi)
![Instanzen](https://i.imgur.com/CNGcHDi.png)

[Imgur](https://imgur.com/pMCjYdf)
![Instanzen](https://i.imgur.com/pMCjYdf.png)
