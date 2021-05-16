# This is script that run when device boot up or wake from sleep.
import gc
import network
import esp
esp.osdebug(None)
gc.collect()

ssid = 'CANALBOX-7652'
password = '4082665619'

sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect('CANALBOX-7652', '4082665619')
    while not sta_if.isconnected():
        pass
print('network config:', sta_if.ifconfig())
