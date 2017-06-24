# -*- coding: UTF-8 -*-

import subprocess as sub
import sys
import os
os.system('kill -s $(pidof python save_log_redis.py)')
os.system('kill -s $(pidof python new_url_updator.py)')
os.system('kill -s $(pidof python guideprotect.py)')
os.system('git reset --hard HEAD')
os.system('git pull')
os.system('python guideprotect.py')

