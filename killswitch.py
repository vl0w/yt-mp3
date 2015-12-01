import os.path

KILLSWITCH_DETECTED_MESSAGE = "Killswitch detected. Stopping execution."


def killswitch_detected(folder:str):
    full_killswitch_path = folder + "kill"
    if os.path.isfile(full_killswitch_path):
        return True
    else:
        return False
