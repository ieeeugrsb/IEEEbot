import json
import os

import ieeebot

from flask import Flask, request, abort, render_template, url_for
from storage import Storage

app = Flask(__name__, template_folder='static/templates', static_folder='static')
app.config['PROPAGATE_EXCEPTIONS'] = True

ieeebot.logger.debug(ieeebot.TOKEN)
ieeebot.logger.debug(ieeebot.DATABASE_FILE)

@app.route('/webhook/<token>', methods=['POST'])
def hello(token=None):
    if token == ieeebot.TOKEN:
        update = request.get_json(force=True)
        ieeebot.logger.debug(str(update))
        
        if update['update_id'] > ieeebot.last_update_id:
            ieeebot.last_update_id = update['update_id']
            ieeebot.process_update(update)
            
        return "", 200
    else:
        return "", 400

@app.route('/ranking', methods=['GET'])
def ranking(group_id=0):
    group = ieeebot.storage.ranking
    return render_template("ranking.html", group_id=group_id, group=group)

if __name__ == "__main__":
    app.run(debug = True) 

