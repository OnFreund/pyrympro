# pyrympro

A python library to communitcate with [Read Your Meter Pro](https://rym-pro.com/).

## Installation

You can install pyvolumio from [PyPI](https://pypi.org/project/pyvolumio/):

    pip3 install pyrympro

Python 3.7 and above are supported.


## How to use

```python
from pyrympro import RymPro
rym = RymPro()
# you can also pass in your own session
rym = RymPro(session)

# device_id can be anything you choose
await rym.login("<email>", "<password>", "<device_id>")
info = await rym.account_info()
meter_reads = await rym.last_read()
...
```