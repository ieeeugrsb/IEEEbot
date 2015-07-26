import json
import os

import ieeebot

from flask import Flask, request, abort
from storage import Storage

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

ieeebot.logger.debug(ieeebot.TOKEN)
ieeebot.logger.debug(ieeebot.DATABASE_FILE)

@app.route('/ieeetestbot', methods=['POST'])
def hello():
    #if not request.json:
    #    abort(400)
    #else:
    ieeebot.logger.info(str(request.get_json(force=True)))

    return "", 200

if __name__ == "__main__":
    app.run(debug = True) 

