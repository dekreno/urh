import numpy
import itertools

from PyQt5.QtWidgets import QWidget, QFileDialog, QInputDialog, QCompleter, QMessageBox
from PyQt5.QtCore import pyqtSlot, Qt, QDir, QStringListModel, QRegExp
from PyQt5.QtGui import QRegExpValidator

from urh.models.SimulatorMessageFieldModel import SimulatorMessageFieldModel
from urh.models.SimulatorMessageTableModel import SimulatorMessageTableModel
from urh.util.ProjectManager import ProjectManager
from urh.ui.ui_simulator import Ui_SimulatorTab
from urh.controller.dialogs.SimulatorDialog import SimulatorDialog
from urh.ui.SimulatorScene import SimulatorScene
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.MessageType import MessageType
from urh.simulator.SimulatorRule import SimulatorRule, SimulatorRuleCondition, ConditionType
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.simulator.SimulatorMessage import SimulatorMessage
from urh.simulator.SimulatorGotoAction import SimulatorGotoAction
from urh.simulator.SimulatorProgramAction import SimulatorProgramAction
from urh.simulator.SimulatorExpressionParser import SimulatorExpressionParser
from urh.simulator.SimulatorItem import SimulatorItem
from urh.simulator.SimulatorConfiguration import SimulatorConfiguration
from urh.controller.CompareFrameController import CompareFrameController
from urh.controller.GeneratorTabController import GeneratorTabController
from urh.controller.dialogs.ModulatorDialog import ModulatorDialog
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.delegates.ProtocolValueDelegate import ProtocolValueDelegate
from urh.ui.RuleExpressionValidator import RuleExpressionValidator

