# Teacher Tally by Loophole
## Roster
- PM: Lucas Lee
    - Database
    - File storage
    - Flask routing
- D1: Andrew Juang
    - Database
    - Droplet deployment
    - File storage
- D2: Ella Krechmer
    - HTML/CSS/SASS
    - Styling direction
    - Teacher profile
- D3: Christopher Liu
    - Auth/Login
    - Teacher directory
    - Droplet deployment
- D4: Eliza Knapp
    - HTML/CSS/SASS
    - Database
    - Auth/Login
    - Teacher Profile

## Description
We will be making a site with the primary function of allowing students to see important information about their teachers —- most importantly, emails, course syllabi, and free periods/office hours. There will be a student login (using Google) where students will be able to see all this information and a teacher login (also using Google) where teachers can update their information.

## API Stuff
Google OAuth 2.0
- API KB: https://github.com/stuy-softdev/notes-and-code/blob/main/api_kb/411_on_GoogleAuth.md 
- How to use in your projects: https://github.com/stuy-softdev/notes-and-code/blob/main/how-to/howto_use_OAuth2-w-googs.md

TLDR: Google OAuth allows the flask app to use "sign in with google" for a secure, authenticated login.

How we used it: To ensure that only members of the stuyvesant community have access to the teacher profiles/schdules, you have to login with a stuyvesant email, which is made possible by google oauth. Further, this way you don't need a separate email and password to use this site!

## Launch Codes
1. Clone repository
```
$ git clone https://github.com/Lucas-Lee11/P04.git
$ cd P04
```

2. Create a new virtual environment
```
$ python3 -m venv env_name
$ source env_name/bin/activate
```

3. Install project dependencies
```
(env_name) $ pip3 install -r requirements.txt
```

4. Run the app
```
(env_name) $ python3 loophole.py
```
Access the app by going to http://127.0.0.1:5000/

Alternatively, use our deployed droplet: http://teachertally.me

## Deployment on a Server
The following instructions are intended for deployment on a DigitalOcean droplet. They are current as of June 1, 2022.
1. Set up a DigitalOcean droplet with Ubuntu 20.04.3 and Apache2. Instructions [here](https://github.com/Clue88/softdev-workshop/tree/main/24_lamp).

2. Install and enable WSGI. When you deploy a new app, you won't need to install the system dependencies again.
```
$ sudo apt-get install libapache2-mod-wsgi-py3 python-dev
$ sudo a2enmod wsgi
```

3. Install the app. (Note: typically, we would recommend using a virtual environment. However, sudo pip3 seems to bypass virtual environments anyway--please submit a PR if you figure out how to fix that--so we're going to ignore that for now.)
```
$ cd /var/www
$ sudo git clone https://github.com/Lucas-Lee11/P04.git
$ sudo apt-get install python3-pip
$ cd P04
$ sudo pip3 install -r requirements.txt
```

4. Configure your virtual host. Note: you can use any text editor (nano, etc.) in place of vim. Replace DROPLET_IP_ADDRESS and USERNAME as appropriate.
```
$ sudo vim TeacherTally.conf
```
You should see the following template in the `.conf` file:
```
<VirtualHost *:80>
    ServerName DROPLET_IP_ADDRESS
    ServerAdmin USERNAME@DROPLET_IP_ADDRESS
    WSGIScriptAlias / /var/www/P04/TeacherTally.wsgi
    <Directory /var/www/P04/app/>
        Order allow,deny
	Allow from all
    </Directory>
    Alias /static /var/www/P04/app/static
    <Directory /var/www/P04/app/static/>
        Order allow,deny
	Allow from all
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
Note: In order to deploy multiple apps, you won't be able to deploy both at the top-level route. You can change the `WSGIScriptAlias` from `/` and `/static` to `P04` and `P04/static`.

Save and close the file. For vim users, type `:wq`.

5. Move the `.conf` file to the correct location.
```
$ sudo cp TeacherTally.conf /etc/apache2/sites-available/TeacherTally.conf
```

6. Enable the virtual host.
```
$ sudo a2ensite TeacherTally
```
To disable your site, use
```
$ sudo a2dissite TeacherTally
```

7. Change the permissions on your database file.
Run the following. This will likely cause an error--it is necessary to generate the database file.
```
$ python3 loophole.py
```
Next, change the owner of the database file to `www-data`.
```
$ sudo chown www-data:www-data loophole.db
$ sudo chmod 755 loophole.db
$ sudo mkdir tmp
$ sudo mv loophole.db tmp/loophole.db
$ sudo chown www-data:www-data tmp
$ sudo chmod 755 tmp
```

8. Apply the deployment patch.
```
$ sudo git apply deployment.patch
```

9. Add OAuth secret files (see 411 on GoogleAuth API and `app/keys/readme`).

10. Restart apache.
```
$ sudo service apache2 restart
```

9. Test your app by going to `http://DROPLET_IP_ADDRESS` in a web browser.
