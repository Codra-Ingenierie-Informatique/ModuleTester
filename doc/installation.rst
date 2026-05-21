Installation
============

Dependencies
------------

.. include:: requirements.rst

.. note::

    Python 3.9+ is required. PyQt5 or PySide2 can be used as Qt binding
    (through `QtPy <https://pypi.org/project/QtPy/>`_).


How to install
--------------

From PyPI:
^^^^^^^^^^

The easiest way to install ModuleTester is from PyPI:

.. code-block:: console

    $ pip install ModuleTester

From a wheel package:
^^^^^^^^^^^^^^^^^^^^^

On any operating system, using pip and the Wheel package:

.. code-block:: console

    $ pip install --upgrade moduletester-1.0.0-py3-none-any.whl

Pandoc (optional):
^^^^^^^^^^^^^^^^^^

ModuleTester uses Pandoc and PyPandoc bindings to generate documents and display test
descriptions. You can get `Pandoc <https://pandoc.org/installing.html>`_ from
`here <https://pandoc.org/installing.html>`_ or by executing the following python code
(all instructions are available on the
`PyPandoc documentation <https://pypi.org/project/pypandoc/>`_).

.. code-block:: python

    import pypandoc
    from pypandoc.pandoc_download import download_pandoc
    # see the documentation how to customize the installation path
    # but be aware that you then need to include it in the `PATH`
    download_pandoc()
    # check the install path with
    print(pypandoc.get_pandoc_path())


From source:
^^^^^^^^^^^^

Installing ModuleTester directly from the source package is straightforward:

.. code-block:: console

    $ pip install .

Or to build a distribution package:

.. code-block:: console

    $ python -m build
