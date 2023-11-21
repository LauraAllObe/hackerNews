Cloning the Repository:
-----------------------
make sure you are up to date:
sudo apt update -y
install git (ubuntu):
---------------------
    sudo apt-add-repository ppa:git-core/ppa
    sudo apt-get update
    sudo apt-get install git
configure git:
--------------
    git config --global user.email "your_email_address@example.com"
    git config --global user.name "your_username"
clone the repository:
---------------------
    git clone https://gitlab.com/cop45216045641/hackerNews.git
change directories:
-------------------
    cd hackerNews
install the latest python3 version (ubuntu):
--------------------------------------------
    sudo apt install python3
install nginx and gunicorn dependencies:
----------------------------------------
    sudo apt install python3-pip 
    sudo apt install python3-dev 
    sudo apt install build-essential 
    sudo apt install libssl-dev 
    sudo apt install libffi-dev 
    sudo apt install python3-setuptools
make a virtual environment:
---------------------------
    sudo apt install python3-venv
    python3 -m venv myenv
activate the virtual environment(ubuntu):
-----------------------------------------
    source myenv/bin/activate
install project dependencies:
-----------------------------
    sudo apt install python3-pip
    pip install attrs==23.1.0
    pip install Authlib==1.2.1
    pip install blinker==1.6.3
    pip install certifi==2023.7.22
    pip install cffi==1.16.0
    pip install charset-normalizer==3.3.0
    pip install click==8.1.7
    pip install coverage==7.3.2
    pip install cryptography==41.0.4
    pip install dill==0.3.7
    pip install exceptiongroup==1.1.3
    pip install Flask==3.0.0
    pip install Flask-SQLAlchemy==3.1.1
    pip install greenlet==3.0.0
    pip install gunicorn==21.2.0
    pip install idna==3.4
    pip install importlib-metadata==6.8.0
    pip install iniconfig==2.0.0
    pip install isort==5.12.0
    pip install itsdangerous==2.1.2
    pip install jaraco.classes==3.3.0
    pip install jeepney==0.8.0
    pip install Jinja2==3.1.2
    pip install jsonschema==4.19.1
    pip install jsonschema-specifications==2023.7.1
    pip install keyring==24.2.0
    pip install MarkupSafe==2.1.3
    pip install mccabe==0.7.0
    pip install more-itertools==10.1.0
    pip install numpy==1.26.1
    pip install packaging==23.2
    pip install platformdirs==3.11.0
    pip install pluggy==1.3.0
    pip install pycparser==2.21
    pip install pylint==3.0.2
    pip install pytest==7.4.3
    pip install python-dotenv==1.0.0
    pip install pytz==2023.3.post1
    pip install referencing==0.30.2
    pip install requests==2.31.0
    pip install rpds-py==0.10.6
    pip install SecretStorage==3.3.3
    pip install SQLAlchemy==2.0.22
    pip install tomli==2.0.1
    pip install tomlkit==0.12.1
    pip install typing_extensions==4.8.0
    pip install urllib3==2.0.6
    pip install Werkzeug==3.0.0
    pip install zipp==3.17.0
install virtual environment gunicorn and nginx dependencies:
------------------------------------------------------------
    pip install wheel
    pip install gunicorn flask
allow respective ports:
-----------------------
    ports for HTTPS/nginx:
        sudo ufw allow 'Nginx Full'
create a server for the application:
------------------------------------
    sudo vim /etc/systemd/system/hackerNews.service
    add the following lines (remplace your_username with your user name):
        [Unit]
        Description=Gunicorn instance to serve hackerNews
        After=network.target

        [Service]
        User=your_username
        Group=www-data
        WorkingDirectory=/home/your_username/hackerNews
        Environment="PATH=/home/your_username/hackerNews/myenv/bin"
        ExecStart=/home/your_username/hackerNews/myenv/bin/gunicorn --workers 3 --bind unix:hackerNews.sock -m 007 wsgi:app

        [Install]
        WantedBy=multi-user.target
start the service and test that it is running:
----------------------------------------------
    sudo systemctl start hackerNews
    sudo systemctl enable hackerNews
    sudo systemctl status hackerNews
configure nginx:
----------------server {
	server_name www.aplacetostorehackernews.online;
	
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/www.aplacetostorehackernews.online/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/www.aplacetostorehackernews.online/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

    add_header Strict-Transport-Security "max-age=31536000; includeSubdomains; preload" always;
    #add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://code.jquery.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; img-src 'self' https://www.google.com";
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";

    	location / {
                include proxy_params;
                proxy_pass http://unix:/home/lauraallobe/hackerNews/hackernews.sock;
        }

        location /newsfeed {
                include proxy_params;
                proxy_pass http://unix:/home/lauraallobe/hackerNews/hackernews.sock;
        }

        location /execute_fetch {
                include proxy_params;
                proxy_pass http://unix:/home/lauraallobe/hackerNews/hackernews.sock;
        }

        location /account {
                include proxy_params;
                proxy_pass http://unix:/home/lauraallobe/hackerNews/hackernews.sock;
        }

	location /admin {
		include proxy_params;
                proxy_pass http://unix:/home/lauraallobe/hackerNews/hackernews.sock;
	}

	location /admin/delete {
		include proxy_params;
                proxy_pass http://unix:/home/lauraallobe/hackerNews/hackernews.sock;
	}

	location /admin/add {
		include proxy_params;
                proxy_pass http://unix:/home/lauraallobe/hackerNews/hackernews.sock;
	}

}
server {
    if ($host = www.aplacetostorehackernews.online) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


	listen 80;
	server_name www.aplacetostorehackernews.online;
    return 404; # managed by Certbot


}
[Unit]
Description=Gunicorn instance to serve hackernews
After=network.target

[Service]
User=lauraallobe
Group=www-data
WorkingDirectory=/home/lauraallobe/hackerNews
Environment="PATH=/home/lauraallobe/hackerNews/venv/bin"
ExecStart=/home/lauraallobe/hackerNews/venv/bin/gunicorn --workers 3 --bind unix:hackernews.sock -m 007 run:app

[Install]
WantedBy=multi-user.target
