# NOTE: The updating of this script will be weird. It updates the second time. When making changes ensure they are properly implemented before BATCH

import os

os.chdir("..")
os.system("git fetch")
os.system("git pull")


