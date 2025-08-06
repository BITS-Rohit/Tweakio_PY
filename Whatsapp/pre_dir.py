"""
Here we have cleanly defined all the directories we have created with desc of why they exist.
"""
import pathlib as pa
from os import mkdir

from Whatsapp import SETTINGS

# -----------------------------------------------------------------------------------------------------------------------
rootDir = pa.Path(__file__).resolve().parent

# ----- for whatsapp session files ----- #
sessionDir = rootDir / "Wa_Session"
sessionDir.mkdir(exist_ok=True)
_initialized_profiles = set()

# ----- for files like doc , img , vid , audio ----- #
files = rootDir / "files"
files.mkdir(exist_ok = True)
# -----------------------------------------------------------------------------------------------------------------------

def designatedProfile(profile: str) -> pa.Path:
    """
    Creates base profile directory and base files (Logs.txt, Race.txt, trace.txt),
    along with savedLogin/ folder for persistence.
    Returns the profile directory path.
    """
    pwd = sessionDir / f"{profile}_Profile"
    pwd.mkdir(exist_ok=True)

    # Create file-based logs instead of directories
    for f_name in ["Logs.txt"]:
        file_path = pwd / f_name
        if not file_path.exists():
            file_path.touch()

    # savedLogin remains a directory (used by persistence logic)
    (pwd / "savedLogin").mkdir(exist_ok=True)
    (pwd / "trace").mkdir(exist_ok=True)

    _initialized_profiles.add(profile)
    return pwd


def ensureProfile(profile: str=SETTINGS.PROFILE) -> pa.Path:
    if profile not in _initialized_profiles:
        return designatedProfile(profile)
    return sessionDir / f"{profile}_Profile"


# ------------------------------------ File Path Getters ------------------------------------#

def getLogsFile(profile: str = SETTINGS.PROFILE) -> pa.Path:
    return ensureProfile(profile) / "Logs.txt"


def TraceStart(profile: str = SETTINGS.PROFILE) -> pa.Path:
    # This is a directory for temporary trace data
    path = ensureProfile(profile) / "trace"
    path.mkdir(exist_ok=True)
    return path

def TraceStop(profile: str = SETTINGS.PROFILE) -> pa.Path:
    # This is the final trace ZIP file path
    return ensureProfile(profile) / "trace" / f"trace_{profile}.zip"


def getRaceFile(profile: str = SETTINGS.PROFILE) -> pa.Path:
    return ensureProfile(profile) / "Race.txt"


def getSavedLoginDir(profile: str = SETTINGS.PROFILE) -> pa.Path:
    return ensureProfile(profile) / "savedLogin"


def get_saved_data_ids(profile: str = SETTINGS.PROFILE) -> pa.Path:
    return ensureProfile(profile) / "SEEN_IDS.pkl"


def get_ban_list(profile: str = SETTINGS.PROFILE) -> pa.Path:
    return ensureProfile(profile) / "BAN_LIST.pkl"


def get_admin_list(profile: str = SETTINGS.PROFILE) -> pa.Path:
    return ensureProfile(profile) / "Admin_List.pkl"


# ------------------------------------ Utility Write Helpers ------------------------------------#

def append_to_file(file_path: pa.Path, message: str):
    """
    Appends a line to the file (adds newline automatically).
    """
    with file_path.open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def write_to_file(file_path: pa.Path, content: str):
    """
    Overwrites the entire file with given content.
    usage : only when we need to rewrite the log file.
    """
    file_path.write_text(content, encoding="utf-8")
