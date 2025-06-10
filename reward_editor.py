import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QListWidget, QLineEdit, QTextEdit, 
                            QComboBox, QPushButton, QLabel, QSpinBox, QTableWidget,
                            QTableWidgetItem, QMessageBox, QFileDialog, QAbstractItemView)
from PySide6.QtCore import Qt
from reward_model import RewardModel, Reward, RewardItem, Requirement

class RewardEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("L2J Reward Editor - Made by Saint")
        self.setMinimumSize(1200, 800)
        
        # Initialize model
        self.model = RewardModel()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create left panel (reward list)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Add file loading buttons
        load_buttons = QHBoxLayout()
        load_xml_btn = QPushButton("Load XML")
        load_text_btn = QPushButton("Load Text")
        load_xml_btn.clicked.connect(self.load_xml_file)
        load_text_btn.clicked.connect(self.load_text_file)
        load_buttons.addWidget(load_xml_btn)
        load_buttons.addWidget(load_text_btn)
        left_layout.addLayout(load_buttons)
        
        self.reward_list = QListWidget()
        self.reward_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.reward_list.currentRowChanged.connect(self.load_reward)
        left_layout.addWidget(QLabel("Rewards:"))
        left_layout.addWidget(self.reward_list)
        
        # Add Delete button
        delete_btn = QPushButton("Delete Reward")
        delete_btn.clicked.connect(self.delete_reward)
        left_layout.addWidget(delete_btn)
        
        # Create right panel (reward details)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Basic info section
        basic_info = QWidget()
        basic_layout = QVBoxLayout(basic_info)
        
        # ID and Name
        id_name_layout = QHBoxLayout()
        self.id_input = QSpinBox()
        self.id_input.setRange(1, 9999)
        self.name_input = QLineEdit()
        id_name_layout.addWidget(QLabel("ID:"))
        id_name_layout.addWidget(self.id_input)
        id_name_layout.addWidget(QLabel("Name:"))
        id_name_layout.addWidget(self.name_input)
        basic_layout.addLayout(id_name_layout)
        
        # Description
        basic_layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        basic_layout.addWidget(self.desc_input)
        
        # Reset period
        reset_layout = QHBoxLayout()
        self.reset_period = QComboBox()
        self.reset_period.addItems(["DAILY", "WEEKLY", "MONTHLY", "SINGLE"])
        reset_layout.addWidget(QLabel("Reset Period:"))
        reset_layout.addWidget(self.reset_period)
        basic_layout.addLayout(reset_layout)
        
        # Category
        category_layout = QHBoxLayout()
        self.category_box = QComboBox()
        self.category_box.addItems(["0", "1", "2", "3"])
        category_layout.addWidget(QLabel("Category:"))
        category_layout.addWidget(self.category_box)
        basic_layout.addLayout(category_layout)
        
        # Level range
        level_layout = QHBoxLayout()
        self.min_level = QSpinBox()
        self.min_level.setRange(1, 99)
        self.max_level = QSpinBox()
        self.max_level.setRange(1, 99)
        level_layout.addWidget(QLabel("Min Level:"))
        level_layout.addWidget(self.min_level)
        level_layout.addWidget(QLabel("Max Level:"))
        level_layout.addWidget(self.max_level)
        basic_layout.addLayout(level_layout)
        
        right_layout.addWidget(basic_info)
        
        # Reward items section
        items_section = QWidget()
        items_layout = QVBoxLayout(items_section)
        items_layout.addWidget(QLabel("Reward Items:"))
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(2)
        self.items_table.setHorizontalHeaderLabels(["Item ID", "Count"])
        items_layout.addWidget(self.items_table)
        
        items_buttons = QHBoxLayout()
        add_item_btn = QPushButton("Add Item")
        remove_item_btn = QPushButton("Remove Item")
        add_item_btn.clicked.connect(self.add_reward_item)
        remove_item_btn.clicked.connect(self.remove_reward_item)
        items_buttons.addWidget(add_item_btn)
        items_buttons.addWidget(remove_item_btn)
        items_layout.addLayout(items_buttons)
        
        right_layout.addWidget(items_section)
        
        # Requirements section
        req_section = QWidget()
        req_layout = QVBoxLayout(req_section)
        req_layout.addWidget(QLabel("Requirements:"))
        
        self.req_table = QTableWidget()
        self.req_table.setColumnCount(2)
        self.req_table.setHorizontalHeaderLabels(["Type", "Value"])
        req_layout.addWidget(self.req_table)
        
        req_buttons = QHBoxLayout()
        add_req_btn = QPushButton("Add Requirement")
        remove_req_btn = QPushButton("Remove Requirement")
        add_req_btn.clicked.connect(self.add_requirement)
        remove_req_btn.clicked.connect(self.remove_requirement)
        req_buttons.addWidget(add_req_btn)
        req_buttons.addWidget(remove_req_btn)
        req_layout.addLayout(req_buttons)
        
        # Mob IDs text box
        req_layout.addWidget(QLabel("Mob IDs (semicolon-separated):"))
        self.mob_ids_input = QLineEdit()
        req_layout.addWidget(self.mob_ids_input)
        
        right_layout.addWidget(req_section)
        
        # Save buttons
        save_buttons = QHBoxLayout()
        save_xml_btn = QPushButton("Save as XML")
        save_text_btn = QPushButton("Save as Text")
        save_xml_btn.clicked.connect(self.save_as_xml)
        save_text_btn.clicked.connect(self.save_as_text)
        save_buttons.addWidget(save_xml_btn)
        save_buttons.addWidget(save_text_btn)
        right_layout.addLayout(save_buttons)
        
        # Add panels to main layout
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        # Add 'Made by Saint' label at the bottom
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        saint_label = QLabel("Made by Saint")
        saint_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(saint_label)
        main_widget.setLayout(main_layout)
    
    def load_xml_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load XML File", "", "XML Files (*.xml)")
        if file_path:
            try:
                self.model.load_from_xml(file_path)
                self.update_reward_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load XML file: {str(e)}")
    
    def load_text_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Text File", "", "Text Files (*.txt)")
        if file_path:
            try:
                self.model.load_from_text(file_path)
                self.update_reward_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load text file: {str(e)}")
    
    def update_reward_list(self):
        self.reward_list.clear()
        for reward in sorted(self.model.rewards.values(), key=lambda x: x.id):
            self.reward_list.addItem(f"{reward.id}: {reward.name}")
    
    def load_reward(self, index):
        if index < 0:
            return
        
        reward_id = int(self.reward_list.currentItem().text().split(':')[0])
        reward = self.model.rewards[reward_id]
        
        # Update basic info
        self.id_input.setValue(reward.id)
        self.name_input.setText(reward.name)
        self.desc_input.setText(reward.description)
        self.reset_period.setCurrentText(reward.reset_period)
        self.min_level.setValue(reward.min_level)
        self.max_level.setValue(reward.max_level)
        self.category_box.setCurrentText(str(getattr(reward, 'category', 0)))
        
        # Update reward items
        self.items_table.setRowCount(len(reward.reward_items))
        for i, item in enumerate(reward.reward_items):
            self.items_table.setItem(i, 0, QTableWidgetItem(str(item.item_id)))
            self.items_table.setItem(i, 1, QTableWidgetItem(str(item.count)))
        
        # Update requirements
        self.req_table.setRowCount(len(reward.requirements))
        for i, req in enumerate(reward.requirements):
            self.req_table.setItem(i, 0, QTableWidgetItem(req.type))
            self.req_table.setItem(i, 1, QTableWidgetItem(req.value))
        
        # Update mob IDs
        self.mob_ids_input.setText(';'.join(str(mid) for mid in getattr(reward, 'mob_ids', [])))
    
    def add_reward_item(self):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        self.items_table.setItem(row, 0, QTableWidgetItem("0"))
        self.items_table.setItem(row, 1, QTableWidgetItem("1"))
    
    def remove_reward_item(self):
        current_row = self.items_table.currentRow()
        if current_row >= 0:
            self.items_table.removeRow(current_row)
    
    def add_requirement(self):
        row = self.req_table.rowCount()
        self.req_table.insertRow(row)
        self.req_table.setItem(row, 0, QTableWidgetItem("kill_mob"))
        self.req_table.setItem(row, 1, QTableWidgetItem("1"))
    
    def remove_requirement(self):
        current_row = self.req_table.currentRow()
        if current_row >= 0:
            self.req_table.removeRow(current_row)
    
    def save_as_xml(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save as XML", "", "XML Files (*.xml)")
        if file_path:
            try:
                self.save_current_reward()
                self.model.save_to_xml(file_path)
                QMessageBox.information(self, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save XML file: {str(e)}")
    
    def save_as_text(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save as Text", "", "Text Files (*.txt)")
        if file_path:
            try:
                self.save_current_reward()
                self.model.save_to_text(file_path)
                QMessageBox.information(self, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save text file: {str(e)}")
    
    def save_current_reward(self):
        if not self.reward_list.currentItem():
            return
        
        reward_id = int(self.reward_list.currentItem().text().split(':')[0])
        
        # Get reward items
        reward_items = []
        for row in range(self.items_table.rowCount()):
            item_id = int(self.items_table.item(row, 0).text())
            count = int(self.items_table.item(row, 1).text())
            reward_items.append(RewardItem(item_id, count))
        
        # Get requirements
        requirements = []
        for row in range(self.req_table.rowCount()):
            req_type = self.req_table.item(row, 0).text()
            req_value = self.req_table.item(row, 1).text()
            requirements.append(Requirement(req_type, req_value))
        
        # Get mob IDs
        mob_ids = []
        mob_ids_str = self.mob_ids_input.text().strip()
        if mob_ids_str:
            mob_ids = [int(x) for x in mob_ids_str.split(';') if x.strip().isdigit()]
        
        # Create updated reward
        reward = Reward(
            id=self.id_input.value(),
            name=self.name_input.text(),
            description=self.desc_input.toPlainText(),
            reset_period=self.reset_period.currentText(),
            reward_items=reward_items,
            requirements=requirements,
            class_filter=[-1],  # Default to all classes
            min_level=self.min_level.value(),
            max_level=self.max_level.value(),
            category=int(self.category_box.currentText()),
            mob_ids=mob_ids
        )
        
        # Update model
        self.model.rewards[reward_id] = reward
        self.update_reward_list()

    def delete_reward(self):
        selected_items = self.reward_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            reward_id = int(item.text().split(':')[0])
            if reward_id in self.model.rewards:
                del self.model.rewards[reward_id]
        self.update_reward_list()
        # Clear the right panel
        self.id_input.setValue(0)
        self.name_input.clear()
        self.desc_input.clear()
        self.reset_period.setCurrentIndex(0)
        self.min_level.setValue(1)
        self.max_level.setValue(1)
        self.items_table.setRowCount(0)
        self.req_table.setRowCount(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RewardEditor()
    window.show()
    sys.exit(app.exec()) 