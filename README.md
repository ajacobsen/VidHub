# THIS REPO IS UNMAINTAINED

# VidHub


## How to setup

Requirements:
* Python 3
* Pip
* Git
* MySQL Server (MariaDB is recommended)
* FFMPEG
* Redis-server
* Libmysqlclient (default-libmysql-dev on Debian)

Setting up: 

* Clone the repo using git

* Rename [config.sample.py](https://github.com/ajacobsen/VidHub/blob/master/vidhub/config.sample.py) to config.py and replace the default configurations to yours
  * [Docs](https://docs.djangoproject.com/en/3.0/topics/settings/)

* Install python dependanices (`pip install -r requirements.txt`)

* Run `./manage.py migrate`
