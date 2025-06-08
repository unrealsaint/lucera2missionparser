import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import customtkinter as ctk
from typing import Dict, List, Optional
import json

class CustomXMLWriter:
    def __init__(self, tree):
        self.tree = tree
        self.indent = "\t"
        
    def _indent(self, elem, level=0):
        i = "\n" + level * self.indent
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + self.indent
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subelem in elem:
                self._indent(subelem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
                
    def write(self, file_path):
        root = self.tree.getroot()
        self._indent(root)
        tree_str = ET.tostring(root, encoding='unicode')
        
        # Add XML declaration
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n\n' + tree_str
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)

class XMLRewardEditor:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("XML Reward Editor")
        self.root.after(0, lambda: self.root.state('zoomed'))  # Maximized window after init
        
        # Set custom dark theme with yellow highlights
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")  # We'll override widget colors below
        self.primary_bg = "#181818"
        self.secondary_bg = "#232323"
        self.highlight_yellow = "#FFD600"
        self.text_fg = "#FFD600"
        self.button_bg = "#232323"
        self.button_hover = "#FFD600"
        self.button_fg = "#181818"
        
        self.tree = None
        self.current_file = None
        self.rewards = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.primary_bg)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top buttons frame
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color=self.secondary_bg)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons
        self.load_btn = ctk.CTkButton(self.button_frame, text="Load XML", command=self.load_xml,
            fg_color=self.button_bg, hover_color=self.button_hover, text_color=self.text_fg)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ctk.CTkButton(self.button_frame, text="Save XML", command=self.save_xml,
            fg_color=self.button_bg, hover_color=self.button_hover, text_color=self.text_fg)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.add_btn = ctk.CTkButton(self.button_frame, text="Add Reward", command=self.add_reward,
            fg_color=self.button_bg, hover_color=self.button_hover, text_color=self.text_fg)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.remove_btn = ctk.CTkButton(self.button_frame, text="Remove Selected", command=self.remove_selected_reward,
            fg_color=self.button_bg, hover_color=self.button_hover, text_color=self.text_fg)
        self.remove_btn.pack(side=tk.LEFT, padx=5)
        
        # Create horizontal split frame
        self.split_frame = ctk.CTkFrame(self.main_frame, fg_color=self.primary_bg)
        self.split_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create list view frame (left side)
        self.list_frame = ctk.CTkFrame(self.split_frame, fg_color=self.secondary_bg)
        self.list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for list with more columns
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview",
            background=self.secondary_bg,
            fieldbackground=self.secondary_bg,
            foreground=self.text_fg,
            rowheight=28,
            font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
            background=self.primary_bg,
            foreground=self.highlight_yellow,
            font=("Segoe UI", 10, "bold"))
        style.map("Treeview.Heading",
            background=[('active', self.primary_bg)])
        
        self.treeview = ttk.Treeview(self.list_frame, columns=("ID", "Name", "Description", "Reset Time", "Requirements", "Rewards"), show="headings")
        self.treeview.heading("ID", text="ID")
        self.treeview.heading("Name", text="Name")
        self.treeview.heading("Description", text="Description")
        self.treeview.heading("Reset Time", text="Reset Time")
        self.treeview.heading("Requirements", text="Requirements")
        self.treeview.heading("Rewards", text="Rewards")
        
        # Set column widths
        self.treeview.column("ID", width=50)
        self.treeview.column("Name", width=150)
        self.treeview.column("Description", width=200)
        self.treeview.column("Reset Time", width=100)
        self.treeview.column("Requirements", width=150)
        self.treeview.column("Rewards", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.treeview.bind("<<TreeviewSelect>>", self.on_reward_select)
        
        # Create edit frame (right side)
        self.edit_frame = ctk.CTkFrame(self.split_frame)
        self.edit_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Edit form
        self.setup_edit_form()
        
        # Add Made by Saint label (bottom right)
        self.madeby_label = ctk.CTkLabel(self.root, text="Made by Saint", text_color=self.highlight_yellow, fg_color="transparent", font=("Segoe UI", 12, "bold"))
        self.madeby_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        
    def setup_edit_form(self):
        # Create scrollable frame
        self.edit_scroll = ctk.CTkScrollableFrame(self.edit_frame)
        self.edit_scroll.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Basic info
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.reset_time_var = tk.StringVar()
        
        # Create form fields
        ctk.CTkLabel(self.edit_scroll, text="ID:").pack(anchor=tk.W, padx=5, pady=2)
        ctk.CTkEntry(self.edit_scroll, textvariable=self.id_var).pack(fill=tk.X, padx=5, pady=2)
        
        ctk.CTkLabel(self.edit_scroll, text="Name:").pack(anchor=tk.W, padx=5, pady=2)
        ctk.CTkEntry(self.edit_scroll, textvariable=self.name_var).pack(fill=tk.X, padx=5, pady=2)
        
        ctk.CTkLabel(self.edit_scroll, text="Description:").pack(anchor=tk.W, padx=5, pady=2)
        self.desc_textbox = ctk.CTkTextbox(self.edit_scroll, height=60)
        self.desc_textbox.pack(fill=tk.X, padx=5, pady=2)
        
        ctk.CTkLabel(self.edit_scroll, text="Reset Time:").pack(anchor=tk.W, padx=5, pady=2)
        self.reset_time_combo = ctk.CTkComboBox(self.edit_scroll, values=["SINGLE", "DAILY", "WEEKLY", "MONTHLY"])
        self.reset_time_combo.pack(fill=tk.X, padx=5, pady=2)
        
        # Reward items frame
        reward_items_header = ctk.CTkFrame(self.edit_scroll)
        reward_items_header.pack(fill=tk.X, padx=5, pady=2)
        ctk.CTkLabel(reward_items_header, text="Reward Items:").pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(reward_items_header, text="Add Reward Item", 
                     command=self.add_reward_item,
                     fg_color=self.highlight_yellow, hover_color="#ffe066", text_color=self.primary_bg).pack(side=tk.RIGHT, padx=5)
        
        self.reward_items_frame = ctk.CTkFrame(self.edit_scroll)
        self.reward_items_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Requirements frame
        requirements_header = ctk.CTkFrame(self.edit_scroll)
        requirements_header.pack(fill=tk.X, padx=5, pady=2)
        ctk.CTkLabel(requirements_header, text="Requirements:").pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(requirements_header, text="Add Requirement", 
                     command=self.add_requirement,
                     fg_color=self.highlight_yellow, hover_color="#ffe066", text_color=self.primary_bg).pack(side=tk.RIGHT, padx=5)
        
        self.requirements_frame = ctk.CTkFrame(self.edit_scroll)
        self.requirements_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # --- Condition (cond) section ---
        cond_header = ctk.CTkFrame(self.edit_scroll)
        cond_header.pack(fill=tk.X, padx=5, pady=2)
        ctk.CTkLabel(cond_header, text="Condition (cond):").pack(side=tk.LEFT, padx=5)
        self.cond_frame = ctk.CTkFrame(self.edit_scroll)
        self.cond_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ctk.CTkLabel(self.cond_frame, text="minLevel:").pack(side=tk.LEFT, padx=2)
        self.cond_minlevel = ctk.CTkEntry(self.cond_frame, width=60)
        self.cond_minlevel.pack(side=tk.LEFT, padx=2)
        ctk.CTkLabel(self.cond_frame, text="maxLevel:").pack(side=tk.LEFT, padx=2)
        self.cond_maxlevel = ctk.CTkEntry(self.cond_frame, width=60)
        self.cond_maxlevel.pack(side=tk.LEFT, padx=2)
        ctk.CTkLabel(self.cond_frame, text="mobId:").pack(side=tk.LEFT, padx=2)
        self.cond_mobid = ctk.CTkEntry(self.cond_frame, width=120)
        self.cond_mobid.pack(side=tk.LEFT, padx=2)
        
        # Save changes button
        ctk.CTkButton(self.edit_scroll, text="Save Changes", 
                     command=self.save_changes,
                     fg_color=self.highlight_yellow, hover_color="#ffe066", text_color=self.primary_bg).pack(anchor=tk.W, padx=5, pady=10)
        
    def on_reward_select(self, event):
        selection = self.treeview.selection()
        if not selection:
            return
            
        item = self.treeview.item(selection[0])
        reward_id = item['values'][0]
        
        # Find reward in our list
        reward = next((r for r in self.rewards if r['id'] == str(reward_id)), None)
        if not reward:
            return
            
        # Populate form
        self.id_var.set(reward['id'])
        self.name_var.set(reward['name'])
        self.reset_time_combo.set(reward['reset_time'])
        
        # Set description
        description = reward['element'].find('description')
        if description is not None:
            self.desc_textbox.delete("1.0", tk.END)
            self.desc_textbox.insert("1.0", description.text or "")
        
        # Clear and populate reward items
        for widget in self.reward_items_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()
                
        for reward_item in reward['element'].findall('.//reward_item'):
            frame = ctk.CTkFrame(self.reward_items_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            item_id_entry = ctk.CTkEntry(frame, placeholder_text="Item ID")
            item_id_entry.pack(side=tk.LEFT, padx=5)
            item_id_entry.insert(0, reward_item.get('id', ''))
            
            count_entry = ctk.CTkEntry(frame, placeholder_text="Count")
            count_entry.pack(side=tk.LEFT, padx=5)
            count_entry.insert(0, reward_item.get('count', ''))
            
            ctk.CTkButton(frame, text="✕", width=40, fg_color="#d9534f", hover_color="#c9302c", command=lambda f=frame: self.remove_reward_item(f)).pack(side=tk.LEFT, padx=5)
            
        # Clear and populate requirements
        for widget in self.requirements_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()
                
        for req in reward['element'].findall('.//requirement/*'):
            frame = ctk.CTkFrame(self.requirements_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            req_types = [
                "obtain_level", "login", "quest_completed", "fishing", "join_clan",
                "battle_in_olympiad", "win_in_olympiad", "kill_monster",
                "kill_monster_by_level", "kill_special_monster", "kill_boss",
                "siege_participation", "enchant_item"
            ]
            
            combo = ctk.CTkComboBox(frame, values=req_types)
            combo.pack(side=tk.LEFT, padx=5)
            combo.set(req.tag)
            
            value_entry = ctk.CTkEntry(frame, placeholder_text="Value")
            value_entry.pack(side=tk.LEFT, padx=5)
            value_entry.insert(0, req.text or "")
            
            ctk.CTkButton(frame, text="Remove", 
                         command=lambda f=frame: f.destroy()).pack(side=tk.LEFT, padx=5)
                         
        # --- Populate cond fields ---
        cond = reward['element'].find('cond')
        minlevel = maxlevel = mobid = ""
        if cond is not None:
            and_elem = cond.find('and')
            if and_elem is not None:
                for child in and_elem:
                    if child.tag == 'player':
                        if 'minLevel' in child.attrib:
                            minlevel = child.attrib['minLevel']
                        if 'maxLevel' in child.attrib:
                            maxlevel = child.attrib['maxLevel']
                    if child.tag == 'target' and 'mobId' in child.attrib:
                        mobid = child.attrib['mobId']
            else:
                # handle <cond><target .../></cond> or <cond><player .../></cond>
                for child in cond:
                    if child.tag == 'player':
                        if 'minLevel' in child.attrib:
                            minlevel = child.attrib['minLevel']
                        if 'maxLevel' in child.attrib:
                            maxlevel = child.attrib['maxLevel']
                    if child.tag == 'target' and 'mobId' in child.attrib:
                        mobid = child.attrib['mobId']
        self.cond_minlevel.delete(0, tk.END)
        self.cond_minlevel.insert(0, minlevel)
        self.cond_maxlevel.delete(0, tk.END)
        self.cond_maxlevel.insert(0, maxlevel)
        self.cond_mobid.delete(0, tk.END)
        self.cond_mobid.insert(0, mobid)
        
    def load_xml(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if not file_path:
            return
            
        try:
            self.tree = ET.parse(file_path)
            self.current_file = file_path
            self.rewards = []
            
            # Clear existing items
            for item in self.treeview.get_children():
                self.treeview.delete(item)
            
            # Load rewards
            for reward in self.tree.findall(".//one_day_reward"):
                # Get requirements text
                requirements = []
                for req in reward.findall('.//requirement/*'):
                    requirements.append(f"{req.tag}: {req.text}")
                requirements_text = ", ".join(requirements)
                
                # Get rewards text
                rewards = []
                for reward_item in reward.findall('.//reward_item'):
                    rewards.append(f"ID:{reward_item.get('id')}x{reward_item.get('count')}")
                rewards_text = ", ".join(rewards)
                
                reward_data = {
                    'id': reward.find('id').text,
                    'name': reward.find('name').text,
                    'description': reward.find('description').text,
                    'reset_time': reward.find('reset_time').text,
                    'element': reward
                }
                self.rewards.append(reward_data)
                self.treeview.insert("", tk.END, values=(
                    reward_data['id'],
                    reward_data['name'],
                    reward_data['description'],
                    reward_data['reset_time'],
                    requirements_text,
                    rewards_text
                ))
                
            messagebox.showinfo("Success", "XML file loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load XML file: {str(e)}")
            
    def save_xml(self):
        if not self.current_file:
            self.current_file = filedialog.asksaveasfilename(
                defaultextension=".xml",
                filetypes=[("XML files", "*.xml")]
            )
            if not self.current_file:
                return
                
        try:
            writer = CustomXMLWriter(self.tree)
            writer.write(self.current_file)
            messagebox.showinfo("Success", "XML file saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save XML file: {str(e)}")
            
    def add_reward(self):
        # Create new reward element
        reward = ET.Element("one_day_reward")
        
        # Add basic elements with proper indentation
        ET.SubElement(reward, "id").text = "0"
        ET.SubElement(reward, "name").text = "New Reward"
        ET.SubElement(reward, "description").text = "New reward description"
        ET.SubElement(reward, "reset_time").text = "SINGLE"
        
        # Add empty reward_items with proper structure
        reward_items = ET.SubElement(reward, "reward_items")
        
        # Add empty requirement with proper structure
        requirement = ET.SubElement(reward, "requirement")
        
        # Add to tree
        self.tree.getroot().append(reward)
        
        # Update UI
        self.rewards.append({
            'id': "0",
            'name': "New Reward",
            'reset_time': "SINGLE",
            'element': reward
        })
        
        # Get requirements and rewards text for display
        requirements_text = ""
        rewards_text = ""
        
        self.treeview.insert("", tk.END, values=(
            "0",
            "New Reward",
            "New reward description",
            "SINGLE",
            requirements_text,
            rewards_text
        ))
        
    def add_reward_item(self, item_id="", count=""):
        frame = ctk.CTkFrame(self.reward_items_frame)
        frame.pack(fill=tk.X, padx=5, pady=2)
        
        item_id_entry = ctk.CTkEntry(frame, placeholder_text="Item ID")
        item_id_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        if item_id:
            item_id_entry.insert(0, item_id)
            
        count_entry = ctk.CTkEntry(frame, placeholder_text="Count")
        count_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        if count:
            count_entry.insert(0, count)
            
        remove_btn = ctk.CTkButton(frame, text="✕", width=40, fg_color="#d9534f", hover_color="#c9302c", text_color="white")
        remove_btn.pack(side=tk.LEFT, padx=5)
        remove_btn.configure(command=lambda f=frame: self.remove_reward_item(f))
        
    def remove_reward_item(self, frame):
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this reward item?"):
            frame.destroy()
        
    def add_requirement(self, req_type="", value=""):
        frame = ctk.CTkFrame(self.requirements_frame)
        frame.pack(fill=tk.X, padx=5, pady=2)
        
        req_types = [
            "obtain_level", "login", "quest_completed", "fishing", "join_clan",
            "battle_in_olympiad", "win_in_olympiad", "kill_monster",
            "kill_monster_by_level", "kill_special_monster", "kill_boss",
            "siege_participation", "enchant_item"
        ]
        
        combo = ctk.CTkComboBox(frame, values=req_types, width=150)
        combo.pack(side=tk.LEFT, padx=5)
        if req_type:
            combo.set(req_type)
            
        value_entry = ctk.CTkEntry(frame, placeholder_text="Value")
        value_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        if value:
            value_entry.insert(0, value)
            
        remove_btn = ctk.CTkButton(frame, text="✕", width=40, fg_color="#d9534f", hover_color="#c9302c", text_color="white")
        remove_btn.pack(side=tk.LEFT, padx=5)
        remove_btn.configure(command=lambda f=frame: self.remove_requirement(f))
        
    def remove_requirement(self, frame):
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this requirement?"):
            frame.destroy()
        
    def save_changes(self):
        selection = self.treeview.selection()
        if not selection:
            return
            
        item = self.treeview.item(selection[0])
        reward_id = item['values'][0]
        
        # Find reward in our list
        reward = next((r for r in self.rewards if r['id'] == str(reward_id)), None)
        if not reward:
            return
            
        # Update basic info
        reward['element'].find('id').text = self.id_var.get()
        reward['element'].find('name').text = self.name_var.get()
        reward['element'].find('reset_time').text = self.reset_time_combo.get()
        
        # Update description
        description = reward['element'].find('description')
        if description is not None:
            description.text = self.desc_textbox.get("1.0", tk.END).strip()
        
        # Update reward items
        reward_items = reward['element'].find('reward_items')
        reward_items.clear()
        
        for frame in self.reward_items_frame.winfo_children():
            if isinstance(frame, ctk.CTkFrame):
                entries = frame.winfo_children()
                if len(entries) >= 2:
                    item_id = entries[0].get()
                    count = entries[1].get()
                    if item_id and count:
                        item = ET.SubElement(reward_items, "reward_item")
                        item.set('id', item_id)
                        item.set('count', count)
                        
        # Update requirements
        requirement = reward['element'].find('requirement')
        requirement.clear()
        
        for frame in self.requirements_frame.winfo_children():
            if isinstance(frame, ctk.CTkFrame):
                entries = frame.winfo_children()
                if len(entries) >= 2:
                    req_type = entries[0].get()
                    value = entries[1].get()
                    if req_type and value:
                        req = ET.SubElement(requirement, req_type)
                        req.text = value
                        
        # --- Save cond fields ---
        minlevel = self.cond_minlevel.get().strip()
        maxlevel = self.cond_maxlevel.get().strip()
        mobid = self.cond_mobid.get().strip()
        cond = reward['element'].find('cond')
        if minlevel or maxlevel or mobid:
            if cond is None:
                cond = ET.SubElement(reward['element'], 'cond')
            # Remove all children
            for child in list(cond):
                cond.remove(child)
            and_elem = ET.SubElement(cond, 'and')
            if minlevel or maxlevel:
                player_elem = ET.SubElement(and_elem, 'player')
                if minlevel:
                    player_elem.set('minLevel', minlevel)
                if maxlevel:
                    player_elem.set('maxLevel', maxlevel)
            if mobid:
                target_elem = ET.SubElement(and_elem, 'target')
                target_elem.set('mobId', mobid)
        else:
            # Remove cond if exists and all fields are empty
            if cond is not None:
                reward['element'].remove(cond)
        
        # Update treeview
        self.treeview.item(selection[0], values=(
            self.id_var.get(),
            self.name_var.get(),
            self.desc_textbox.get("1.0", tk.END).strip(),
            self.reset_time_combo.get(),
            "Requirements",
            "Rewards"
        ))
        
        messagebox.showinfo("Success", "Changes saved successfully!")
        
    def remove_selected_reward(self):
        selection = self.treeview.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a reward to remove")
            return
            
        if not messagebox.askyesno("Confirm", "Are you sure you want to remove this reward?"):
            return
            
        item = self.treeview.item(selection[0])
        reward_id = item['values'][0]
        
        # Find reward in our list
        reward = next((r for r in self.rewards if r['id'] == str(reward_id)), None)
        if not reward:
            return
            
        # Remove from XML tree
        root = self.tree.getroot()
        root.remove(reward['element'])
        
        # Remove from our rewards list
        self.rewards.remove(reward)
        
        # Remove from treeview
        self.treeview.delete(selection[0])
        
        # Clear edit form
        self.clear_edit_form()
        
        messagebox.showinfo("Success", "Reward removed successfully!")
        
    def clear_edit_form(self):
        self.id_var.set("")
        self.name_var.set("")
        self.desc_textbox.delete("1.0", tk.END)
        self.reset_time_combo.set("")
        
        # Clear reward items
        for widget in self.reward_items_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()
                
        # Clear requirements
        for widget in self.requirements_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()
                
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = XMLRewardEditor()
    app.run() 