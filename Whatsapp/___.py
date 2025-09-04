from Whatsapp import Extra as ex,SETTINGS

# Shared Module
ban_list : list = None
seen_ids : dict = None
admin_list  : list =None
AdminNAME = "BITS - Rohit"

# --- change vars --- #
# these changes will let us know if list is empty initially or after change it is empty.
# if empty after change then means we still need to save them . else don't save.
ban_change = False
admin_change = False

def load() -> None:
    global admin_list
    loaded_admins = ex.pick_adminList()
    admin_list = loaded_admins if loaded_admins else ["917678686855"]
    print("#=== Admin List loaded ===#")
    if SETTINGS.DEBUG :  print(admin_list)

    global ban_list
    ban_list = ex.pick_banlist()
    print("#=== Ban List loaded ===#")
    if SETTINGS.DEBUG : print(ban_list)

    global seen_ids
    seen_ids = ex.pick_ids()
    print("#=== Seen IDS loaded ===#")
    if SETTINGS.DEBUG : print(seen_ids)

