from machine import I2C, Pin
import json
import network
import utime as time
import urequests as requests
import ssd1306

# Initialise OLED
i2c = I2C(scl=Pin(4), sda=Pin(5))
screen_width, screen_height = 128, 64
oled = ssd1306.SSD1306_I2C(screen_width, screen_height, i2c)
oled.fill(0)

# Display a heading
text_height = 8
heading_padding = 10
heading = '-= City Temps =-'
oled.text(heading,
          (screen_width - len(heading) * text_height) // 2,
          heading_padding)
oled.show()

# Read config
with open('config.json') as f:
    config = json.load(f)

# Establish network connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config['ssid'], config['ssid_password'])

connecting = 'Connecting to'
oled.text(connecting,
          (screen_width - len(connecting) * text_height) // 2,
          text_height * 6)
oled.text(config['ssid'],
          (screen_width - len(config['ssid']) * text_height) // 2,
          text_height * 7)
oled.show()

while not wlan.isconnected():
    # TODO: Should timeout
    time.sleep(1)

while True:
    print('Query Weather Map')
    # Query OpenWeatherMap for city temperatures
    api_root = 'https://api.openweathermap.org/data/2.5'
    r = requests.get(api_root + '/group?id={},{}&units=metric&APPID={}'.format(config['city1_id'],
                                                                               config['city2_id'],
                                                                               config['appid']))
    # TODO: Check response code
    # Parse JSON for city names and temperatures
    city_temps = [(city['name'], city['main']['temp']) for city in r.json()['list']]
    start_time = time.ticks_ms()

    oled.fill(1)
    oled.fill_rect(0, 31, 128, 62, 0)
    oled.text(city_temps[0][0], 5, 5, 0)
    oled.text(city_temps[1][0], 5, 36)
    oled.line(0, 63, 128, 63, 1)

    oled.text('{:4.1f}'.format(city_temps[0][1]), 90, 11, 0)
    oled.text('{:4.1f}'.format(city_temps[1][1]), 90, 42, 1)

    oled.show()

    while time.ticks_ms() - start_time < config['query_interval_sec'] * 1000:
        # Update progress, sleep
        time.sleep(config['update_interval_sec'])
        next_query_percent = (time.ticks_ms() - start_time) / (config['query_interval_sec'] * 1000)
        oled.line(128 - int(128 * next_query_percent), 63, 128, 63, 0)
        oled.show()