
![City Temps Example](images/citytemps.gif)

## Installation

Modify `src/config.json` to suit your installation then copy the contents of `src` to the root of a MicroPython-enabled device.
The device should have an SSD1306-powered I2C display and be wifi-capable.

Tested on a Wemos with OLED display (as pictured).

Copying the files to the device is easy with [rshell](https://github.com/dhylands/rshell):

```sh
>matt:~/code/micropython-citytemps-demo/$ rshell -p /dev/ttyUSB0 rsync . /pyboard
```

## Configuration

A configuration file is supplied in JSON format. Default contents are:

```json
{
    "ssid": "TestNetwork",
    "ssid_password": "TestNetworkPassword",
    "appid": "b1b15e88fa797225412429c1c50c122a1",    
    "city1_id": 7286283,
    "city2_id": 2158177,
    "query_interval_sec": 30,
    "update_interval_sec": 1,
    "scl_pin": 4,
    "sda_pin": 5
}
```
### Network config

Set `ssid` and `ssid_password` to match your wifi network.

### OpenWeatherMap API config

_City Temps_ uses [OpenWeatherMap](https://openweathermap.org/)'s [API](https://openweathermap.org/api) to provide the temperature data. OpenWeatherMap requires users of the API to register for an API key so follow [How to Start](https://openweathermap.org/appid) to grab a key. Use of the API is free with some [very reasonable constraints](https://openweathermap.org/price).

When you've registered for a key you need to configure `appid` with it.

Now, since we're querying for temperature data for two cities we need to configure _which_ two cities. We're using OpenWeatherMap's [By city ID](https://openweathermap.org/current#cityid) API - it allows us to query city data using a unique ID for each city in their system. By default `city1_id` is Lausanne, Switzerland, `city2_id` Melbourne, Australia.

### Display config

_City Temps_ expects a 128x64 SSD1306 display to be connected via I2C. The default configuration matches the Wemos device that uses pins 4 and 5. If your configuration differs then `scl_pin` and `sda_pin` will require modification.

### Interval config

`query_interval_sec` determines the seconds between querying OpenWeatherMap for updated temperature data. OpenWeatherMap indicate that their data typically updates every ten minutes so the default of 30 seconds may be a little aggressive (but is useful for a demo!). 

`update_interval_sec` configures how often the progress bar is updated.