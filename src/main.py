from machine import I2C, Pin
import json
import network
import utime as time
import urequests as requests
import ssd1306

# Read config
with open('config.json') as f:
    config = json.load(f)

# Initialise OLED
i2c = I2C(scl=Pin(config['scl_pin']), sda=Pin(config['sda_pin']))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
oled.fill(0)

def text_horiz_centred(fb, text, y, char_width=8):
    ''' Helper to display text horizontally centred '''
    fb.text(text, (fb.width - len(text) * char_width) // 2, y)

# Display a heading
char_height = 8
text_horiz_centred(oled, '-= City Temps =-', 10)
oled.show()

# Establish network connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config['ssid'], config['ssid_password'])

# Display a "Connecting to network" message
text_horiz_centred(oled, 'Connecting to', char_height * 6)
text_horiz_centred(oled, config['ssid'], char_height * 7)
oled.show()

while not wlan.isconnected():
    # TODO: Should timeout. How to handle timeout? Retry connect?
    time.sleep(1)

while True:
    # Query OpenWeatherMap for city temperatures
    api_root = 'https://api.openweathermap.org/data/2.5'
    api_params = '/group?id={},{}&units=metric&APPID={}'
    r = requests.get(api_root + api_params.format(config['city1_id'],
                                                  config['city2_id'],
                                                  config['appid']))
    # TODO Check return code. How to handle if not 200?
    # if r.status_code == 200:

    # Parse JSON for city names and temperatures
    city_temps = [(city['name'], city['main']['temp']) for city in r.json()['list']]
    r.close()
    start = time.ticks_ms()

    # Fill top half of display white, bottom half black
    oled.fill(1)
    oled.fill_rect(0, oled.height // 2, oled.width, oled.height, 0)

    # Display city names
    oled.text(city_temps[0][0], 5, 5, 0)
    oled.text(city_temps[1][0], 5, 36)

    # Display city temperatures
    oled.text('{:4.1f}'.format(city_temps[0][1]), 90, 11, 0)
    oled.text('{:4.1f}'.format(city_temps[1][1]), 90, 42, 1)

    # Draw full 'progress bar' on bottom line of display
    oled.line(0, oled.height - 1, oled.width, oled.height - 1, 1)

    oled.show()

    # Sleep, update progress
    while time.ticks_diff(time.ticks_ms(), start) < config['query_interval_sec'] * 1000:
        time.sleep(config['update_interval_sec'])
        next_query_percent = time.ticks_diff(time.ticks_ms(), start) / (config['query_interval_sec'] * 1000)
        oled.line(oled.width - int(oled.width * next_query_percent), oled.height - 1,
                  oled.width, oled.height - 1,
                  0)
        oled.show()