FAQ & Troubleshooting
=====================


No tests found after loading a package
---------------------------------------

**Symptom**: ModuleTester opens but the tree view is empty.

**Cause**: Test scripts must contain the ``# guitest: show`` annotation for
ModuleTester to discover them.

**Fix**: Add the following comment at the top of each test file:

.. code-block:: python

   # guitest: show

Alternatively, set ``category = all`` in the ``[general]`` section of
``moduletester.ini`` to load every script regardless of annotations.

See :doc:`user_guide` for more details on test discovery.


Pandoc not found
----------------

**Symptom**: Export fails with a message about Pandoc not being available.

**Cause**: ModuleTester uses `Pandoc <https://pandoc.org/>`_ (via
`pypandoc <https://pypi.org/project/pypandoc/>`_) to convert reports to
DOCX, ODT, PDF, and other formats.

**Fix**: Install Pandoc using one of these methods:

.. code-block:: python

   import pypandoc
   from pypandoc.pandoc_download import download_pandoc
   download_pandoc()

Or download it directly from https://pandoc.org/installing.html.

After installation, verify with:

.. code-block:: python

   import pypandoc
   print(pypandoc.get_pandoc_path())


Configuration conflict error
-----------------------------

**Symptom**: ``ConfigConflictError`` when loading a package.

**Cause**: The ``moduletester.ini`` file contains keys that do not match the
expected configuration schema — either unknown keys or missing required keys
(e.g. after upgrading ModuleTester).

**Fix**: Delete or rename the ``moduletester.ini`` file and let ModuleTester
recreate it with default values. Alternatively, edit the file to match the
expected options listed in :doc:`configuration`.


Invalid path in configuration
------------------------------

**Symptom**: ``InvalidPathError`` when loading a package.

**Cause**: A path option in ``moduletester.ini`` (``template_dir``,
``docx_reference``, ``odt_reference``, ``css_style``, or a template name)
points to a file or directory that does not exist.

**Fix**: Check that all paths in the ``[export]`` section are correct and
that the referenced files exist. Relative paths are resolved from the
package directory.


Export produces empty or broken output
--------------------------------------

**Symptom**: The exported document is empty, malformed, or missing styles.

**Possible causes**:

- Pandoc is not installed (see above).
- The CSS stylesheet or reference document is missing or corrupted.
- A custom template has a Jinja2 syntax error.

**Fix**:

1. Verify Pandoc is installed and accessible.
2. Reset to default templates by removing the ``template_dir`` option from
   ``moduletester.ini``.
3. Check the application console for Jinja2 error messages.
4. Set ``reload_templates_on_export = 1`` in ``moduletester.ini`` to force
   template reloading during development.


Dark theme rendering issues on Windows 10
------------------------------------------

**Symptom**: Some UI elements are hard to read with the dark theme on
Windows 10.

**Cause**: Known compatibility issue with the Qt dark theme on Windows 10.

**Fix**: This issue has been addressed in version 1.0.0. Make sure you are
running the latest version:

.. code-block:: console

   $ pip install --upgrade ModuleTester


Test runs but result stays "None"
---------------------------------

**Symptom**: A test finishes but its result is not recorded.

**Possible causes**:

- The test process exited abnormally or was killed.
- An encoding error prevented output capture.

**Fix**: Version 1.0.0 includes fixes for ``end_time`` remaining ``None``
and for non-UTF8 output encoding. Upgrade to the latest version:

.. code-block:: console

   $ pip install --upgrade ModuleTester
