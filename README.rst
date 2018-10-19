ProlixPy
========

Experiments in stenography in Python

Prequisites
-----------

For local testing

* Running Redis instance.
* Flask package installed (pip3 install Flask)

Installation
------------

From the root of this repo:

::

    pip3 install .

Usage examples
--------------

*To get an obscured message*

::

    import prolix
    prolix_api = prolix.api()

    clear_text = "Mary had a little lamb whose fleece was white as snow"
    results = prolix_api.obscure(text=clear_text)
    key = results['key']
    obscured_text = results['obscured_text']

The key is valid for expiration_secs seconds.

*To clarify the message*

::

    import prolix
    prolix_api = prolix.api()

    results = prolix_api.clarify(key=key, text=obscured_text)
    clarified_text = results['clarified_text']

Once the key has expired, the text cannot (ever) be clarified by anyone.
The clarified text is not stored anywhere.

Demo server
-----------

::

    prolix

Go to local server_

.. _server: http://127.0.0.1:5000

