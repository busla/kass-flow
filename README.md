# Kass Flow

Helper for the [KASS](https://www.kass.is/) payment gateway. Written for python 3.8.5 (probably works on versions >= 3.6).

## TODO

- [x] Create payment
- [ ] Retreive payment info
- [ ] Retreive payment status
- [ ] Cancel payment
- [ ] Add concurrency with RQ when dispatching multiple payments

## Usage

```python
from kass_flow import kass

kass_token = "some-token"
kass_url = "https://api.kass.is/v1/payments"
instance = kass.KassBilling(kass_token, kass_url)

payload = {
    "amount": 2199,
    "description": "Kass bolur",
    "image_url": "https://photos.kassapi.is/kass/kass-bolur.jpg",
    "order": "ABC123",
    "recipient": "7798217",
    "terminal": 1,
    "expires_in": 90,
    "notify_url": "https://example.com/callbacks/kass",
}

result, is_valid = instance.dispatch(payload)
```

## Development

```sh
pip install poetry
 # to manage envs yourself
poetry config virtualenvs.create false
poetry install
pytest tests
```

If you are using VSCode for development there is a `.vscode/settings.example.json` for sensible defaults. Since mypy is used you need to install the `mypyls` language server.

```
poetry install "https://github.com/matangover/mypyls/archive/master.zip#egg=mypyls[default-mypy]"
# or
pip install "https://github.com/matangover/mypyls/archive/master.zip#egg=mypyls[default-mypy]"
```
