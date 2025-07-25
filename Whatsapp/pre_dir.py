"""
Here we have cleanly defined all the directories we have created with desc of why they exist.
"""
import pathlib as pa
import SETTINGS

#-----------------------------------------------------------------------------------------------------------------------
rootDir = pa.Path(__file__).resolve().parent
sessionDir = rootDir / "Wa_Session"
sessionDir.mkdir(exist_ok=True)
_initialized_profiles = set()
#-----------------------------------------------------------------------------------------------------------------------


def designatedProfile(profile: str) -> pa.Path:
    """
    Creates base profile directory and Logs, Race subfolders.
    Returns the profile directory path.
    """
    pwd = sessionDir / f"{profile}_Profile"
    pwd.mkdir(exist_ok=True)

    (pwd / "Logs").mkdir(exist_ok=True)
    (pwd / "Race").mkdir(exist_ok=True)
    (pwd / "trace").mkdir(exist_ok=True)
    (pwd / "savedLogin").mkdir(exist_ok=True)

    _initialized_profiles.add(profile)
    return pwd


def ensureProfile(profile: str) -> pa.Path:
    if profile not in _initialized_profiles:
        return designatedProfile(profile)
    return sessionDir / f"{profile}_Profile"


def getTraceDir(profile: str = SETTINGS.PROFILE) -> pa.Path:
    return ensureProfile(profile) / "trace"


def getLogsDir(profile: str = SETTINGS.PROFILE) -> pa.Path:
    return ensureProfile(profile) / "Logs"


def getRaceDir(profile: str = SETTINGS.PROFILE) -> pa.Path:
    return ensureProfile(profile) / "Race"


def getSavedLoginDir(profile: str = SETTINGS.PROFILE) -> pa.Path:
    return ensureProfile(profile) / "savedLogin"