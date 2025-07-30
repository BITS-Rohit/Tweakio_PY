from Whatsapp import Extra as ex

# Shared Module
ban_list : list = None
seen_ids : dict = None
admin_list  : list =None
AdminNAME = "BITS - Rohit"

def load() -> None:
    global admin_list
    loaded_admins = ex.pick_adminList()
    admin_list = loaded_admins if loaded_admins else ["917678686855"]
    print("#=== Admin List loaded ===#")
    print(admin_list)

    global ban_list
    ban_list = ex.pick_banlist()
    print("#=== Ban List loaded ===#")
    print(ban_list)

    global seen_ids
    seen_ids = ex.pick_ids()
    print("#=== Seen IDS loaded ===#")
    # print(seen_ids)




