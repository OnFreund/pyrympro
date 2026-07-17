## Status
[![Build Status](https://github.com/OnFreund/pyrympro/actions/workflows/ci.yml/badge.svg)](https://github.com/OnFreund/pyrympro/actions/workflows/ci.yml)

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

## Testing PRs

Every pull request automatically publishes a test build as a GitHub pre-release. You can find the install command in the PR comment posted by the bot, or on the [Releases page](https://github.com/OnFreund/pyrympro/releases) (pre-releases are tagged `pr-{number}`).

**pip:**
```
pip install https://github.com/OnFreund/pyrympro/releases/download/pr-42/pyrympro-0.0.0.dev42-py3-none-any.whl
```

**Home Assistant** — temporarily update the `rympro` integration's `manifest.json` to use the PEP 508 URL form so HA doesn't overwrite it on restart:
```json
{
  "requirements": ["pyrympro @ https://github.com/OnFreund/pyrympro/releases/download/pr-42/pyrympro-0.0.0.dev42-py3-none-any.whl"]
}
```
Replace `42` with the actual PR number. Revert to the pinned version (e.g. `pyrympro==0.0.9`) after testing.

The install URL is stable for the lifetime of the PR — new commits to the same PR reuse the same tag and wheel name, so you don't need to update `manifest.json` if more commits are pushed.

The pre-release and comment are deleted automatically when the PR is merged or closed.