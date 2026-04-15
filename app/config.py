import os

class Config:
    CS_JWT_PASS = os.getenv("CS_JWT_PASS", "jwtpass123")
    SQLALCHEMY_TRACK_MODIFICATIONS = False