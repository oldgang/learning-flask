# learning-flask
## Initializing the database
Open the python interpreter while inside the project directory an execute these commands:  
`from project import db, create_app, models`  
`create_app()`  
This will initialize the sqlite database and create a file called `db.sqlite` in the `instance` folder.
## Running the app
### Windows Powershell:
`$env:FLASK_APP="project"`  
`$env:FLASK_DEBUG=1` -> set this to `1` if you want to enable debug mode.  
`flask run`
