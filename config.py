class Config:
    SECRET_KEY = "mysecretkey123"   # just a random string
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
