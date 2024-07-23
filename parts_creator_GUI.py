import tkinter as tk
from tkinter import ttk
import json
import sys

# Global variable to store the loaded data
loaded_data = {}
current_file = ""

# Sample parts_file_list
parts_file_list = {
    "Command": "PartData/CommandDatabase.json",
    "Engine": "PartData/EngineDatabase.json",
    "Powerplant": "PartData/PowerPlantDatabase.json",
    "Protection": "PartData/ProtectionDatabase.json",
    "Storage": "PartData/StorageDatabase.json",
    "Utility": "PartData/UtilityDatabase.json",
    "Weapons": "PartData/WeaponDatabase.json",
    "Projectile": "PartData/ProjectileDatabase.json",
    "Rider Bay": "PartData/RiderBayDatabase.json",
    "Fighters": "PartData/FightersDatabase.json"
}

class RedirectText:
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)

    def flush(self):
        pass

def load_file(filename):
    global loaded_data, current_file
    current_file = filename
    debug_print(f"Loading file: {filename}")  # Debug print
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            loaded_data = {entry["Key"]: entry["Value"]["data"] for item in data if isinstance(item, dict) for entry in item.get("Value", {}).get("entries", [])}
            debug_print("Data loaded successfully")  # Debug print
            debug_print("Data structure:")  # Debug print to show the structure
            debug_print(json.dumps(data, indent=4))  # Pretty print the data structure
            display_entries(data)
    except Exception as e:
        debug_print(f"Error loading file: {e}")

def display_entries(data):
    # Clear existing entries
    for row in tree.get_children():
        tree.delete(row)

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                entries = item.get("Value", {}).get("entries", [])
                debug_print(f"Number of entries: {len(entries)}")  # Debug print
                if not entries:
                    debug_print("No entries found.")
                    return

                for entry in entries:
                    if isinstance(entry, dict):
                        key = entry.get("Key", "N/A")
                        value = entry.get("Value", {}).get("data", {})
                        
                        # Extract relevant fields
                        sprite = value.get("Sprite", {}).get("StringType", {}).get("_string", "N/A")
                        size_x = value.get("SizeX", {}).get("IntType", {}).get("_int", "N/A")
                        size_y = value.get("SizeY", {}).get("IntType", {}).get("_int", "N/A")
                        
                        # Debug print for each entry
                        debug_print(f"Adding entry: {key}, {sprite}, {size_x}, {size_y}")
                        
                        # Insert new row into the table
                        tree.insert("", "end", values=(key, sprite, size_x, size_y))
    else:
        debug_print("Data is not in expected format.")

def on_dropdown_select(event):
    selected_option = dropdown.get()
    file_path = parts_file_list.get(selected_option)
    if file_path:
        load_file(file_path)
    else:
        debug_print("File path not found.")

def on_tree_select(event):
    view_data()

def view_data():
    selected_item = tree.selection()
    if selected_item:
        item_key = tree.item(selected_item)["values"][0]
        item_data = loaded_data.get(item_key, {})
        display_data(item_data)
    else:
        debug_print("No item selected.")

def display_data(data):
    # Clear existing data in data_display
    data_display.delete("1.0", tk.END)
    
    # Format and display data
    for key, value in data.items():
        if isinstance(value, dict):
            value_str = json.dumps(value, indent=4)
        else:
            value_str = str(value)
        data_display.insert(tk.END, f"{key}:\n{value_str}\n\n")

def debug_print(message):
    debug_display.insert(tk.END, message + "\n")
    debug_display.see(tk.END)

def save_data():
    selected_item = tree.selection()
    if not selected_item:
        debug_print("No item selected for saving.")
        return
    
    item_key = tree.item(selected_item)["values"][0]
    
    try:
        # Get the edited data from the data display
        edited_data = data_display.get("1.0", tk.END).strip().split("\n\n")

        # Parse the edited data into a dictionary
        parsed_data = {}
        for entry in edited_data:
            if entry:
                key, value = entry.split(":\n", 1)
                try:
                    parsed_data[key] = json.loads(value)
                except json.JSONDecodeError as e:
                    parsed_data[key] = value  # Save as string if JSON parsing fails
                    debug_print(f"Warning: Saved '{key}' as string due to JSON decode error: {e}")

        # Update the global loaded_data
        loaded_data[item_key] = parsed_data
        
        # Save to the current file
        save_to_file()
        debug_print(f"Data for {item_key} saved successfully.")
    except Exception as e:
        debug_print(f"Error saving data: {e}")
