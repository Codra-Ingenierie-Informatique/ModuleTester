
- [Tree](#tree)
- [Command line](#command-line)
- [Doc](#doc)
  - [Root](#root)
  - [gui](#gui)
  - [gui/components](#gui.components)
  - [gui/states](#gui.states)
  - [gui/widgets](#gui.widgets)

# Tree

```sh
pytestbench
|   exporter.py
|   bench.py
|   model.py
|   python_helpers.py
|   serializer.py
|   TODO.txt
|   tree.txt
|
+---gui
|   |   window.py
|   |   main.py
|   |
|   +---components
|   |   |   body_component.py
|   |   |   result_information.py
|   |   |   status_bar_component.py
|   |   |   test_information.py
|   |   |   tool_bar_component.py
|   |
|   +---states
|   |   |   bench_signals.py
|   |   |   bench_state_machine.py
|   |   |   runner.py
|   |
|   +---widgets
|   |   |   cli_widget.py
|   |   |   result_comment.py
|   |   |   result_error_widget.py
|   |   |   result_output_widget.py
|   |   |   result_props_widget.py
|   |   |   tab_image_widget.py
|   |   |   test_description_widget.py
|   |   |   test_list_widget.py
|   |   |   test_prop_widget.py
```

# Command Line

```sh
python -m pytestbench.bench -h
```

# Doc

## Root

### exporter.py

All functions to export files from TestSuite to rst files

### bench.py

Main class for the pytestbench. Manage the test_suite. Not serialized.
Contains the definition of the command lines

### model.py

Contains the different dataclasses used by the TestBench.

### python_helpers.py

Contains helpers function for python

### serializer.py

Contains classes and functions to serialize the test suite to a .testbench file.

## gui

### window.py

Main window of the pytestbench.

### main.py

Main class for the graphical pytestbench

## gui.components

### body_component.py

Central widget of the main window. Contains the [list of test](#test_list_widget.py), the [test information widget](#test_information.py)
the [result information widget](#result_information.py), and the [command line widget](#cli_widget.py).

### result_information.py

Information group for the result of a test. Contains a tab widget, and a [prop group](#result_props_widget.py)

### status_bar_component.py

Statusbar component class

### test_information.py

Information group for the test itself. Contains a tab widget with [test description](#test_description_widget.py)
and [images](#tab_images_widget.py), and a [prop group](#test_prop_widget)

### tool_bar_component.py

Defines the action in the toolbar as well as the toolbar component itself

## gui.states

### bench_signals.py

Defines custom signals used in the gui

### bench_state_machine.py

Defines the state_machine used in the gui as well as the transitions between states

### runner.py

Defines custom QThread to run the test without blocking HMI

## gui.widgets

### cli_widget.py

Defines the group containing the run command line used for last run

### result_comment.py

Defines the widget containing the editable comment for the test result

### result_error_widget.py

Defines the widget containing the error message for the test result

### result_output_widget.py

Defines the widget containing the output message for the test result

### result_props_widget.py

Defines the group containing the table with the properties of the TestResult and the
combo box

### tab_image_widget.py

Defines the tab widget used to display the images in the HMI

### test_description_widget.py

Defines the widget containing the editable description for the test information

### test_list_widget.py

Defines the tree widget displaying the test name, status, and last run date

### test_prop_widget.py

Defines the group containing the table with the properties of the Test.
