from app import app
from waitress import serve
from paste.translogger import TransLogger
import logging.config
import logging
from datetime import datetime


# LOG_FILENAME = 'app/temp_files/requests.log'
# logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
# logging.info("\n")
# logging.info("*** The application started: " + str(datetime.now()))


if __name__ == "__main__":
    app.run(port=5003, debug=True)
    #serve(TransLogger(app, logger_name='lta', setup_console_handler=False), host='127.0.0.1', port=5003)
    #serve(TransLogger(app, logger_name='lta', setup_console_handler=False), host='172.20.7.226', port=8081)



    # serve(app, host='127.0.0.1', port=5000)
    #serve(app, host='172.20.7.226', port=8080)
    #app.run('0.0.0.0', 8080)
    # app.run('0.0.0.0', 80)