import itertools
import os, re, sys
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
import json

# Global variable to store the loaded data
loaded_data = {}
database_data = {}
current_file = ""
created_parts = []


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
all_parts_shops = ["SilberblumShipPartsMerchant0","PirnmillShipPartsMerchant0","CheatShipPartsMerchant1","CheatShipPartsMerchant2","store_Crossington_PartsStore","store_Part_AberdoniaTown","store_Part_CrossingtonTown","store_Part_BluegladeTown","store_Part_FostertonTown","store_Part_MiddletonTown","store_Part_StreampoolTown"]

class RedirectText:
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)

    def flush(self):
        pass

##############################################################################################################################################
# Ship grid window

def list_grid_files(directory='./ShipsData/GridLayout'):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.json')]

def load_grid_layout(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['PartGrid']

def get_next_ship_number(directory='./ShipsData/GridLayout'):
    # Get the list of files and extract the numbers
    files = list_grid_files(directory)

    # Extract numbers from filenames and find the largest one
    def extract_number(file_name):
        match = re.search(r'\d+', file_name)
        return int(match.group()) if match else 0

    numbers = [extract_number(file) for file in files]

    # Return the next available number
    return max(numbers) + 1 if numbers else 1

def save_grid_layout_as_new(grid_data, directory='./ShipsData/GridLayout'):
    # Get the next available ship number
    next_ship_number = get_next_ship_number(directory)

    # Create the new file name using the ship number
    new_file_path = os.path.join(directory, f"{next_ship_number}.json")

    # Save the grid layout to the new file
    with open(new_file_path, 'w') as file:
        json.dump({"PartGrid": grid_data}, file, indent=4)

    return new_file_path  # Return the new file path for reference

class ColorPicker(tk.Toplevel):
    def __init__(self, parent, app):
        self.app = app  # Reference to the main application to reset the color picker reference
        super().__init__(parent)
        self.title("Color Picker")
        self.geometry("200x300")
        
        self.selected_color = tk.StringVar(value="grey")
        
        # Color values and their labels
        color_map = {
            'grey': '0 empty space',
            'blue': '1 engines',
            'green': '2 command',
            'red': '3 weapons',
            'orange': '4 armor',
            'yellow': '5 cargo'
        }
        
        # Create buttons with color as background and labels as text
        for color, label in color_map.items():
            btn = tk.Button(self, bg=color, fg='black', text=label, width=20,
                            command=lambda c=color: self.set_color(c))
            btn.pack(pady=5)  # Vertical alignment with padding
        
        #handel window closing
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_color(self, color):
        self.selected_color.set(color)
    
    def get_selected_color(self):
        return self.selected_color.get()
    
    def on_close(self):
        self.app.color_picker = None  # Reset reference in the main application
        self.destroy()

class GridDisplay(tk.Toplevel):
    def __init__(self, parent, grid_data, file_path_var, color_picker):
        super().__init__(parent)
        self.grid_data = grid_data
        self.file_path_var = file_path_var
        self.color_picker = color_picker  # Reference to the color picker
        self.title("Grid Layout Editor")
        self.geometry("600x600")

        self.canvas = tk.Canvas(self, width=600, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.draw_grid()

    def draw_grid(self):
        cell_size = 20  # Adjust as needed
        for i, row in enumerate(self.grid_data):
            for j, cell in enumerate(row):
                color = self.get_color(cell)
                self.canvas.create_rectangle(
                    j * cell_size, i * cell_size,
                    (j + 1) * cell_size, (i + 1) * cell_size,
                    fill=color, outline='black'
                )
                self.canvas.tag_bind(self.canvas.find_all()[-1], '<Button-1>', self.change_color)

    def get_color(self, value):
        colors = {0: 'grey', 1: 'blue', 2: 'green', 3: 'red', 4: 'orange', 5: 'yellow'}
        return colors.get(value, 'grey')

    def change_color(self, event):
        x, y = event.x, event.y
        cell_size = 20  # Adjust as needed
        col = x // cell_size
        row = y // cell_size

        # Get the selected color from the color picker
        selected_color = self.color_picker.get_selected_color()
        
        if selected_color:
            self.canvas.itemconfig(self.canvas.find_closest(x, y), fill=selected_color)
            self.grid_data[row][col] = self.get_value_from_color(selected_color)

    def get_value_from_color(self, color):
        color_map = {'grey': 0, 'blue': 1, 'green': 2, 'red': 3, 'orange': 4, 'yellow': 5}
        return color_map.get(color, 0)
    
    def save_grid_layout(self, file_path):
        """Save the current grid data to a JSON file."""
        grid_data_to_save = {"PartGrid": self.grid_data}
        with open(file_path, 'w') as file:
            json.dump(grid_data_to_save, file, indent=4)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ship Editor")
        self.geometry("800x600")

        self.grid_display = None
        self.color_picker = None  # Reference to the color picker

        self.file_list = ttk.Treeview(self)
        self.file_list.pack(side=tk.LEFT, fill=tk.Y)
        self.file_list.bind("<Double-1>", self.on_file_select)

        self.file_path_var = tk.StringVar()
        self.file_path_entry = tk.Entry(self, textvariable=self.file_path_var)
        self.file_path_entry.pack(fill=tk.X)

        self.open_button = tk.Button(self, text="Open Grid Layout", command=self.open_grid_layout)
        self.open_button.pack()

        self.save_button = tk.Button(self, text="Save Grid Layout", command=self.save_grid_layout)
        self.save_button.pack()

        self.save_as_button = tk.Button(self, text="Save As", command=self.save_grid_layout_as_new)  # New Save As button
        self.save_as_button.pack()

        self.populate_file_list()

    def populate_file_list(self):
        # Clear the existing entries in the Treeview
        for item in self.file_list.get_children():
            self.file_list.delete(item)
        
        # Get the list of files
        files = list_grid_files()

        # Sort files based on numeric order
        def extract_number(file_name):
            match = re.search(r'\d+', file_name)
            return int(match.group()) if match else float('inf')

        sorted_files = sorted(files, key=extract_number)
        # Add sorted files to the Treeview
        for file in sorted_files:
            self.file_list.insert('', 'end', text=file)

    def on_file_select(self, event):
        selected_item = self.file_list.selection()[0]
        file_name = self.file_list.item(selected_item, "text")
        file_path = os.path.join('./ShipsData/GridLayout', file_name)
        self.file_path_var.set(file_path)
        self.open_grid_layout()

    def open_grid_layout(self):
        file_path = self.file_path_var.get()
        if file_path:
            grid_data = load_grid_layout(file_path)
            
            # Create a new Color Picker if none exists
            if self.color_picker is None:
                self.color_picker = ColorPicker(self, self)  # Pass reference to the main application
            
            # Open Grid Display and pass the color picker
            if self.grid_display:
                self.grid_display.destroy()
            self.grid_display = GridDisplay(self, grid_data, self.file_path_var, self.color_picker)

    def save_grid_layout(self):
        """Save the current grid layout to the existing file or ask for a new one if no file selected."""
        if self.grid_display:
            file_path = self.file_path_var.get()  # Get the current file path
            if not file_path:  # If no file path, prompt for new file name
                file_path = self.prompt_for_save_as()
            if file_path:
                self.grid_display.save_grid_layout(file_path)
                self.file_path_var.set(file_path)  # Set the new file path in case of "Save As"

    def save_grid_layout_as_new(self):
        if self.grid_display:
            # Save the grid data to a new file with an incremented ship number
            new_file_path = save_grid_layout_as_new(self.grid_display.grid_data)
            self.file_path_var.set(new_file_path)  # Update the file path variable
            self.populate_file_list()  # Refresh the file list to include the new file

################################################################################################################################## 

def debug_print(message):
    debug_display.insert(tk.END, message + "\n")
    debug_display.see(tk.END)

def load_database_data():
    global database_data
    try:
        with open("ItemTable/Database.json", 'r') as file:
            data = json.load(file)
            debug_print("Database file loaded successfully.")
            database_data.clear()
            for item in data:
                if "Value" in item and "entries" in item["Value"]:
                    for entry in item["Value"]["entries"]:
                        if "Key" in entry and "Value" in entry:
                            key = entry["Key"]
                            database_data[key] = entry["Value"]
    except Exception as e:
        debug_print(f"Error loading database data: {e}")


def load_file(filename):
    global loaded_data, current_file
    current_file = filename
    debug_print(f"Loading file: {filename}")  # Debug print
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            debug_print("Data loaded successfully")  # Debug print
            #debug_print("Data structure:")  # Debug print to show the structure
            #debug_print(json.dumps(data, indent=4))  # Pretty print the data structure
            display_entries(data)

              # Extract all entries and store them in loaded_data
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        entries = item.get("Value", {}).get("entries", [])
                        for entry in entries:
                            if isinstance(entry, dict):
                                key = entry.get("Key", "N/A")
                                value = entry.get("Value", {})
                                loaded_data[key] = value

    except Exception as e:
        debug_print(f"Error loading file: {e}")
        return

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
                        #debug_print(f"Adding entry: {key}, {sprite}, {size_x}, {size_y}")
                        
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
    global loaded_data
    selected_item = tree.selection()
    if selected_item:
        item_key = tree.item(selected_item)["values"][0]
        item_data = loaded_data.get(item_key, {})
        if not item_data:
            debug_print(f"{item_key} does not exist. Please create this part")
        update_data_display(item_key)
        update_database_display(item_key)
    else:
        debug_print("No item selected.")

def update_data_display(key):
    # Clear existing data in data_display
    if key in loaded_data:
        entry_data = loaded_data[key]
        formatted_data = json.dumps(entry_data, indent=4)
        data_display.delete("1.0", tk.END)
        data_display.insert(tk.END, formatted_data)
    else:
        debug_print(f"No entry found for key: {key}")

def update_database_display(key):
    global database_data
    if key in database_data:
        entry_data = database_data[key]
        formatted_data = json.dumps(entry_data, indent=4)
        database_display.delete("1.0", tk.END)
        database_display.insert(tk.END, formatted_data)
    else:
        debug_print(f"No entry found for key: {key}")


def update_created_parts_display():
    created_parts_text.config(state=tk.NORMAL)  # Enable editing
    created_parts_text.delete("1.0", tk.END)  # Clear the current text
    created_parts_text.insert(tk.END, ", ".join(created_parts))  # Insert the parts as a comma-separated string
    created_parts_text.config(state=tk.DISABLED)  # Disable editing

def add_created_part():
    new_part_key = tree.item(tree.selection())["values"][0]
    if new_part_key and new_part_key not in created_parts:
        debug_print(f"Adding {new_part_key} to list")
        created_parts.append(new_part_key)
        update_created_parts_display()

def delete_created_part():
    selected_part = tree.item(tree.selection())["values"][0]
    if selected_part in created_parts:
        created_parts.remove(selected_part)
        update_created_parts_display()

            


##########################################################################################################
def save_data():
    global loaded_data, database_data
    selected_item = tree.selection()
    if not selected_item:
        debug_print("No item selected for saving.")
        return
    
    item_key = tree.item(selected_item)["values"][0]
    
    try:
        # Get the edited data from the part data display
        edited_data = data_display.get("1.0", tk.END).strip()
        try:
            parsed_data = json.loads(edited_data)
        except json.JSONDecodeError as e:
            debug_print(f"Error parsing JSON data from part data display: {e}")
            return

        # Get the edited data from the DB data display
        edited_database_data = database_display.get("1.0", tk.END).strip()
        try:
            parsed_database = json.loads(edited_database_data)
        except json.JSONDecodeError as e:
            debug_print(f"Error parsing JSON data from DB data display: {e}")
            return

        # Update the global loaded_data and database_data
        loaded_data[item_key] = parsed_data
        database_data[item_key] = parsed_database
        
        # Save to the current file
        save_part_to_file()
        #save to DB
        save_part_to_db()
        debug_print(f"Data for {item_key} saved successfully.")
    except Exception as e:
        debug_print(f"Error saving data: {e}")

def save_part_to_file():
    global loaded_data, current_file
    try:
        with open(current_file, 'r') as file:
            data = json.load(file)
        
        for item in data:
            if isinstance(item, dict):
                for entry in item.get("Value", {}).get("entries", []):
                    key = entry["Key"]
                    if key in loaded_data:
                        # Directly assign the loaded data to the "data" field
                        entry["Value"] = loaded_data[key]
        
        with open(current_file, 'w') as file:
            json.dump(data, file, indent=4)
        
        debug_print("Part File saved successfully.")
    except Exception as e:
        debug_print(f"Error saving file: {e}")



def save_part_to_db():
    global database_data
    try:
        with open("ItemTable/Database.json", 'r') as file:
            data = json.load(file)
        
        for item in data:
            if isinstance(item, dict):
                for entry in item.get("Value", {}).get("entries", []):
                    key = entry["Key"]
                    if key in database_data:
                        # Directly assign the database data to the "data" field
                        entry["Value"] = database_data[key]
        
        with open("ItemTable/Database.json", 'w') as file:
            json.dump(data, file, indent=4)
        
        debug_print("DBFile saved successfully.")
    except Exception as e:
        debug_print(f"Error saving file: {e}")



def create_new_part():
    global loaded_data
    selected_item = tree.selection()
    if not selected_item:
        debug_print("No item selected for creating new part.")
        return
    
    last = tree.get_children()[-1]
    last_key = tree.item(last)["values"][0]
    item_key = tree.item(selected_item)["values"][0]
    item_data = loaded_data.get(item_key, {}).copy()
    
    # Generate new key
    Key = ["".join(x) for _, x in itertools.groupby(last_key, key=str.isdigit)]
    debug_print(f"{Key[0]}{Key[1]}")
    new_key = f"{Key[0]}{int(Key[1])+1}"
    
    # Create the new entry
    new_entry = {
        "Key": new_key,
        "Value": item_data
    }
    
    # Append the new entry to the loaded_data
    loaded_data[new_key] = item_data
    created_parts.append(new_key)
    update_created_parts_display()
    

    key = new_entry.get("Key", "N/A")
    value = new_entry.get("Value", {}).get("data", {})
    
    # Extract relevant fields
    sprite = value.get("Sprite", {}).get("StringType", {}).get("_string", "N/A")
    size_x = value.get("SizeX", {}).get("IntType", {}).get("_int", "N/A")
    size_y = value.get("SizeY", {}).get("IntType", {}).get("_int", "N/A")
    
    # Debug print for each new_entry
    #debug_print(f"Adding new_entry: {key}, {sprite}, {size_x}, {size_y}")
    
    # Insert new row into the table
    tree.insert("", "end", values=(key, sprite, size_x, size_y))
     # Automatically select and view the new part
    for item in tree.get_children():
        if tree.item(item)["values"][0] == new_key:
            # Set the selection
            tree.selection_set(item)
            # Optionally, scroll the tree view to the selected item
            tree.see(item)
            break

    # Update the JSON data and save to file
    try:
        with open(current_file, 'r') as file:
            data = json.load(file)
        
        for item in data:
            if isinstance(item, dict):
                item.get("Value", {}).get("entries", []).append(new_entry)
        
        with open(current_file, 'w') as file:
            json.dump(data, file, indent=4)
        
        debug_print(f"New part {new_key} created and saved successfully.")
        display_entries(data)
    except Exception as e:
        debug_print(f"Error creating new part: {e}")
    try:
        update_database(new_key)
    except Exception as e:
        debug_print(f"Error creating new DB Entry: {e}")

def delete_entry():
    global loaded_data
    selected_item = tree.selection()
    if not selected_item:
        debug_print("No item selected for deleting.")
        return
    
    item_key = tree.item(selected_item)["values"][0]

    # delete from temp data
    if item_key in created_parts:
        created_parts.remove(item_key)
        update_created_parts_display()
    if item_key in database_data:
        del database_data[item_key]
    if item_key in loaded_data:
        del loaded_data[item_key]
        debug_print(f"Entry {item_key} deleted successfully.")
    else:
        debug_print(f"Entry {item_key} not found in loaded data.")
    
    # Delete from parts file
    try:
        with open(current_file, 'r') as file:
            data = json.load(file)
    
        for item in data:
            if isinstance(item, dict):
                entries = item.get("Value", {}).get("entries", [])
                for i, entry in enumerate(entries):
                    if entry["Key"] == item_key:
                        del entries[i]
                        break  # Exit the loop once the item is found and deleted

        with open(current_file, 'w') as file:
            json.dump(data, file, indent=4)
    except:
        debug_print(f"Issues with deleting data from {current_file}")
    
     # Delete from database
    try:
        with open("ItemTable/Database.json", 'r') as file:
            data = json.load(file)
    
        for item in data:
            if isinstance(item, dict):
                entries = item.get("Value", {}).get("entries", [])
                for i, entry in enumerate(entries):
                    if entry["Key"] == item_key:
                        del entries[i]
                        break  # Exit the loop once the item is found and deleted
        
        with open("ItemTable/Database.json", 'w') as file:
            json.dump(data, file, indent=4)
    except:
        debug_print(f"Issues with deleting data from ItemTable/Database.json")
    
    
   
    
    ########################################################################################################        
    # delete from shops
    # todo
    # Final Cleanup
    tree.delete(selected_item)

    

def update_in_stores():
    global loaded_data
    debug_print(f"getting indices")
    selected_indices = store_listbox.curselection()
    debug_print(f"using indices {selected_indices}")
    target_stores = [all_parts_shops[i] for i in selected_indices]
    debug_print(f"using stores {target_stores}")
    if not target_stores:
        debug_print("You must select at least one shop to update")
        return
    
    if not created_parts:
        debug_print("using selected part to add to stores.")
        selected_item = tree.selection()
        created_parts.append(tree.item(selected_item)["values"][0])
        update_created_parts_display()
        if not created_parts:
            debug_print("You must create or select a part to add to stores.")
            return

    update_offer_data(created_parts, target_stores)
    debug_print(f"Updated stores: {target_stores} with new parts: {created_parts}")

def update_offer_data( new_offers, target_stores):
    debug_print("opening store data")
    try:
        with open("MerchantData\StoreData.json", "r") as store_file:
            data = json.load(store_file)
    except Exception as e:
        debug_print(f"Error opening store data: {e}")
        return

    try:
        debug_print(f"Looking to add to stores: {target_stores}")
        for store in data:
            if "Value" in store and "entries" in store["Value"]:
                for entry in store["Value"]["entries"]:
                    if entry["Key"] in target_stores and "Value" in entry and "data" in entry["Value"]:
                        if "OfferTable" in entry["Value"]["data"]:
                            debug_print("adding to OfferTable")
                            offer_table = entry["Value"]["data"]["OfferTable"]
                            if "StringListType" in offer_table:
                                string_list_type = offer_table["StringListType"]
                                if "_lsstring" in string_list_type:
                                    string_list_type["_lsstring"].extend(new_offers)
                                if "InitValue" in string_list_type:
                                    string_list_type["InitValue"].extend(new_offers)
                    
                        if "AmountOffer" in entry["Value"]["data"]:
                            debug_print("adding to AmountOffer")
                            AmountOffer =entry["Value"]["data"]["AmountOffer"]
                            if "IntListType" in AmountOffer:
                                IntListType = AmountOffer["IntListType"]
                                if "_lsint" in IntListType:
                                    IntListType["_lsint"].extend([IntListType["_lsint"][-1]] * len(new_offers))
                                if "InitValue" in IntListType:
                                    IntListType["InitValue"].extend([IntListType["InitValue"][-1]] * len(new_offers))

                        if "OfferPriceOffset" in entry["Value"]["data"]:
                            debug_print("adding to OfferPriceOffset")
                            OfferPriceOffset =entry["Value"]["data"]["OfferPriceOffset"]
                            if "FloatListType" in OfferPriceOffset:
                                FloatListType = OfferPriceOffset["FloatListType"]
                                if "_lsfloat" in FloatListType:
                                    FloatListType["_lsfloat"].extend([FloatListType["_lsfloat"][-1]] * len(new_offers))
                                if "InitValue" in FloatListType:
                                    FloatListType["InitValue"].extend([FloatListType["InitValue"][-1]] * len(new_offers))
                                    
                        if "OfferRestock" in entry["Value"]["data"]:
                            OfferRestock =entry["Value"]["data"]["OfferRestock"]
                            if "BoolListType" in OfferRestock:
                                BoolListType = OfferRestock["BoolListType"]
                                if "_lsbool" in BoolListType:
                                    BoolListType["_lsbool"].extend([BoolListType["_lsbool"][-1]] * len(new_offers))
                                if "InitValue" in BoolListType:
                                    BoolListType["InitValue"].extend([BoolListType["InitValue"][-1]] * len(new_offers))

                        if "OfferCondition" in entry["Value"]["data"]:
                            OfferCondition =entry["Value"]["data"]["OfferCondition"]
                            if "ItemConditionEnumListType" in OfferCondition:
                                ItemConditionEnumListType = OfferCondition["ItemConditionEnumListType"]
                                if "itemConditionList" in ItemConditionEnumListType:
                                    ItemConditionEnumListType["itemConditionList"].extend([ItemConditionEnumListType["itemConditionList"][-1]] * len(new_offers))
                                if "InitValue" in ItemConditionEnumListType:
                                    ItemConditionEnumListType["InitValue"].extend([ItemConditionEnumListType["InitValue"][-1]] * len(new_offers))

                        if "OfferQuality"in entry["Value"]["data"]:
                            OfferQuality =entry["Value"]["data"]["OfferQuality"]
                            if "ItemQualityEnumListType" in OfferQuality:
                                ItemQualityEnumListType = OfferQuality["ItemQualityEnumListType"]
                                if "itemQualityList" in ItemQualityEnumListType:
                                    ItemQualityEnumListType["itemQualityList"].extend([ItemQualityEnumListType["itemQualityList"][-1]] * len(new_offers))
                                if "InitValue" in ItemQualityEnumListType:
                                    ItemQualityEnumListType["InitValue"].extend([ItemQualityEnumListType["InitValue"][-1]] * len(new_offers))
        # reformat to json                            
        #print(json.dumps(data, indent=4))
        debug_print("reformating data")
        # Optionally, save the modified JSON data back to the file
        with open("MerchantData/StoreData.json", "w") as store_file:
            json.dump(data, store_file, indent=4)
        debug_print("File saved")
    except Exception as e:
        debug_print(f"Error updating store data: {e}")

def update_database(selected_key):
    global loaded_data,created_parts
    debug_print("Updating ItemTable/Database.json")
    try:
        with open("ItemTable/Database.json", "r") as db_file:
            item_table_data = json.load(db_file)
    except Exception as e:
        debug_print(f"Error opening ItemTable/Database.json: {e}")
        return

    try:  
        #sanity check
        for db_entry in item_table_data:
                    if db_entry["Key"] == "ItemTable":
                        for entry in db_entry["Value"]["entries"]:
                            if entry["Key"] == selected_key:
                                debug_print(f"{selected_key} already exists in ItemTable")
                                return
        item = loaded_data[selected_key]
        if isinstance(item, dict):
            id_value = item.get("data",{}).get("ID", {}).get("StringType", {}).get("_string")
            if id_value:
                for db_entry in item_table_data:
                    if db_entry["Key"] == "ItemTable":
                        for entry in db_entry["Value"]["entries"]:
                            if entry["Key"] == id_value:
                                new_entry = entry.copy()
                                new_entry["Key"] = selected_key
                                db_entry["Value"]["entries"].append(new_entry)
                                debug_print(f"Added new entry with key {selected_key} based on ID {id_value}")
                                break

        with open("ItemTable/Database.json", "w") as db_file:
            json.dump(item_table_data, db_file, indent=4)
        debug_print("ItemTable/Database.json updated successfully.")
    except Exception as e:
        debug_print(f"Error updating ItemTable/Database.json: {e}")


def initialize():
    load_file("PartData/CommandDatabase.json")
    load_database_data()

def open_grid_layout():
    file_path = tk.filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        grid_data = load_grid_layout(file_path)
        grid_display = GridDisplay(root, grid_data)

def save_grid_layout(grid_display):
    file_path = tk.filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        grid_display.save_grid_layout(file_path)


###################################################################################################################################################################################    
# Create the main application window
root = tk.Tk()
root.title("Parts File Loader")

# Create and pack the debug display
debug_display = tk.Text(root, height=5, state=tk.NORMAL)
debug_display.pack(pady=10, fill='both', expand=True)
sys.stdout = RedirectText(debug_display)

# Add a text widget to display created parts
created_parts_text = tk.Text(root, height=2, state=tk.DISABLED)
created_parts_text.pack(pady=5)

# Button to add a new created part
add_part_button = tk.Button(root, text="Add Part", command=add_created_part)
add_part_button.pack(pady=5)

# Button to delete the selected created part
delete_part_button = tk.Button(root, text="Delete Part", command=delete_created_part)
delete_part_button.pack(pady=5)

# Create and pack the dropdown menu
dropdown = ttk.Combobox(root, values=list(parts_file_list.keys()))
dropdown.pack(pady=10)
dropdown.bind("<<ComboboxSelected>>", on_dropdown_select)

# Create and pack the treeview for displaying entries
tree = ttk.Treeview(root, columns=("Key", "Sprite", "Size X", "Size Y"), show='headings')
tree.heading("Key", text="Key")
tree.heading("Sprite", text="Sprite")
tree.heading("Size X", text="Size X")
tree.heading("Size Y", text="Size Y")
tree.pack(pady=10, fill='both', expand=True)
tree.bind("<<TreeviewSelect>>", on_tree_select)


# Create and pack the Save button
save_button = tk.Button(root, text="Save", command=save_data)
save_button.pack(side=tk.LEFT, padx=10, pady=5)

# Create and pack the Create New Part button
create_new_part_button = tk.Button(root, text="Create New Part", command=create_new_part)
create_new_part_button.pack(side=tk.LEFT, padx=10, pady=5)

# Create and pack the Delete button
delete_button = tk.Button(root, text="Delete", command=delete_entry)
delete_button.pack(side=tk.RIGHT, padx=10, pady=5)

#create and pack the Update Database Button
update_database_button = tk.Button(root, text="Update Database", command=update_database)
update_database_button.pack(pady=10)

# Create and pack the data display frame
data_display = tk.Text(root, height=20, width=80)
data_display.pack(pady=10,side=tk.LEFT, fill='both', expand=True)

# Create and pack the database display text widget
database_display = tk.Text(root, height=20, width=80)
database_display.pack(pady=10, side=tk.RIGHT, fill='both', expand=True)

# Create and pack the update in stores button
update_stores_button = tk.Button(root, text="Update in Stores", command=update_in_stores)
update_stores_button.pack(pady=10)

# Create and pack the listbox for selecting stores
store_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)
for store in all_parts_shops:
    store_listbox.insert(tk.END, store)
store_listbox.pack(pady=10, fill='both', expand=True)

# Run the application
# Call this function at the start of the program
initialize()
#create ship application window
if __name__ == "__main__":
    app = Application()
    app.mainloop()

