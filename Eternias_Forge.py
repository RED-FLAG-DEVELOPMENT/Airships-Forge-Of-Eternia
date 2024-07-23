import itertools
import re
import sys
import tkinter as tk
from tkinter import ttk
import json

# Global variable to store the loaded data
loaded_data = {}
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

def update_created_parts_display():
    created_parts_text.config(state=tk.NORMAL)
    created_parts_text.delete("1.0", tk.END)
    for part in created_parts:
        created_parts_text.insert(tk.END, f"{part}\n")
    created_parts_text.config(state=tk.DISABLED)

def add_created_part():
    new_part_key = tree.item(tree.selection())["values"][0]
    if new_part_key and new_part_key not in created_parts:
        created_parts.append(new_part_key)
        update_created_parts_display()

def delete_created_part():
    selected_part = created_parts_text.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
    if selected_part in created_parts:
        created_parts.remove(selected_part)
        update_created_parts_display()

##########################################################################################################
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
        with open(current_file, 'r') as file:
            data = json.load(file)
        
        for item in data:
            if isinstance(item, dict):
                for entry in item.get("Value", {}).get("entries", []):
                    key = entry["Key"]
                    if key in loaded_data:
                        entry["Value"]["data"] = loaded_data[key]
        
        with open(current_file, 'w') as file:
            json.dump(data, file, indent=4)
        
        debug_print("File saved successfully.")
    except Exception as e:
        debug_print(f"Error saving file: {e}")

def create_new_part():
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
        "Value": {
            "selected": False,
            "data": item_data
        }
    }
    
    # Append the new entry to the loaded_data
    loaded_data[new_key] = item_data
    created_parts.append(new_key)
    update_created_parts_display()
    
    # Update the tree
    sprite = new_entry.get("Sprite", {}).get("StringType", {}).get("_string", "N/A")
    size_x = new_entry.get("SizeX", {}).get("IntType", {}).get("_int", "N/A")
    size_y = new_entry.get("SizeY", {}).get("IntType", {}).get("_int", "N/A")
    
    tree.insert("", "end", values=(new_key, sprite, size_x, size_y))
     # Automatically select and view the new part
    for row in tree.get_children():
        if tree.item(row)["values"][0] == new_key:
            tree.selection_set(row)
            view_data()
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

def delete_entry():
    selected_item = tree.selection()
    if not selected_item:
        debug_print("No item selected for deleting.")
        return
    
    item_key = tree.item(selected_item)["values"][0]
    
    if item_key in created_parts:
        created_parts.remove(item_key)
        update_created_parts_display()

    if item_key in loaded_data:
        del loaded_data[item_key]
        update_json_data()
        save_to_file()
        debug_print(f"Entry {item_key} deleted successfully.")
    else:
        debug_print(f"Entry {item_key} not found in loaded data.")

    ########################################################################################################        
    # delete from database
    debug_print("Updating ItemTable/Database.json")
    try:
        with open("ItemTable/Database.json", "r") as db_file:
            item_table_data = json.load(db_file)
    except Exception as e:
        debug_print(f"Error opening ItemTable/Database.json: {e}")
        return
    try:
        for db_entry in item_table_data:
            if db_entry["Key"] == "ItemTable":
                for entry in db_entry["Value"]["entries"]:
                    if entry["Key"] == item_key:
                        del entry[item_key]
                        debug_print(f"removed entry with key {item_key}")
                        break

        with open("ItemTable/Database.json", "w") as db_file:
            json.dump(item_table_data, db_file, indent=4)
        debug_print("ItemTable/Database.json updated successfully.")
    except Exception as e:
        debug_print(f"Error updating ItemTable/Database.json: {e}")
    
    ########################################################################################################        
    # delete from shops
    
    # Final Cleanup
    tree.delete(selected_item)

def update_json_data():
    global loaded_data, current_file
    try:
        with open(current_file, 'r') as file:
            data = json.load(file)
        
        for item in data:
            if isinstance(item, dict):
                entries = item.get("Value", {}).get("entries", [])
                item["Value"]["entries"] = [entry for entry in entries if entry["Key"] in loaded_data]

        with open(current_file, 'w') as file:
            json.dump(data, file, indent=4)
        
        debug_print("JSON data updated successfully.")
    except Exception as e:
        debug_print(f"Error updating JSON data: {e}")


    

def update_in_stores():
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

def update_database():
    debug_print("Updating ItemTable/Database.json")
    try:
        with open("ItemTable/Database.json", "r") as db_file:
            item_table_data = json.load(db_file)
    except Exception as e:
        debug_print(f"Error opening ItemTable/Database.json: {e}")
        return

    items_to_update = created_parts.copy()

    if not items_to_update:
        selected_item = tree.selection()
        items_to_update.append(tree.item(selected_item)["values"][0])

    try:
        for part_key in items_to_update:
                #sanity check
                for db_entry in item_table_data:
                            if db_entry["Key"] == "ItemTable":
                                for entry in db_entry["Value"]["entries"]:
                                    if entry["Key"] == part_key:
                                        debug_print(f"{part_key} already exists in ItemTable")
                                        return
                item = loaded_data[part_key]
                if isinstance(item, dict):
                    id_value = item.get("ID", {}).get("StringType", {}).get("_string")
                    if id_value:
                        for db_entry in item_table_data:
                            if db_entry["Key"] == "ItemTable":
                                for entry in db_entry["Value"]["entries"]:
                                    if entry["Key"] == id_value:
                                        new_entry = entry.copy()
                                        new_entry["Key"] = part_key
                                        db_entry["Value"]["entries"].append(new_entry)
                                        debug_print(f"Added new entry with key {part_key} based on ID {id_value}")
                                        break

        with open("ItemTable/Database.json", "w") as db_file:
            json.dump(item_table_data, db_file, indent=4)
        debug_print("ItemTable/Database.json updated successfully.")
    except Exception as e:
        debug_print(f"Error updating ItemTable/Database.json: {e}")



###################################################################################################################################################################################    
# Create the main application window
root = tk.Tk()
root.title("Parts File Loader")

# Create and pack the debug display
debug_display = tk.Text(root, height=5, state=tk.NORMAL)
debug_display.pack(pady=10, fill='both', expand=True)
sys.stdout = RedirectText(debug_display)

# Add a text widget to display created parts
created_parts_text = tk.Text(root, height=1, state=tk.DISABLED)
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

# Create and pack the data display frame
data_display = tk.Text(root, height=20, wrap=tk.WORD)
data_display.pack(pady=10, fill='both', expand=True)



# Create and pack the Save button
save_button = tk.Button(root, text="Save", command=save_data)
save_button.pack(side=tk.RIGHT, padx=10, pady=10)

# Create and pack the Create New Part button
create_new_part_button = tk.Button(root, text="Create New Part", command=create_new_part)
create_new_part_button.pack(side=tk.RIGHT, padx=10, pady=10)

# Create and pack the Delete button
delete_button = tk.Button(root, text="Delete", command=delete_entry)
delete_button.pack(side=tk.RIGHT, padx=10, pady=10)

# Create and pack the update in stores button
update_stores_button = tk.Button(root, text="Update in Stores", command=update_in_stores)
update_stores_button.pack(pady=10)

update_database_button = tk.Button(root, text="Update Database", command=update_database)
update_database_button.pack(pady=10)

# Create and pack the listbox for selecting stores
store_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)
for store in all_parts_shops:
    store_listbox.insert(tk.END, store)
store_listbox.pack(pady=10, fill='both', expand=True)

# Run the application
root.mainloop()
