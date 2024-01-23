from flask import Flask
from app.views import app
import config

app.config.from_object(config)

if __name__ == '__main__':
    app.run(debug=True)
