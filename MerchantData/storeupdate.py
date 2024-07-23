
#this is used to update the store.json file
# inital idea is to use json handeling as  a dictionary and append additions specified in command line to update the json file automatically
# store list:
import json

# Map the group names to their corresponding data from Shop_Groups
def map_target_stores(shop_groups, target_stores):
    result = set()
    for item in target_stores:
        if item in shop_groups:
            result.update(shop_groups[item])  # Add all items from the group
        else:
            result.add(item)  # Add individual store names that are not groups
    return result

def update_offer_data( new_offers, target_stores):
    with open("MerchantData/StoreData.json", "r") as store_file:
        data = json.load(store_file)
    for store in data:
        if "Value" in store and "entries" in store["Value"]:
            for entry in store["Value"]["entries"]:
                if entry["Key"] in target_stores and "Value" in entry and "data" in entry["Value"]:
                    
                    if "OfferTable" in entry["Value"]["data"]:
                        offer_table = entry["Value"]["data"]["OfferTable"]
                        if "StringListType" in offer_table:
                            string_list_type = offer_table["StringListType"]
                            if "_lsstring" in string_list_type:
                                string_list_type["_lsstring"].extend(new_offers)
                            if "InitValue" in string_list_type:
                                string_list_type["InitValue"].extend(new_offers)
                   
                    if "AmountOffer" in entry["Value"]["data"]:
                        AmountOffer =["Value"]["data"]["AmountOffer"]
                        if "IntListType" in AmountOffer:
                            IntListType = AmountOffer["IntListType"]
                            if "_lsint" in string_list_type:
                                IntListType["_lsint"].extend([IntListType["_lsint"][-1]] * len(new_offers))
                            if "InitValue" in string_list_type:
                                IntListType["InitValue"].extend([IntListType["InitValue"][-1]] * len(new_offers))

                    if "OfferPriceOffset" in entry["Value"]["data"]:
                        OfferPriceOffset =["Value"]["data"]["OfferPriceOffset"]
                        if "FloatListType" in OfferPriceOffset:
                            FloatListType = OfferPriceOffset["FloatListType"]
                            if "_lsfloat" in string_list_type:
                                FloatListType["_lsfloat"].extend([FloatListType["_lsfloat"][-1]] * len(new_offers))
                            if "InitValue" in string_list_type:
                                FloatListType["InitValue"].extend([FloatListType["InitValue"][-1]] * len(new_offers))
                    if "OfferRestock" in entry["Value"]["data"]:
                        OfferRestock =["Value"]["data"]["OfferRestock"]
                        if "BoolListType" in OfferRestock:
                            BoolListType = OfferRestock["BoolListType"]
                            if "_lsbool" in string_list_type:
                                BoolListType["_lsbool"].extend([BoolListType["_lsbool"][-1]] * len(new_offers))
                            if "InitValue" in string_list_type:
                                BoolListType["InitValue"].extend([BoolListType["InitValue"][-1]] * len(new_offers))

                    if "OfferCondition" in entry["Value"]["data"]:
                        OfferCondition =["Value"]["data"]["OfferCondition"]
                        if "ItemConditionEnumListType" in OfferCondition:
                            ItemConditionEnumListType = OfferCondition["ItemConditionEnumListType"]
                            if "itemConditionList" in string_list_type:
                                ItemConditionEnumListType["itemConditionList"].extend([ItemConditionEnumListType["itemConditionList"][-1]] * len(new_offers))
                            if "InitValue" in string_list_type:
                                ItemConditionEnumListType["InitValue"].extend([ItemConditionEnumListType["InitValue"][-1]] * len(new_offers))

                    if "OfferQuality"in entry["Value"]["data"]:
                        OfferQuality =["Value"]["data"]["OfferQuality"]
                        if "ItemQualityEnumListType" in OfferQuality:
                            ItemQualityEnumListType = OfferQuality["ItemQualityEnumListType"]
                            if "itemQualityList" in string_list_type:
                                ItemQualityEnumListType["itemQualityList"].extend([ItemQualityEnumListType["itemQualityList"][-1]] * len(new_offers))
                            if "InitValue" in string_list_type:
                                ItemQualityEnumListType["InitValue"].extend([ItemQualityEnumListType["InitValue"][-1]] * len(new_offers))
    print(json.dumps(data, indent=4))

    # Optionally, save the modified JSON data back to the file
    with open("MerchantData/StoreData.json", "w") as store_file:
        json.dump(data, store_file, indent=4)
                    
Shop_Groups = {
    "cheat_parts": {"CheatShipPartsMerchant1"}, "cheat_ships": {"CheatShipMerchant1"}, "cheat_weps": {"CheatShipPartsMerchant2"},
    "all_ships": {"CheatShipMerchant1","store_Blueglade_ShipStore","store_Everspring_ShipStore","store_AKShipwright_0","SilberblumShipMerchant0","SilberblumShipMerchant2","store_Ship_DawnIslesTown","store_Ship_DawnIslesTown_DLC","store_Ship_EverspringTown","store_Ship_LaventumCity","store_Ship_LaventumIndustrialYard","store_Ship_FirefortCity","store_Ship_FindhornVillage","store_Ship_GreenvaleTown","store_Com_Ship_1stSuthseg","store_Com_Ship_2ndSuthseg","store_Com_Ship_3rdSuthseg","store_Com_Ship_4thSuthseg","store_Com_Ship_2ndAecerlian","store_Com_Ship_7thAecerlian","store_Com_Ship_32ndNVRN","store_Com_Ship_SunvaleConglomerate","store_Com_Ship_TheTeutons","store_Com_Ship_TheSuthsegianGarrison","store_Com_Ship_ThePlowerRebellion","store_Com_Ship_Brotherhood","store_Com_Ship_DisciplesOfTheHuntingGod","store_Com_Ship_DisciplesOfEvergreenQueen","store_Com_Ship_CoilWorshipper","store_Com_Ship_FarmerGuild","store_Com_Ship_BankofFoirthe"},
    "all_parts+shops": {"SilberblumShipPartsMerchant0","PirnmillShipPartsMerchant0","CheatShipPartsMerchant1","CheatShipPartsMerchant2","store_Crossington_PartsStore","store_Part_AberdoniaTown","store_Part_CrossingtonTown","store_Part_BluegladeTown","store_Part_FostertonTown","store_Part_MiddletonTown","store_Part_StreampoolTown",}
}

# Read the JSON data from the file



new_offers_input = input("Enter the items to be added, separated by commas: ")
target_stores_input = input("Enter the store keys to be updated, separated by commas: ")

# Split the input strings into lists
new_offers = [item.strip() for item in new_offers_input.split(",")]
target_stores = [store.strip() for store in target_stores_input.split(",")]

# Get the updated list of store names
updated_stores = map_target_stores(Shop_Groups, target_stores)

update_offer_data( new_offers, updated_stores)