class SimulatorTabController(QWidget):
    def __init__(self, compare_frame_controller: CompareFrameController,
                       generator_tab_controller: GeneratorTabController,
                       project_manager: ProjectManager, parent):
        super().__init__(parent)

        self.project_manager = project_manager
        self.compare_frame_controller = compare_frame_controller
        self.generator_tab_controller = generator_tab_controller
        self.proto_analyzer = compare_frame_controller.proto_analyzer

        self.simulator_config = SimulatorConfiguration(self.project_manager)
        self.sim_expression_parser = SimulatorExpressionParser(self.simulator_config)
        SimulatorItem.protocol_manager = self.simulator_config
        SimulatorItem.expression_parser = self.sim_expression_parser

        self.ui = Ui_SimulatorTab()
        self.ui.setupUi(self)

        self.ui.splitter.setSizes([self.width() / 0.7, self.width() / 0.3])

        self.ui.treeProtocols.setHeaderHidden(True)
        self.tree_model = self.generator_tab_controller.tree_model
        self.ui.treeProtocols.setModel(self.tree_model)

        self.simulator_message_field_model = SimulatorMessageFieldModel(self)
        self.ui.tblViewFieldValues.setModel(self.simulator_message_field_model)
        self.ui.tblViewFieldValues.setItemDelegateForColumn(1, ComboBoxDelegate(ProtocolLabel.DISPLAY_FORMATS, parent=self.ui.tblViewFieldValues))
        self.ui.tblViewFieldValues.setItemDelegateForColumn(2, ComboBoxDelegate(SimulatorProtocolLabel.VALUE_TYPES, parent=self.ui.tblViewFieldValues))
        self.ui.tblViewFieldValues.setItemDelegateForColumn(3, ProtocolValueDelegate(controller=self, parent=self.ui.tblViewFieldValues))
        self.project_manager.reload_field_types()
        self.update_field_name_column()

        self.simulator_message_table_model = SimulatorMessageTableModel(self.project_manager, self)
        self.ui.tblViewMessage.setModel(self.simulator_message_table_model)

        self.ui.ruleCondLineEdit.setValidator(RuleExpressionValidator(self.sim_expression_parser, is_formula=False))
        self.completer_model = QStringListModel([])
        self.ui.ruleCondLineEdit.setCompleter(QCompleter(self.completer_model, self.ui.ruleCondLineEdit))
        self.ui.ruleCondLineEdit.setToolTip(self.sim_expression_parser.rule_condition_help)

        self.simulator_scene = SimulatorScene(mode=0, simulator_config=self.simulator_config)
        self.simulator_scene.tree_root_item = compare_frame_controller.proto_tree_model.rootItem
        self.ui.gvSimulator.setScene(self.simulator_scene)
        self.ui.gvSimulator.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.ui.gvSimulator.proto_analyzer = compare_frame_controller.proto_analyzer

        self.ui.navLineEdit.setValidator(QRegExpValidator(QRegExp("^\d+(\.\d+)*$")))

        self.__active_item = None

        self.create_connects(compare_frame_controller)

    def refresh_field_types_for_labels(self):
        for msg in self.simulator_config.get_all_messages():
            for lbl in (lbl for lbl in msg.message_type if lbl.field_type is not None):
                msg.message_type.change_field_type_of_label(lbl, self.field_types_by_caption.get(lbl.field_type.caption, None))

        self.update_field_name_column()
        self.update_ui()

    @property
    def field_types(self):
        return self.project_manager.field_types

    @property
    def field_types_by_caption(self):
        return self.project_manager.field_types_by_caption

    def update_field_name_column(self):
        field_types = [ft.caption for ft in self.field_types]
        self.ui.tblViewFieldValues.setItemDelegateForColumn(0, ComboBoxDelegate(field_types, is_editable=True, return_index=False, parent=self.ui.tblViewFieldValues))

    def create_connects(self, compare_frame_controller):
        self.ui.btnChooseExtProg.clicked.connect(self.on_btn_choose_ext_prog_clicked)
        self.ui.extProgramLineEdit.textChanged.connect(self.on_ext_program_line_edit_text_changed)
        self.ui.cmdLineArgsLineEdit.textChanged.connect(self.on_cmd_line_args_line_edit_text_changed)
        self.ui.ruleCondLineEdit.textChanged.connect(self.on_rule_cond_line_edit_text_changed)
        self.ui.btnStartSim.clicked.connect(self.on_show_simulate_dialog_action_triggered)
        self.ui.btnNextNav.clicked.connect(self.ui.gvSimulator.navigate_forward)
        self.ui.btnPrevNav.clicked.connect(self.ui.gvSimulator.navigate_backward)
        self.ui.navLineEdit.returnPressed.connect(self.on_nav_line_edit_return_pressed)
        self.ui.goto_combobox.currentIndexChanged.connect(self.on_goto_combobox_index_changed)
        self.ui.spinBoxRepeat.valueChanged.connect(self.on_repeat_value_changed)
        self.ui.cbViewType.currentIndexChanged.connect(self.on_view_type_changed)
        self.ui.tblViewMessage.create_fuzzing_label_clicked.connect(self.create_fuzzing_label)
        self.ui.tblViewMessage.open_modulator_dialog_clicked.connect(self.open_modulator_dialog)
        self.ui.tblViewMessage.selectionModel().selectionChanged.connect(self.on_table_selection_changed)
        self.ui.tabWidget.currentChanged.connect(self.on_selected_tab_changed)

        self.tree_model.modelReset.connect(self.refresh_tree)

        self.simulator_scene.selectionChanged.connect(self.on_simulator_scene_selection_changed)

        self.simulator_message_field_model.protocol_label_updated.connect(self.item_updated)
        self.ui.gvSimulator.message_updated.connect(self.item_updated)
        self.ui.gvSimulator.new_messagetype_clicked.connect(self.add_message_type)
        self.ui.gvSimulator.consolidate_messages_clicked.connect(self.consolidate_messages)

        self.simulator_config.items_added.connect(self.refresh_message_table)
        self.simulator_config.items_updated.connect(self.refresh_message_table)
        self.simulator_config.items_moved.connect(self.refresh_message_table)
        self.simulator_config.items_deleted.connect(self.refresh_message_table)
        self.simulator_config.participants_changed.connect(self.update_vertical_table_header)
        self.simulator_config.item_dict_updated.connect(self.on_item_dict_updated)

    def consolidate_messages(self):
        self.simulator_config.consolidate_messages()

    def add_message_type(self, message: SimulatorMessage):
        names = set(message_type.name for message_type in self.proto_analyzer.message_types)
        name = "Message type #"
        i = next(i for i in itertools.count(start=1) if name+str(i) not in names)

        msg_type_name, ok = QInputDialog.getText(self, self.tr("Enter message type name"),
                                                 self.tr("Name:"), text=name + str(i))

        if ok:
            msg_type = MessageType(name=msg_type_name)

            for lbl in message.message_type:
                msg_type.add_protocol_label(start=lbl.start, end=lbl.end - 1, name=lbl.name,
                                            color_ind=lbl.color_index, type=lbl.field_type)

            self.proto_analyzer.message_types.append(msg_type)
            self.compare_frame_controller.fill_message_type_combobox()
            self.compare_frame_controller.active_message_type = self.compare_frame_controller.active_message_type

            message.message_type.name = msg_type_name
            self.simulator_config.items_updated.emit([message])

    def on_repeat_value_changed(self, value):
        self.active_item.repeat = value
        self.simulator_config.items_updated.emit([self.active_item])

    def on_item_dict_updated(self):
        self.completer_model.setStringList(self.sim_expression_parser.label_identifier())
        #self.update_goto_combobox()

    def on_selected_tab_changed(self, index: int):
        if index == 0:
            if self.active_item is not None:
                self.ui.gvSimulator.jump_to_item(self.active_item)
            else:
                self.update_ui()
        else:
            self.ui.tblViewMessage.resize_columns()
            self.update_vertical_table_header()

    def refresh_message_table(self):
        self.simulator_message_table_model.protocol.messages[:] = self.simulator_config.get_all_messages()
        self.simulator_message_table_model.update()

        if isinstance(self.active_item, SimulatorMessage):
            self.simulator_message_field_model.update()

        self.ui.tblViewMessage.resize_columns()
        self.update_ui()

    def load_config_from_xml_tag(self, xml_tag):
        if xml_tag is None:
            return
        self.simulator_config.on_project_updated()
        self.simulator_config.load_from_xml(xml_tag, self.proto_analyzer.message_types)

    def close_all(self):
        self.simulator_scene.clear_all()

    @pyqtSlot(int, int, int)
    def create_fuzzing_label(self, msg_index: int, start: int, end: int):
        con = self.simulator_message_table_model.protocol
        start, end = con.convert_range(start, end - 1, self.ui.cbViewType.currentIndex(), 0, False, msg_index)
        lbl = self.simulator_config.add_label(start=start, end=end, parent_item=con.messages[msg_index])

        try:
            index = self.simulator_message_field_model.message_type.index(lbl)
            self.ui.tblViewFieldValues.edit(self.simulator_message_field_model.createIndex(index, 0))
        except ValueError:
            pass

    @pyqtSlot()
    def open_modulator_dialog(self):
        selected_message = self.simulator_message_table_model.protocol.messages[self.ui.tblViewMessage.selected_rows[0]]
        preselected_index = selected_message.modulator_index

        modulator_dialog = ModulatorDialog(self.project_manager.modulators, parent=self)
        modulator_dialog.ui.treeViewSignals.setModel(self.tree_model)
        modulator_dialog.ui.treeViewSignals.expandAll()
        modulator_dialog.ui.comboBoxCustomModulations.setCurrentIndex(preselected_index)
        modulator_dialog.showMaximized()

        self.generator_tab_controller.initialize_modulation_dialog(selected_message.encoded_bits_str[0:10], modulator_dialog)

        modulator_dialog.finished.connect(self.refresh_modulators)
        modulator_dialog.finished.connect(self.generator_tab_controller.refresh_pause_list)

    @pyqtSlot()
    def refresh_modulators(self):
        # update Generator tab ...
        cBoxModulations = self.generator_tab_controller.ui.cBoxModulations
        current_index = cBoxModulations.currentIndex()
        cBoxModulations.clear()

        for modulator in self.project_manager.modulators:
            cBoxModulations.addItem(modulator.name)

        cBoxModulations.setCurrentIndex(current_index)

        # update Simulator tab ...
        index = self.sender().ui.comboBoxCustomModulations.currentIndex()

        for row in self.ui.tblViewMessage.selected_rows:
            self.simulator_message_table_model.protocol.messages[row].modulator_index = index

    def update_goto_combobox(self):
        goto_combobox = self.ui.goto_combobox

        goto_combobox.blockSignals(True)
        goto_combobox.clear()
        goto_combobox.addItem("Select item ...")
        goto_combobox.addItems(SimulatorGotoAction.goto_identifier())
        goto_combobox.setCurrentIndex(-1)
        goto_combobox.blockSignals(False)

        index = goto_combobox.findText(self.active_item.goto_target)

        if index == -1:
            index = 0

        goto_combobox.setCurrentIndex(index)

    def update_ui(self):
        if self.active_item is not None:
            scene_item = self.simulator_scene.model_to_scene(self.active_item)
            self.ui.navLineEdit.setText(self.active_item.index())
            self.ui.btnNextNav.setEnabled(not scene_item.next() is None)
            self.ui.btnPrevNav.setEnabled(not scene_item.prev() is None)

            text = self.tr("Detail view for item #") + self.active_item.index()

            if isinstance(self.active_item, SimulatorMessage):
                text += " (" + self.active_item.message_type.name + ")"
                self.ui.spinBoxRepeat.setValue(self.active_item.repeat)
                self.ui.lblEncodingDecoding.setText(self.active_item.decoder.name)

            self.ui.lblMsgFieldsValues.setText(text)
        else:
            self.ui.navLineEdit.clear()
            self.ui.btnNextNav.setEnabled(False)
            self.ui.btnPrevNav.setEnabled(False)

            self.ui.lblMsgFieldsValues.setText(self.tr("Detail view for item"))

    def update_vertical_table_header(self):
        self.simulator_message_table_model.refresh_vertical_header()
        self.ui.tblViewMessage.resize_vertical_header()

    @pyqtSlot()
    def on_rule_cond_line_edit_text_changed(self):
        self.active_item.condition = self.ui.ruleCondLineEdit.text()
        self.item_updated(self.active_item)

    @pyqtSlot()
    def on_view_type_changed(self):
        self.simulator_message_table_model.proto_view = self.ui.cbViewType.currentIndex()
        self.simulator_message_table_model.update()
        self.ui.tblViewMessage.resize_columns()
        
    @pyqtSlot()
    def on_goto_combobox_index_changed(self):
        if not isinstance(self.active_item, SimulatorGotoAction):
            return

        self.active_item.goto_target = None if self.ui.goto_combobox.currentIndex() == 0 else self.ui.goto_combobox.currentText()
        self.item_updated(self.active_item)

    @pyqtSlot()
    def on_simulator_scene_selection_changed(self):
        selected_items = self.simulator_scene.selectedItems()
        self.active_item = selected_items[0].model_item if selected_items else None

        self.update_ui()

    @pyqtSlot()
    def on_table_selection_changed(self):
        selection = self.ui.tblViewMessage.selectionModel().selection()

        if selection.isEmpty():
            self.active_item = None
            self.ui.lNumSelectedColumns.setText("0")
        else:
            max_row = numpy.max([rng.bottom() for rng in selection])
            self.active_item = self.simulator_message_table_model.protocol.messages[max_row]
            _, _, start, end = self.ui.tblViewMessage.selection_range()
            self.ui.lNumSelectedColumns.setText(str(end - start))

        self.update_ui()

    @property
    def active_item(self):
        return self.__active_item

    @active_item.setter
    def active_item(self, value):
        self.__active_item = value

        if isinstance(self.active_item, SimulatorGotoAction):
            self.update_goto_combobox()

            self.ui.detail_view_widget.setCurrentIndex(1)
        elif isinstance(self.active_item, SimulatorMessage):
            self.simulator_message_field_model.update()
            self.ui.spinBoxRepeat.setValue(self.active_item.repeat)
            self.ui.lblEncodingDecoding.setText(self.active_item.decoder.name)

            self.ui.detail_view_widget.setCurrentIndex(2)
        elif (isinstance(self.active_item, SimulatorRuleCondition) and
              self.active_item.type != ConditionType.ELSE):
            self.ui.ruleCondLineEdit.setText(self.active_item.condition)
            self.ui.detail_view_widget.setCurrentIndex(3)
        elif isinstance(self.active_item, SimulatorProgramAction):
            self.ui.extProgramLineEdit.setText(self.active_item.ext_prog)
            self.ui.cmdLineArgsLineEdit.setText(self.active_item.args)

            self.ui.detail_view_widget.setCurrentIndex(4)
        else:
            self.ui.detail_view_widget.setCurrentIndex(0)

        self.update_ui()

    @pyqtSlot()
    def on_show_simulate_dialog_action_triggered(self):
        if not self.simulator_config.protocol_valid():
            QMessageBox.critical(self, self.tr("Invalid protocol configuration"),
                self.tr("There are some problems with your protocol configuration. Please fix them first."))
            return

        if not len(self.simulator_config.get_all_messages()):
            QMessageBox.critical(self, self.tr("No messages found"), self.tr("Please add at least one message."))
            return

        s = SimulatorDialog(self.simulator_config, self.project_manager.modulators,
                            self.sim_expression_parser, self.project_manager, parent=self)

        s.exec_()

    @pyqtSlot()
    def on_nav_line_edit_return_pressed(self):
        nav_text = self.ui.navLineEdit.text()

        curr_item = self.simulator_config.rootItem

        index_list = nav_text.split(".")
        index_list = list(map(int, index_list))

        for index in index_list:
            if (curr_item is None or index > curr_item.child_count()
                    or isinstance(curr_item, SimulatorMessage)):
                break

            curr_item = curr_item.children[index - 1]

            if isinstance(curr_item, SimulatorRule):
                curr_item = curr_item.children[0]

        self.ui.gvSimulator.jump_to_item(curr_item)

    @pyqtSlot()
    def on_btn_choose_ext_prog_clicked(self):
        file_name, ok = QFileDialog.getOpenFileName(self, self.tr("Choose external program"), QDir.homePath())

        if file_name is not None and ok:
            self.ui.extProgramLineEdit.setText(file_name)

    @pyqtSlot()
    def on_ext_program_line_edit_text_changed(self):
        self.active_item.ext_prog = self.ui.extProgramLineEdit.text()
        self.item_updated(self.active_item)

    @pyqtSlot()
    def on_cmd_line_args_line_edit_text_changed(self):
        self.active_item.args = self.ui.cmdLineArgsLineEdit.text()
        self.item_updated(self.active_item)

    def item_updated(self, item: SimulatorItem):
        self.simulator_config.items_updated.emit([item])

    @pyqtSlot()
    def refresh_tree(self):
        self.ui.treeProtocols.expandAll()
