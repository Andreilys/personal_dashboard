# Personal Dashboard

This is a personal dashboard I built to aggregate and visualize all the different tracking services that track my life. The dashboard is updated in real time and can be found at https://qself-dashboard.herokuapp.com/

Right now it visualizes:
- Time spent online, along with productivtity and unproductivity (Rescuetime)
- Steps and location (Moves)
- Chess (lichess.com)
- Weight (Withings smart scale)
- Pomodoro time (Toggl.com)
- Todo's (Todoist)
- Time spent programming (Wakatime)
- Top artists and songs for the month (Spotify)

## Table of Contents

- [Installation and Setup](#installation)
- [Support](#support)
- [Contributing](#contributing)
- [Licensing](#licensing)


## Installation and Setup

First make sure you have python3 installed and are using it throughout, since some of the syntax doesn't port over to python2.

```sh
git clone https://github.com/Andreilys/personal_dashboard
```
Install [Postgres](https://www.postgresql.org/download/)
Using psql create and name your database "qself\_dashboard"
Enter your API credentials into personal\_info\_template.py and rename it to personal\_info.py. Run these commands next:
```sh
Run python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

Now run the application with python3 app.py, you'll now need to give permission to Spotify for the app to access your data (Which will save a .emailCache file) followed by withings (make sure you are just copy+pasting oauth\_verifier and not including oauth\_token) and Moves which should then create permanent pickle files in your personal\_dashboard folder.

You're done setting it up locally!

**Setting up on Heroku**\s\s
With the application working locally, you might be interested in hosting it on the cloud, I prefer heroku so i'll walk you through instructions on how to set up there. First things first, make sure you register an account on heroku and download their [Heroku Toolbelt](https://devcenter.heroku.com/articles/heroku-cli), afterwards login with heroku login.

Once logged in run these commands 
 ```sh
heroku create (your app name)
git remote add pro git@heroku.com:YOUR\_APP\_NAME.git
git add personal\_dashboard/personal\_info.py -f
git add migrations -f
git add nokia\_data.pkl -f
git add moves\_data.pkl -f
git commit -m "adding personal info and migrations folder" (may need to login to github for this)
git push pro master
heroku config:set APP\_SETTINGS=config.ProductionConfig
heroku addons:create heroku-postgresql:hobby-dev --app (YOUR\_APP\_NAME)
heroku run python manage.py db upgrade --app (YOUR\_APP\_NAME)
```

Thats it! The other thing you should consider doing is setting the timezone of your heroku app so that everything is in sync, you can do this with the following command (Substituting the timezone with your own)

```sh
heroku config:add TZ="America/Los\_Angeles"
```
## Support

Please [open an issue](https://github.com/Andreilys/personal_dashboard/issues/new) for support.


## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/andreilys/personal_dashboard/compare).

## Licensing

CanvasJS is a commercial product and commercial usage of CanvasJS requires you to purchase a license. Without a commercial license, you can use it for evaluation purposes only. Please refer to the following link for further details: https://canvasjs.com

Copyright (c) 2017, Andrei Lyskov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
