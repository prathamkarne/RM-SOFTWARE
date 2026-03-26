class Config:
    SECRET_KEY = 'your_secret_key_here'  # Change this to a secure random value
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:@localhost/hotel_db1'  # Update with your PostgreSQL credentials and DB name
    SQLALCHEMY_TRACK_MODIFICATIONS = False