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
* Pipenv

* Clone the repo using git

* Modify [https://github.com/ajacobsen/VidHub/blob/master/vidhub/config.sample.py config.sample.py] and replace the default configurations to yours
  * [https://docs.djangoproject.com/en/3.0/topics/settings/ Docs]

* Install python dependanices (`pip install -r requirements.txt`)

* Run `./manage.py migrate`
