if [ ! -d ./guideprotect ]; then
    git clone https://github.com/bleakhouse/guideprotect
fi
apt-get install -y redis-server
yum install redis-server
systemctl enable mysql
systemctl start mysql
pip install netifaces
pip install scapy
pip install web.py
pip install redis
pip install psutil
mysql -u root -p123456 -e "grant all privileges on *.* to test@localhost identified by '123456';"
mysql -u root -p123456 -e "grant all privileges on *.* to test@127.0.0.1 identified by '123456';"
mysql -u root -e "flush privileges;"
cd guideprotect
git pull
python start_with_old_all_kill.py
