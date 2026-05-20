Installation
============

Dependencies
------------

.. include:: requirements.rst

.. note::

    Python 3.11 and PyQt5 are the reference for production release


How to install
--------------

Wheel package:
^^^^^^^^^^^^^^

On any operating system, using pip and the Wheel package is the easiest way to
install ModuleTester on an existing Python distribution:

.. code-block:: console

    $ pip install --upgrade ModuleTester-1.0.0-py2.py3-none-any.whl

ModuleTester uses Pandoc and PyPandoc bindings to generate documents and display test
descriptions. You can get `Pandoc <https://pandoc.org/installing.html>`_ from
`here <https://pandoc.org/installing.html>`_ or by executing the following python code (
All instructions are available on the
`PyPandoc documentation <https://pypi.org/project/pypandoc/>`_).

.. code-block:: python

    pip install pypandoc
    from pypandoc.pandoc_download import download_pandoc
    # see the documentation how to customize the installation path
    # but be aware that you then need to include it in the `PATH`
    download_pandoc()
    # check the install path with
    print(pypandoc.get_pandoc_path())



Source package:
^^^^^^^^^^^^^^^

Installing ModuleTester directly from the source package is straigthforward:

.. code-block:: console

    $ python -m build
