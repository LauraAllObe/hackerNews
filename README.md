##  this is the README.md file for the hackerNews project
    The flask application was configured using nginx and gunicorn and uses an SQLite database. The hackerNews 
    application aims at delivering the latest hackernews on an hourly basis. The home route "/" displays a paginated 
    view in descending order (by time) of these news items, which can be liked and disliked by users that are logged 
    in. The login "/login", logout "/logout", and callback "/callback" routes are handled by auth0 to allow users 
    to create and access their accounts (linked to Google). The admin "/admin" route allows non-admin users and add 
    and delete admins. The profile "/account" route allows users to view their profile information. The newsfeed 
    "/newsfeed" route displays the latest news items in descending order (by time).
![](https://youtu.be/uVsRSZlpIrU)
Table of Contents:
==================
    1       file description
    2-8     project description & features
    19-61   file structure
    63-275  installation and configuration
    277-288 testing (pylint and pytest/coverage)
    290-297 closing notes

File Structure:
===============
    hackerNews/
    │
    ├── __pycache__/
    │ └── ...
    ├── hackernews/
    │ ├── __pycache__/
    │ │ └── ...
    │ ├── static/
    │ │ ├── cat.gif
    │ │ ├── clock.gif
    │ │ ├── logo.png
    │ │ ├── main.css
    │ │ ├── red_thumbs_down.png
    │ │ ├── red_thumbs_up.png
    │ │ ├── thumbs_down.png
    │ │ └── thumbs_up.png
    │ ├── templates/
    │ │ ├── account.html
    │ │ ├── admin.html
    │ │ ├── home.html
    │ │ ├── layout.html
    │ │ ├── newsfeed.html
    │ │ └── ...
    │ ├── __init__.py
    │ ├── models.py
    │ ├── routes.py
    │ ├── test_models.py
    │ ├── test_routes.py
    │ └── ...
    ├── instance/
    │ └── ...
    ├── venv/
    │ ├── bin
    │ │ ├── activate
    │ │ └── ...
    │ └── ...
    ├── README.md
    ├── report.txt
    ├── run.py
    ├── unit_test_pipeline.sh
    └── ...

Installation and Configurations:
================================
    NOTE: for Mac or Windows, please use 
    the equivalent commands for your system
    Cloning the Repository:
    -----------------------
    make sure you are up to date:
    sudo apt update -y
    install git:
    ------------
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
    install the latest python3 version:
    -----------------------------------
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
        python3 -m venv venv
    activate the virtual environment:
    ---------------------------------
        source venv/bin/activate
    install project dependencies:
    -----------------------------
        pip install -r requirements.txt

        OR

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
    deactivate your virtual environment:
    ------------------------------------
        deactivate  
    allow ports for HTTPS/Nginx:
    ----------------------------
        sudo ufw allow 'Nginx HTTPS'
    create a server for the application:
    ------------------------------------
        sudo vim /etc/systemd/system/hackerNews.service
        add the following lines (remplace user_name with your user name):
            [Unit]
            Description=Gunicorn instance to serve hackerNews
            After=network.target

            [Service]
            User=user_name
            Group=www-data
            WorkingDirectory=/home/user_name/hackerNews
            Environment="PATH=/home/user_name/hackerNews/venv/bin"
            ExecStart=/home/user_name/hackerNews/venv/bin/gunicorn --workers 3 --bind unix:hackerNews.sock -m 007 wsgi:app

            [Install]
            WantedBy=multi-user.target
    start the service and test that it is running:
    ----------------------------------------------
        sudo systemctl start hackerNews
        sudo systemctl enable hackerNews
        sudo systemctl status hackerNews
    generate SSL certificate using certbot(replace domain_name with your 
    domain name and domain_prefix with your domain prefix, exclude https://):
    -------------------------------------------------------------------------
        sudo apt install python3-certbot-nginx
        sudo certbot --nginx -d domain_name -d domain_prefix.domain_name
    configure nginx:
    ----------------
        sudo vi /etc/nginx/sites-available/hackerNews
        add the following lines (replace domain_name with your domain name 
        and domain_prefix with your domain prefix, exclude https://):
        -------------------------------------------------------------
        NOTE: lines 198-202, 246-253 should be generated by certbot
            server {
                server_name domain_prefix.domain_name;
                
                listen 443 ssl; # managed by Certbot
                ssl_certificate /etc/letsencrypt/live/domain_prefix.domain_name/fullchain.pem; # managed by Certbot
                ssl_certificate_key /etc/letsencrypt/live/domain_prefix.domain_name/privkey.pem; # managed by Certbot
                include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
                ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

                add_header Strict-Transport-Security "max-age=31536000; includeSubdomains; preload" always;
                add_header X-Content-Type-Options nosniff;
                add_header X-Frame-Options "SAMEORIGIN";
                add_header X-XSS-Protection "1; mode=block";

                    location / {
                            include proxy_params;
                            proxy_pass http://unix:/home/lauraallobe/hackerNews/hackerNews.sock;
                    }

                    location /newsfeed {
                            include proxy_params;
                            proxy_pass http://unix:/home/lauraallobe/hackerNews/hackerNews.sock;
                    }

                    location /execute_fetch {
                            include proxy_params;
                            proxy_pass http://unix:/home/lauraallobe/hackerNews/hackerNews.sock;
                    }

                    location /account {
                            include proxy_params;
                            proxy_pass http://unix:/home/lauraallobe/hackerNews/hackerNews.sock;
                    }

                location /admin {
                    include proxy_params;
                            proxy_pass http://unix:/home/lauraallobe/hackerNews/hackerNews.sock;
                }

                location /admin/delete {
                    include proxy_params;
                            proxy_pass http://unix:/home/lauraallobe/hackerNews/hackerNews.sock;
                }

                location /admin/add {
                    include proxy_params;
                            proxy_pass http://unix:/home/lauraallobe/hackerNews/hackerNews.sock;
                }

            }
            server {
                if ($host = domain_prefix.domain_name) {
                    return 301 https://$host$request_uri;
                } # managed by Certbot


                listen 80;
                server_name domain_prefix.domain_name;
                return 404; # managed by Certbot


            }
    link the file and test for syntax errors:
    -----------------------------------------
        sudo ln -s /etc/nginx/sites-available/hackerNews /etc/nginx/sites-enabled
        sudo nginx -t
        sudo systemctl restart nginx
    allow permissions for nginx(remplace user_name with your user name):
    --------------------------------------------------------------------
        sudo chmod 755 /home/user_name
    run your server(replace domain_name with your domain name):
    -----------------------------------------------------------
        https://domain_name

Testing:
========
    change to project directory:
    ----------------------------
        cd hackerNews
    run pylint:
    -----------
        pylint run.py hackernews/models.py hackernews/routes.py hackernews/__init__.py hackernews/test_models.py hackernews/test_routes.py
    run pytest using coverage:
    --------------------------
        coverage run --source=. -m pytest test_models.py test_routes.py
        coverage report

Closing Notes:
==============
    after changing nginx, run the following:
    ---------------------------------------
        sudo systemctl restart nginx
    after changing the hackerNews application, run the following:
    ------------------------------------------------------------
        sudo systemctl restart hackerNews