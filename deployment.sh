if [ ! -d ./guideprotect ]; then
    git clone https://github.com/bleakhouse/guideprotect
fi
apt-get install -y redis-server
systemctl enable mysql
systemctl start mysql
pip install netifaces
pip install scapy
pip install web.py
pip install redis
pip install psutil
mysql -u root -e "grant all privileges on *.* to test@localhost identified by '123456';"
mysql -u root -e "grant all privileges on *.* to test@127.0.0.1 identified by '123456';"
mysql -u root -e "flush privileges;"
cd guideprotect
git pull
python new_url_updator.py &
python guideprotect.py