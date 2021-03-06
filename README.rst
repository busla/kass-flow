
Kass Flow
=========

Helper for the `KASS <https://www.kass.is/>`_ payment gateway. Written for python 3.8.5 (probably works on versions >= 3.6).

See the `KASS API docs <https://kass.github.io/api/>`_ for more info.

This module is not affiliated with KASS.

TODO
----


* [x] Create payment
* [ ] Retreive payment info
* [ ] Retreive payment status
* [ ] Cancel payment
* [ ] Add concurrency with RQ when dispatching multiple payments

Usage
-----

Here is a short guide to get you started.

This will dispatch a payment to the KASS API.

.. code-block:: sh

   poetry add kass-flow
   # or
   pip install kass-flow

.. code-block:: python

   from kass_flow.kass import KassBilling
   from kass_flow.interfaces import KassRequestPaymentDict

   kass_token: str = "some-token"
   kass_url: str = "https://api.kass.is/v1/payments"
   instance = KassBilling(kass_token, kass_url)

   payload: KassRequestPaymentDict = {
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

When the recipient cancels or pays the requested order KASS will send a callback to the ``notify_url``\ , which you need to catch on your server and probably validate the signature that is included in the POST payload.

At some point in time the user will pay/reject the requested order. Here is an example on how to validate the payload.

.. code-block:: python

   from kass_flow.kass import KassBilling
   from kass_flow.interfaces import KassRequestPaymentDict

   def some_view_that_handles_kass_callback(request):
       payload = request.data
       kass_token: str = "some-token"
       kass_url: str = "https://api.kass.is/v1/payments"
       instance = KassBilling(kass_token, kass_url)

       if instance.is_signature_valid(payload):
           # process the payload.

Development
-----------

.. code-block:: sh

   pip install poetry
    # to manage envs yourself
   poetry config virtualenvs.create false
   poetry install
   pytest tests

If you are using VSCode for development there is a ``.vscode/settings.example.json`` for sensible defaults. Since mypy is used you need to install the ``mypyls`` language server.

.. code-block::

   poetry install "https://github.com/matangover/mypyls/archive/master.zip#egg=mypyls[default-mypy]"
   # or
   pip install "https://github.com/matangover/mypyls/archive/master.zip#egg=mypyls[default-mypy]"
