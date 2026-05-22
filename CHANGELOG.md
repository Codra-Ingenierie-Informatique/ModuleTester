# ModuleTester Releases #

## Version 1.0.1 ##

### New features

- Add Example Calculator reference implementation (`example/`) demonstrating
  full ModuleTester integration with manual GUI tests, unit tests (pytest +
  coverage), and qualification scripts
- Add step-by-step integration guide in documentation (`doc/example.rst`)

### Bug fixes

- Set fixed font for result label in `ResultError` and `ResultOutput` widgets
- Change launch configuration type from `python` to `debugpy`

### Improvements

- Add `pypandoc_binary` to requirements
- Add missing `PyQtWebEngine` to requirements
- Add deps requirements sync script `scripts\update_requirements.py`

## Version 1.0.0 ##

First stable release of ModuleTester.

### New features

- Reworked GUI with dockable panels, collapsible CLI widget, and resizable
  result/info panels
- Tree view for test navigation with body/tree synchronization
- Notification system for test execution output
- Configuration editor widget with error handling and conflict resolution
- Web engine view for test descriptions with forced reload and restricted
  context menu
- New Jinja2-based document exporter supporting HTML, DOCX, ODT, PDF, MD
  and RST output formats
- Test list export as a standalone document
- Customizable CSS styling for exported documents (code blocks, inline
  code spans)
- Missing module handling with placeholder display
- Bundled `pyqtspinner` widget (removed external dependency)

### Bug fixes

- Fixed processes not being able to be opened/closed on Linux
- Fixed package-defined templates not applied on generated files
- Fixed module not reloading correctly after code changes
- Fixed command timeout handling in test execution
- Fixed command line arguments parsing
- Fixed encoding errors on test outputs (non-UTF8)
- Fixed double-click run synchronization with the run button
- Fixed partial name match causing unintended tests to run
- Fixed `end_time` remaining `None` after test completion
- Fixed `communicate()` returning `None` in edge cases
- Fixed invalid tests returned by `get_tests()`
- Fixed toolbar layout and typing issues
- Fixed dark theme rendering on Windows 10
- Fixed result combo box state while tests are running
- Fixed RST conversion using `sys.prefix` for executable lookup

### Improvements

- Improved configuration system with new tools and better error handling
- Consistent result enum casing between widgets
- Removed dead code and debug prints
- Pylint pass and type checking improvements

## Version 0.1.0 ##

Experimental release. Not ready for production use.
