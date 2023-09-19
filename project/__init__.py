from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    # read secret key from file
    try:
        with open('instance/db-secret.txt', 'r') as f:
            app.config['SECRET_KEY'] = f.read().strip()
    except:
        print('Error: could not read the secret key from file.')
        exit()

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    # initialize the database instance with the app
    db.init_app(app)
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    
        # code to validate and add user to database goes here
    try:
        # read user credentials from file
        with open('instance/user-credentials.txt', 'r') as f:
            lines = f.readlines()
            name = lines[0].strip()
            password = lines[1].strip()
    except:
        print('Error: could not read user credentials from file.')
        exit()
        
    with app.app_context():
        user = User.query.filter_by(name=name).first() # if this returns a user, then the email already exists in database

    if not user: # if a user is found, we want to redirect back to signup page so user can try again
        # create a new user. Hash the password so the plaintext version isn't saved.
        new_user = User(name=name, password=generate_password_hash(password, method='sha256'))

        # add the new user to the database
        try:
            with app.app_context():
                db.session.add(new_user)
                db.session.commit()
            print(f'User {name} created successfully.')
        except:
            print('Error: could not add user to database.')
            exit()
    
    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app