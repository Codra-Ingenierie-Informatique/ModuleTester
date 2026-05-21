Template Customisation
======================

ModuleTester uses `Jinja2 <https://jinja.palletsprojects.com/>`_ templates
and `Pandoc <https://pandoc.org/>`_ to generate reports in multiple formats.
You can customise the appearance and content of exported documents by
providing your own templates, CSS stylesheets, and reference documents.


Architecture overview
---------------------

The export pipeline works as follows:

1. A Jinja2 template (``*.j2``) is rendered to an intermediate HTML string.
2. Pandoc converts the HTML to the target format (DOCX, ODT, PDF, etc.).
3. For HTML output, a CSS stylesheet is embedded directly in the file.
4. For DOCX/ODT output, a reference document controls styles and formatting.

The export engine is implemented in ``moduletester.new_exporter`` and uses a
``FileSystemLoader`` pointed at the ``template_dir`` directory configured in
``moduletester.ini``.


Default templates
-----------------

ModuleTester ships with the following files in its ``default_templates/``
directory:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - File
     - Purpose
   * - ``test_results_template.j2``
     - Main report template. Renders test descriptions, commands, results,
       and status icons grouped by sub-module.
   * - ``test_list_template.j2``
     - Simplified template that lists tests without detailed results.
   * - ``default_style.css``
     - CSS stylesheet embedded in HTML exports. Controls layout, code block
       styling, and result formatting.
   * - ``custom-reference.docx``
     - Word reference document used by Pandoc. Defines heading styles, fonts,
       and page layout for DOCX exports.
   * - ``custom-reference.odt``
     - LibreOffice reference document used by Pandoc. Same role as the DOCX
       reference for ODT exports.


Using custom templates
----------------------

To override the default templates:

1. Create a directory in your package (e.g. ``my_templates/``).

2. Copy the default templates you want to modify into that directory.

3. Set ``template_dir`` in your ``moduletester.ini``:

   .. code-block:: ini

      [export]
      template_dir = my_templates

   The path is relative to the package root directory.

4. Edit the copied templates as needed.

.. tip::

   Set ``reload_templates_on_export = 1`` in ``moduletester.ini`` while
   developing templates. This forces ModuleTester to reload templates from
   disk on every export, so you can iterate without restarting the
   application.


Template variables
------------------

Inside a Jinja2 template, the main context object is ``doc_obj``, an instance
of ``DocumentExporter``. The most useful attributes are:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Variable
     - Description
   * - ``doc_obj.test_suite``
     - The ``TestSuite`` object containing all tests and results.
   * - ``doc_obj.test_suite.package``
     - The ``Module`` object for the loaded package (name, path, etc.).
   * - ``doc_obj.test_suite.package.full_name``
     - Fully qualified package name (e.g. ``guidata``).
   * - ``doc_obj.test_suite.author``
     - Author string (or ``None``).
   * - ``doc_obj.test_suite.last_run``
     - Date/time of the last test execution.
   * - ``doc_obj.test_suite.tests``
     - List of all ``Test`` objects.
   * - ``doc_obj.test_suite.group_tests()``
     - Returns a dict grouping tests by sub-module name.
   * - ``doc_obj.docstrings_header_shift``
     - Heading level shift for embedded docstrings.
   * - ``doc_obj.toc_depth``
     - Table of contents depth.

Each ``Test`` object provides:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Attribute
     - Description
   * - ``test.package.last_name``
     - Test script filename (without path).
   * - ``test.command``
     - The command line used to execute the test.
   * - ``test.result``
     - The ``TestResult`` object (or ``None`` if not yet run).
   * - ``test.result.result_name``
     - Human-readable result string (e.g. "Accepted", "Failed").
   * - ``test.result.result.icon_path``
     - Path to the status icon image.
   * - ``test.result.last_run``
     - Date/time of this test's last run.
   * - ``test.get_html_description(...)``
     - Renders the test docstring as HTML.

The translation function ``_()`` is available globally in templates for
internationalised strings.


CSS customisation
-----------------

The ``default_style.css`` file controls the appearance of HTML exports. You
can override it by placing your own CSS file in your custom template
directory and setting the ``css_style`` option:

.. code-block:: ini

   [export]
   css_style = my_style.css

The CSS is embedded directly in the HTML output using Pandoc's
``--embed-resources`` flag.


DOCX and ODT reference documents
---------------------------------

Pandoc uses reference documents to control styles in Word and LibreOffice
exports. To customise:

1. Open the default reference document (``custom-reference.docx`` or
   ``custom-reference.odt``) in your word processor.

2. Modify the styles (headings, body text, fonts, margins, etc.) without
   changing the content structure.

3. Save the modified file in your custom template directory and update
   ``moduletester.ini``:

   .. code-block:: ini

      [export]
      docx_reference = my-reference.docx
      odt_reference = my-reference.odt

See the `Pandoc documentation on reference documents
<https://pandoc.org/MANUAL.html#option--reference-doc>`_ for details on
which styles are used.
