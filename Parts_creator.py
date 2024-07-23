import json

# Define the dictionary with parts categories and file locations
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

def display_categories(parts_file_list):
    print("Available Categories:")
    for i, category in enumerate(parts_file_list.keys(), 1):
        print(f"{i}. {category}")

def get_user_selection(parts_file_list):
    display_categories(parts_file_list)
    while True:
        try:
            choice = int(input("Enter the number of the category you want to update: ").strip())
            if 1 <= choice <= len(parts_file_list):
                selected_category = list(parts_file_list.keys())[choice - 1]
                return selected_category
            else:
                print("Invalid choice. Please enter a number corresponding to the categories listed.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def load_file(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} could not be decoded.")
        return None

def display_entries(data):
    # Print the entire data structure to help with debugging
    print("Loaded Data:")
    
    if not isinstance(data, list):
        print("Error: Data is not a list.")
        return

    # Assuming the list contains dictionaries and we need to find the relevant dictionary
    for item in data:
        if isinstance(item, dict):
            entries = item.get("Value", {}).get("entries", [])
            if not entries:
                print("No entries found.")
                return

            print("Available Entries:")
            for i, entry in enumerate(entries, 1):
                entry_key = entry.get("Key", "Unknown")
                part_types = entry.get("Value", {}).get("data", {}).get("PartTypes", {}).get("PartEnumType", {}).get("partType", "Unknown")
                sprite = entry.get("Value", {}).get("data", {}).get("Sprite", {}).get("StringType", {}).get("_string", "Unknown")
                size_x = entry.get("Value", {}).get("data", {}).get("SizeX", {}).get("IntType", {}).get("_int", "Unknown")
                size_y = entry.get("Value", {}).get("data", {}).get("SizeY", {}).get("IntType", {}).get("_int", "Unknown")

                print(f"{i}. Key: {entry_key}, PartTypes: {part_types}, Sprite: {sprite}, SizeX: {size_x}, SizeY: {size_y}")
        else:
            print("Error: Unexpected data format in the list.")

def get_entry_selection(data):
    while True:
        try:
            choice = int(input("Enter the number of the entry you want to base your new part on: ").strip())
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        entries = item.get("Value", {}).get("entries", [])
                        if 1 <= choice <= len(entries):
                            selected_entry = entries[choice - 1]
                            return selected_entry
            print("Invalid choice. Please enter a number corresponding to the entries listed.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    # Get user selection
    selected_category = get_user_selection(parts_file_list)

    # Load the corresponding file
    file_path = parts_file_list[selected_category]
    data = load_file(file_path)

    if data is not None:
        print(f"Data from {selected_category} file loaded successfully.")
        # Display entries with details
        display_entries(data)
        
        # Get entry selection
        selected_entry = get_entry_selection(data)
        print(f"You selected: {selected_entry}")
        # Proceed with further operations, e.g., creating new parts based on the selected entry

if __name__ == "__main__":
    main()
