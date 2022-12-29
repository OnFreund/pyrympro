# pyrympro

A python library to communicate with [Read Your Meter Pro](https://rym-pro.com/).

## Installation

You can install pyvolumio from [PyPI](https://pypi.org/project/pyvolumio/):

    pip3 install pyrympro

Python 3.7 and above are supported.


## How to use

### Initialize

**With predefined client session**

```python
import aiohttp
from pyrympro.rympro import RymPro

session = aiohttp.ClientSession()
rym = RymPro(session)
```

**Let client generate session**
```python
from pyrympro.rympro import RymPro

rym = RymPro() 
```

### Initialize client and login
```python
from pyrympro.rympro import RymPro

rym = RymPro() 
await rym.initialize("<username>", "<password>")
```

### Get the latest details
```python
from pyrympro.rympro import RymPro

rym = RymPro() 
await rym.initialize("<username>", "<password>")

await rym.update()

print(f"profile: {rym.profile}")
print(f"meters: {rym.meters}")
print(f"customer_service: {rym.customer_service}")
print(f"settings: {rym.settings}")
```

### Set alerts for leaks in all channels
```python
from pyrympro.helpers.enums import MediaTypes, AlertTypes
from pyrympro.rympro import RymPro

rym = RymPro() 
await rym.initialize("<username>", "<password>")

await rym.update()

print(f"settings: {rym.settings}")

await rym.set_alert_settings(AlertTypes.LEAK, MediaTypes.ALL, True)

print(f"settings: {rym.settings}")
```

**Channels**

- None (MediaTypes.NONE)
- Email (MediaTypes.EMAIL)
- SMS (MediaTypes.SMS)
- All (MediaTypes.ALL)

**Alert Types**
- Daily exception (AlertTypes.DAILY_EXCEPTION)
- Leak (AlertTypes.LEAK)
- Consumption identified will away or vacation (AlertTypes.CONSUMPTION_WHILE_AWAY)