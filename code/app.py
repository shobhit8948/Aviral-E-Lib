from application import app
from application.routes import *



if __name__== '__main__':
    app.run(host= '0.0.0.0', port= 8000, debug= True)