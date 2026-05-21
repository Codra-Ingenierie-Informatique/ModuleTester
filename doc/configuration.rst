Configuration Reference
=======================

ModuleTester is configured through an INI file named ``moduletester.ini``
placed at the root of the target Python package. When ModuleTester loads a
package, it looks for this file automatically.

If the file is absent, default values are used for every option.


Complete example
----------------

.. code-block:: ini

   [general]
   docstring_fmt = rst
   category = visible

   [export]
   template_dir = default_templates
   test_results_template_name = test_results_template.j2
   test_list_template_name = test_list_template.j2
   docx_reference = custom-reference.docx
   odt_reference = custom-reference.odt
   css_style = default_style.css
   export_fmts = html, docx
   reload_templates_on_export = 0
   docstrings_header_shift = 3
   toc_depth = 2

   [gui]
   test_list_visible = 1
   test_list_pos = left
   test_props_visible = 1
   test_props_pos = right
   result_tab_visible = 1
   result_tab_pos = bottom
   result_props_visible = 1
   result_props_pos = right
   cli_visible = 0
   cli_pos = bottom
   toolbox_visible = 0
   toolbox_pos = bottom


``[general]`` section
---------------------

.. list-table::
   :header-rows: 1
   :widths: 25 10 15 50

   * - Option
     - Type
     - Default
     - Description
   * - ``docstring_fmt``
     - str
     - ``rst``
     - Format used to interpret test docstrings. Supported values: ``rst``
       (reStructuredText), ``md`` (Markdown), ``plain`` (plain text).
   * - ``category``
     - str
     - ``visible``
     - Which test category to load. ``visible`` loads only scripts annotated
       with ``# guitest: show``. ``all`` loads every script in the package.


``[export]`` section
--------------------

.. list-table::
   :header-rows: 1
   :widths: 25 10 15 50

   * - Option
     - Type
     - Default
     - Description
   * - ``template_dir``
     - str
     - ``default_templates``
     - Path to the directory containing Jinja2 templates, CSS, and reference
       documents. Relative paths are resolved from the package directory.
   * - ``test_results_template_name``
     - str
     - ``test_results_template.j2``
     - Filename of the Jinja2 template used for test result reports.
   * - ``test_list_template_name``
     - str
     - ``test_list_template.j2``
     - Filename of the Jinja2 template used for test list documents.
   * - ``docx_reference``
     - str
     - ``custom-reference.docx``
     - Filename of the DOCX reference document used by Pandoc for styling
       Word exports.
   * - ``odt_reference``
     - str
     - ``custom-reference.odt``
     - Filename of the ODT reference document used by Pandoc for styling
       LibreOffice exports.
   * - ``css_style``
     - str
     - ``default_style.css``
     - Filename of the CSS stylesheet embedded in HTML exports.
   * - ``export_fmts``
     - list
     - ``html, docx``
     - Comma-separated list of export formats enabled in the GUI export
       dialog. Supported values: ``html``, ``docx``, ``odt``, ``pdf``,
       ``rst``, ``md``.
   * - ``reload_templates_on_export``
     - bool
     - ``0``
     - When set to ``1``, templates are reloaded from disk on every export.
       Useful during template development.
   * - ``docstrings_header_shift``
     - int
     - ``3``
     - Number of heading levels to shift when rendering docstrings inside
       the exported document (avoids clashing with report headings).
   * - ``toc_depth``
     - int
     - ``2``
     - Maximum depth of the table of contents generated in HTML exports.


``[gui]`` section
-----------------

Each dockable panel has two options: ``*_visible`` (boolean, ``0`` or ``1``)
controls whether the panel is shown on startup, and ``*_pos`` (string)
controls its initial dock position (``left``, ``right``, ``top``, or
``bottom``).

.. list-table::
   :header-rows: 1
   :widths: 25 10 15 50

   * - Option
     - Type
     - Default
     - Description
   * - ``test_list_visible``
     - bool
     - ``1``
     - Show the test list tree view on startup.
   * - ``test_list_pos``
     - str
     - ``left``
     - Dock position of the test list panel.
   * - ``test_props_visible``
     - bool
     - ``1``
     - Show the test properties panel on startup.
   * - ``test_props_pos``
     - str
     - ``right``
     - Dock position of the test properties panel.
   * - ``result_tab_visible``
     - bool
     - ``1``
     - Show the execution results panel (Comment/Output/Error tabs) on
       startup.
   * - ``result_tab_pos``
     - str
     - ``bottom``
     - Dock position of the execution results panel.
   * - ``result_props_visible``
     - bool
     - ``1``
     - Show the result properties panel on startup.
   * - ``result_props_pos``
     - str
     - ``right``
     - Dock position of the result properties panel.
   * - ``cli_visible``
     - bool
     - ``0``
     - Show the CLI command panel on startup.
   * - ``cli_pos``
     - str
     - ``bottom``
     - Dock position of the CLI command panel.
   * - ``toolbox_visible``
     - bool
     - ``0``
     - Show the toolbox panel on startup.
   * - ``toolbox_pos``
     - str
     - ``bottom``
     - Dock position of the toolbox panel.


Error handling
--------------

When loading ``moduletester.ini``, the following errors may occur:

- **ConfigConflictError**: raised when the INI file contains extra keys not
  recognised by ModuleTester, or is missing expected keys. If you pass
  ``resolve=True`` to the loader, ModuleTester will automatically add missing
  keys with default values and remove unknown keys.

- **InvalidPathError**: raised when a path option (``template_dir``,
  ``docx_reference``, ``odt_reference``, ``css_style``, or template names)
  points to a file or directory that does not exist.

See :doc:`faq` for troubleshooting tips.
