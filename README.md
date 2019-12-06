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
	

	