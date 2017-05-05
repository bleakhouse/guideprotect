if [ ! -d ./guideprotect ]; then
    git clone https://github.com/bleakhouse/guideprotect
fi

pip install netifaces
pip install scapy
mysql -u root -e "grant all privileges on *.* to test@localhost identified by '123456';"
mysql -u root -e "grant all privileges on *.* to test@127.0.0.1 identified by '123456';"
mysql -u root -e "flush privileges;"
cd guideprotect
git pull
python guideprotect.py