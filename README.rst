ProlixPy
========

Experiments in stenography in Python

Prequisites
-----------

For local testing, a running Redis instance.

Installation
------------

From the root of this repo:

`python3 setup.py install`

Usage examples
--------------

API in preparation. Meanwhile ...

*To get an obscured message*

from prolix import steno

steno = steno.Steno()
results = steno.obscure(text=clear_text, expiration_secs=30)
key = results['key']
obscured_text = results['obscured_text']

The key is valid for expiration_secs seconds.

*To clarify the message*

from prolix import steno

steno = steno.Steno()
results = steno.clarify(key=key, text=obscured_text)
clarified_text = results['clarified_text']

Once the key has expired, the text cannot (ever) be clarified by anyone.
The clarified text is not stored anywhere.
