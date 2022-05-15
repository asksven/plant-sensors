# Fetch data from miflora sensors

This is a little home project I did to fetch the data from a bunch of BLE plant sensors.

## Identify MAC addresses

This assumes you already have miflora sensors set-up and installed for some plants.

To retrieve the bluetooth LE mac-adresses of the miflora sensors run:

```
sudo hcitool lescan
```

This will return a list looking like this:

```
...
80:EA:CA:89:xx:xx Flower care
...
80:EA:CA:89:xx:xx Flower care
...
80:EA:CA:89:xx:xx Flower care
80:EA:CA:89:xx:xx Flower care
80:EA:CA:89:xx:xx Flower care
```

Note that the vendor name as well as the 4 first bytes may vary. For more information about how bluetooth MAC addresses are structured see [here](https://macaddresschanger.com/what-is-bluetooth-address-BD_ADDR)

## Install dependencies

Run `pip install -r requirements.txt`

## Configure

1. Copy `input_template.json` to `input.json` and add your sensors there
1. Copy `setenv_template` to `setenv` and configure your influxdb there

## Run

```
source setenv
python poller.py
```

Once you have tested everything you can add it as a scheduled cronjob, e.g. to run every 15 minutes.

Open your cron-config: `crontab -e`, and add this:

```
*/15 * * * * cd /home/pi/git/plant-sensors && ./run.sh
```

`run.sh` is just a wrapper that writes the output to `logs`. Once your setup runs properly you can remove the logging part.
