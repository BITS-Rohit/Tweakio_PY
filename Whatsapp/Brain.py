
from Whatsapp import  SETTINGS,_,pre_dir,Selectors_Config
from Whatsapp.BrowserManager import CusBrowser
import playwright.sync_api as p

#-----------------------------------------------------------------------------------------------------------------------
debug = SETTINGS.DEBUG
refreshTime = SETTINGS.REFRESH_TIME
is_global = False #Initial value to be False
browser = CusBrowser.getInstance() # Global instance for the singleton browser
#-----------------------------------------------------------------------------------------------------------------------

def mess_handle(page : p.Page) ->None :
    # we will work for on page passed down by the login methods in webLogin
    pass






if __name__ == "__main__":
    mess_handle()