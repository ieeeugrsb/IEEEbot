import json
import os

import ieeebot

from flask import Flask, request, abort
from storage import Storage

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

ieeebot.logger.debug(ieeebot.TOKEN)
ieeebot.logger.debug(ieeebot.DATABASE_FILE)

@app.route('/webhook/<token>', methods=['POST'])
def hello(token=None):
    if token == ieeebot.TOKEN:
        update = request.get_json(force=True)
        ieeebot.logger.info(str(update))
        
        if update['update_id'] > ieeebot.last_update_id:
            ieeebot.last_update_id = update['update_id']
            ieeebot.process_update(update)
            
        return "", 200
    else:
        return "", 400

if __name__ == "__main__":
    app.run(debug = True) 