def save_to_file():
    global loaded_data, current_file
    try:
        # Load the current file content
        with open(current_file, 'r') as file:
            data = json.load(file)
        
        # Update the data with the modified loaded_data
        for item in data:
            if isinstance(item, dict):
                entries = item.get("Value", {}).get("entries", [])
                for entry in entries:
                    if entry["Key"] in loaded_data:
                        entry["Value"]["data"] = loaded_data[entry["Key"]]

        # Save the updated data back to the file
        with open(current_file, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        debug_print(f"Error saving file: {e}")

def create_new_part():
    selected_item = tree.selection()
    if not selected_item:
        debug_print("No item selected for creating a new part.")
        return

    item_key = tree.item(selected_item)["values"][0]
    item_data = loaded_data.get(item_key, {}).copy()
    
    # Find a new key
    base_key = item_key.rstrip('0123456789')
    existing_keys = [key for key in loaded_data.keys() if key.startswith(base_key)]
    new_key = f"{base_key}{len(existing_keys)}"
    
    # Update the key in the new item
    new_item_data = item_data.copy()
    new_item_data["Key"] = new_key

    # Add the new item to loaded_data
    loaded_data[new_key] = new_item_data
    
    # Update the tree
    sprite = new_item_data.get("Sprite", {}).get("StringType", {}).get("_string", "N/A")
    size_x = new_item_data.get("SizeX", {}).get("IntType", {}).get("_int", "N/A")
    size_y = new_item_data.get("SizeY", {}).get("IntType", {}).get("_int", "N/A")
    
    tree.insert("", "end", values=(new_key, sprite, size_x, size_y))
     # Automatically select and view the new part
    for row in tree.get_children():
        if tree.item(row)["values"][0] == new_key:
            tree.selection_set(row)
            view_data()
            break
    
    debug_print(f"New part created: {new_key}")
    
    # Save the new part data
    save_data()
    debug_print(f"New part created: {new_key}")

# Create the main application window
root = tk.Tk()
root.title("Parts File Loader")

# Create and pack the debug display
debug_display = tk.Text(root, wrap=tk.NONE, height=10, state=tk.NORMAL)
debug_display.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky='ew')

# Redirect print statements to the debug display
sys.stdout = RedirectText(debug_display)
sys.stderr = RedirectText(debug_display)

# Create and pack the dropdown menu
dropdown = ttk.Combobox(root, values=list(parts_file_list.keys()))
dropdown.grid(row=1, column=0, padx=10, pady=10)
dropdown.bind("<<ComboboxSelected>>", on_dropdown_select)

# Create and pack the "Save" button
save_button = tk.Button(root, text="Save", command=save_data)
save_button.grid(row=1, column=2, padx=10, pady=10)

# Create and pack the "Create New Part" button
create_part_button = tk.Button(root, text="Create New Part", command=create_new_part)
create_part_button.grid(row=1, column=3, padx=10, pady=10)

# Create and pack the treeview for displaying entries
tree = ttk.Treeview(root, columns=("Key", "Sprite", "Size X", "Size Y"), show='headings')
tree.heading("Key", text="Key")
tree.heading("Sprite", text="Sprite")
tree.heading("Size X", text="Size X")
tree.heading("Size Y", text="Size Y")
tree.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

# Bind the treeview selection event
tree.bind("<<TreeviewSelect>>", on_tree_select)

# Create and pack the scrollable data display
data_display_frame = tk.Frame(root)
data_display_frame.grid(row=2,
 column=3, padx=10, pady=10, sticky='nsew')

data_display_scrollbar = tk.Scrollbar(data_display_frame)
data_display_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

data_display = tk.Text(data_display_frame, wrap=tk.NONE, yscrollcommand=data_display_scrollbar.set, state=tk.NORMAL)
data_display.pack(pady=10, fill='both', expand=True)
data_display_scrollbar.config(command=data_display.yview)

# Configure grid weights
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_rowconfigure(2, weight=1)

# Run the application
root.mainloop()
