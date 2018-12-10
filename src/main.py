from machine import I2C, Pin
import json
import network
import urequests as requests
import ssd1306

# Initialise OLED
i2c = I2C(scl=Pin(4), sda=Pin(5))
screen_width, screen_height = 128, 64
oled = ssd1306.SSD1306_I2C(screen_width, screen_height, i2c)
oled.fill(0)

# Display a heading
text_height = 8
heading = 'City Temps'
oled.text(heading,
          screen_width // 2 - len(heading) * text_height // 2,
          screen_height // 2 - text_height // 2)
oled.show()

# Read config
with open('config.json') as f:
    config = json.load(f)

# Establish network connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config['ssid'], config['ssid_password'])

# Query OpenWeatherMap for city temperatures
api_root = 'https://api.openweathermap.org/data/2.5'
r = requests.get(api_root + '/group?id={},{}&units=metric&APPID={}'.format(config['city1_id'], 
                                                                           config['city2_id'],
                                                                           config['appid']))
# Parse JSON for city names and temperatures
city_temps = [(city['name'], city['main']['temp']) for city in r.json()['list']]

oled.fill(1)
oled.fill_rect(0, 31, 128, 62, 0)
oled.text(city_temps[0][0], 5, 5, 0)
oled.text(city_temps[1][0], 5, 36)
oled.line(0, 63, 128, 63, 1)

oled.text('{:4.1f}'.format(city_temps[0][1]), 90, 11, 0)
oled.text('{:4.1f}'.format(city_temps[1][1]), 90, 42, 1)

oled.show()
