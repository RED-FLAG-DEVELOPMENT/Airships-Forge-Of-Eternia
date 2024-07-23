import json

# Read the JSON data from the file
with open("MerchantData/StoreData.json", "r") as store_file:
    store_entries = json.load(store_file)

def extract_store_details(data,keyword):
    details = []
    for store in data:
        if "Value" in store and "entries" in store["Value"]:
            for entry in store["Value"]["entries"]:
                if "Key" in entry and "Value" in entry and "data" in entry["Value"]:
                    store_name = entry["Key"]
                    data_section = entry["Value"]["data"]

                    # Check if the keyword is in the store name
                   
                    if keyword.lower() in store_name.lower():
                        # Extract StoreName["_string"]
                        store_name_value = None
                        if "StoreName" in data_section:
                            store_name_section = data_section["StoreName"]
                            if "StringType" in store_name_section:
                                string_type_section = store_name_section["StringType"]
                                if "_string" in string_type_section:
                                    store_name_value = string_type_section["_string"]

                        # Extract FocusTab["MerchantPlayerOfferFilterEnumType"]["merchantPlayerOfferFilter"]
                        focus_tab_value = None
                        if "FocusTab" in data_section:
                            focus_tab_section = data_section["FocusTab"]
                            if "MerchantPlayerOfferFilterEnumType" in focus_tab_section:
                                merchant_filter_section = focus_tab_section["MerchantPlayerOfferFilterEnumType"]
                                if "merchantPlayerOfferFilter" in merchant_filter_section:
                                    focus_tab_value = merchant_filter_section["merchantPlayerOfferFilter"]

                        # Prepare details for output
                        store_details = f"Key: {store_name}"
                        if store_name_value:
                            store_details += f"\nStoreName: {store_name_value}"
                        if focus_tab_value:
                            store_details += f"\nFocusTab: {focus_tab_value}"
                        store_details += "\n"  # Add a blank line for readability
                        details.append(store_details)
    return details

def extract_store_names(data,keyword):
    details = []
    for store in data:
        if "Value" in store and "entries" in store["Value"]:
            for entry in store["Value"]["entries"]:
                if "Key" in entry and "Value" in entry and "data" in entry["Value"]:
                    
                    store_name = entry["Key"]

                    # Check if the keyword is in the store name
                    if keyword.lower() in store_name.lower():
                        # Prepare details for output
                        store_details = f'"{store_name}",'
                        details.append(store_details)
    return details

#get keyword
keyword_input = input("Enter the keyword you want to sort by (leave blank for all): ")
output_select = input("1) Detailed output  \n2) Simple output: ")
# Extract store details
if output_select == "1":
    store_details = extract_store_details(store_entries, keyword_input)
if output_select == "2":
    store_details = extract_store_names(store_entries, keyword_input)
else:
    print(f"Invalid output selector")
# Write details to a file
output_file_path = "MerchantData/StoreDetails.txt"
with open(output_file_path, "w") as output_file:
    output_file.writelines(store_details)

print(f"Store details have been written to {output_file_path}")
