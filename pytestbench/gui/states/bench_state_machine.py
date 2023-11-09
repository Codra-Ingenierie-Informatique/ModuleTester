# pylint: disable=missing-module-docstring,missing-function-docstring
# pylint: disable=missing-class-docstring

from typing import Optional

from PyQt5 import QtCore as QC

from pytestbench.gui.states.bench_signals import TMSignals


class TMStateMachine(QC.QStateMachine):
    def __init__(self, signals: TMSignals, parent: Optional[QC.QState] = None):
        super().__init__(QC.QState.ExclusiveStates, parent)
        self.signals = signals
        # main states
        self.started_state = QC.QState(self)
        self.loaded_states = QC.QState(QC.QState.ParallelStates, self)

        # Loaded child states
        self.update_states = QC.QState(QC.QState.ExclusiveStates, self.loaded_states)
        self.file_states = QC.QState(QC.QState.ExclusiveStates, self.loaded_states)
        self.run_states = QC.QState(QC.QState.ExclusiveStates, self.loaded_states)

        # Update states children
        self.up_to_date_state = QC.QState(self.update_states)
        self.modified_state = QC.QState(self.update_states)

        # File states children
        self.has_file_state = QC.QState(self.file_states)
        self.no_file_state = QC.QState(self.file_states)

        # Run states children
        self.running_state = QC.QState(self.run_states)
        self.waiting_run_state = QC.QState(self.run_states)
        self.paused_state = QC.QState(self.run_states)

    def start_machine(self, has_save_path: bool = False):
        self.setInitialState(self.started_state)
        if has_save_path:
            self.file_states.setInitialState(self.has_file_state)
        else:
            self.file_states.setInitialState(self.no_file_state)

        self.update_states.setInitialState(self.up_to_date_state)
        self.run_states.setInitialState(self.waiting_run_state)

        self.setup_states_transitions()

        self.start()

    def setup_states_transitions(self):
        # Start state transitions
        self.started_state.addTransition(self.signals.benchLoaded, self.loaded_states)

        # File states transitions
        self.has_file_state.addTransition(
            self.signals.templateCreated, self.no_file_state
        )
        self.no_file_state.addTransition(
            self.signals.testbenchLoaded, self.has_file_state
        )

        # Update states transitions
        self.up_to_date_state.addTransition(
            self.signals.benchModified, self.modified_state
        )
        self.modified_state.addTransition(
            self.signals.benchSaved, self.up_to_date_state
        )

        # Running states transitions
        self.waiting_run_state.addTransition(
            self.signals.run_started, self.running_state
        )
        self.running_state.addTransition(
            self.signals.run_stopped, self.waiting_run_state
        )
        self.running_state.addTransition(self.signals.run_paused, self.paused_state)
        self.paused_state.addTransition(self.signals.run_reloaded, self.running_state)
        self.paused_state.addTransition(
            self.signals.run_stopped, self.waiting_run_state
        )
