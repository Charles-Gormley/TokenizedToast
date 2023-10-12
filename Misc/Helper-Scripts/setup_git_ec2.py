# NOTE: The updating of this script will be weird. It updates the second time. When making changes ensure they are properly implemented before BATCH

import os

os.chdir("/home/ec2-user/TokenizedToast/")
print(os.getcwd())
os.system('git reset --hard')
os.system("git fetch")
os.system("git pull")

