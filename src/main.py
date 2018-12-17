from machine import I2C, Pin
import json
import network
import utime as time
import urequests as requests
import ssd1306

# Read config
with open('config.json') as f:
    config = json.load(f)
    assert len(config['city_ids']) <= 4 # Only four cities will fit on the display

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
    api_params = '/group?id={}&units=metric&APPID={}'
    r = requests.get(api_root + api_params.format(','.join(str(c) for c in config['city_ids']),
                                                  config['appid']))
    # TODO Check return code. How to handle if not 200?
    # if r.status_code == 200:

    # Parse JSON for city names and temperatures
    city_temps = [{'name': city['name'], 'temperature': city['main']['temp']} for city in r.json()['list']]
    r.close()
    start = time.ticks_ms()

    oled.fill(0)
    for city_n, city in enumerate(city_temps):
        panel_height = oled.height // len(city_temps)
        panel_top = panel_height * city_n
        text_colour = city_n % 2 ^ len(city_temps) % 2 # The last panel should have a black background

        # Draw panel background
        oled.fill_rect(0, panel_top,                         # x1, y1
                       oled.width, panel_top + panel_height, # x2, y2 
                       text_colour ^ 1)                      # colour

        # Display city name (up to 10 characters - to avoid overwriting temperature)
        oled.text(city['name'][:10], 5, panel_top + (panel_height - char_height) // 2, text_colour)

        # Display city temperatures
        oled.text('{:4.1f}'.format(city['temperature']), 90, panel_top + (panel_height - char_height) // 2, text_colour)

    # Draw full 'progress bar' on bottom line of display
    oled.line(0, oled.height - 1, oled.width, oled.height - 1, 1)

    oled.show()

    # Sleep, update progress
    while time.ticks_diff(time.ticks_ms(), start) < config['query_interval_sec'] * 1000:
        time.sleep(config['update_interval_sec'])
        next_query_percent = time.ticks_diff(time.ticks_ms(), start) / (config['query_interval_sec'] * 1000)
        oled.line(oled.width - int(oled.width * next_query_percent), oled.height - 1, # x
                  oled.width, oled.height - 1, # y
                  0) # colour
        oled.show()