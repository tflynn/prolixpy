import sys
import os
from os import path
import json
import tempfile

from flask import Flask, render_template, request, jsonify, Response

import prolix
import standard_logger
from pyxutils import paths as pxpaths

LOGGER = standard_logger.get_logger('prolix_server', level_str='ERROR', console=True)
TEMPLATES_DIR = path.normpath(path.join(pxpaths.get_package_path('prolix'),'server','templates'))

app = Flask("prolix_server", template_folder=TEMPLATES_DIR)


@app.route("/", methods=['GET'])
def display_form():
    # TODO Clear
    if request.method == 'GET':
        return render_template('main_form.html', clear_text="Enter some text here")
    else:
        return "Error in server"

@app.route("/obscure", methods=['POST'])
def obscure_data():
    if request.method == 'POST':
        clear_text = request.form['clearText']
        clear_text_file = tempfile.NamedTemporaryFile(delete=False)
        with open(clear_text_file.name,'w') as f:
            f.write(clear_text)
        papi = prolix.api(logger=LOGGER)
        results = papi.obscure(text=clear_text,expiration_secs=60)
        if results['success']:
            key = results['key']
            obscured_text = results['obscured_text']
            obscured_text_file = tempfile.NamedTemporaryFile(delete=False)
            with open(obscured_text_file.name, 'w') as f:
                f.write(obscured_text)
            return render_template('main_form.html',
                                   clear_text=clear_text,
                                   obscured_text=obscured_text,
                                   key=key,
                                   clear_text_file_name=clear_text_file.name,
                                   obscured_text_file_name=obscured_text_file.name
                                  )
        else:
            LOGGER.error("Server error API Error {0)".format(results['errors']))
            return "Error in server"
    else:
        return "Error in server"


@app.route("/clarify", methods=['POST'])
def clarify_data():
    if request.method == 'POST':
        try:
            original_clear_text_file_name = request.form['hiddenClearTextFileName']
            if path.exists(original_clear_text_file_name):
                with open(original_clear_text_file_name,'r') as f:
                    original_clear_text = f.read()
                os.remove(original_clear_text_file_name)
            else:
                msg = "original_clear_text_file_name {0} does not exist".format(original_clear_text_file_name)
                LOGGER.error(msg)
                return "Error in server " + msg

            key = request.form['hiddenObscureKey']

            obscured_text_file_name = request.form['hiddenObscureTextFileName']
            if path.exists(obscured_text_file_name):
                with open(obscured_text_file_name,'r') as f:
                    obscured_text = f.read()
                os.remove(obscured_text_file_name)
            else:
                msg = "obscured_text_file_name {0} does not exist".format(obscured_text_file_name)
                LOGGER.error(msg)
                return "Error in server " + msg

            papi = prolix.api(logger=LOGGER)
            results = papi.clarify(text=obscured_text,key=key)
            if results['success']:
                clarified_text = results['clarified_text']
                return render_template('main_form.html',
                                       clear_text=original_clear_text,
                                       obscured_text=obscured_text,
                                       key=key,
                                       clarified_text=clarified_text,
                                       clear_text_file_name=original_clear_text_file_name,
                                       obscured_text_file_name=obscured_text_file_name
                                      )
            else:
                LOGGER.error("Server error API Error {0)".format(results['errors']))
                return "Error in server. API error {0}".format(results['errors'])

        except Exception as e:
            LOGGER.error("Server error {0}".format(e))
            return "Error in server exception {0}".format(e)

    else:
        return "Unsupported method"


@app.route("/api/form", methods=['GET'])
def display_api_form():
    if request.method == 'GET':
        request.args = {}
        return render_template('index.html')
    else:
        msg = "/api only supports GET"
        LOGGER.error(msg)
        return msg


@app.route("/api/obscure", methods=['POST'])
def api_obscure_data():
    try:
        if request.method == 'POST':
            raw_data = request.get_data().decode("UTF8")
            obscure_request_json = json.loads(raw_data)
            clear_text = obscure_request_json['clearText'].strip()
            papi = prolix.api(logger=LOGGER)
            results = papi.obscure(text=clear_text,expiration_secs=600)
            if results['success']:
                key = results['key']
                obscured_text = results['obscured_text']
                out = {"key": key, "obscured_text": obscured_text}
            else:
                msg = "Server error API Error {0)".format(results['errors'])
                LOGGER.error(msg)
                out = {"error": msg}
        else:
            msg = "/api/obscure only supports POST"
            out = {"error": msg}

    except Exception as e:
        msg = "/api/obscure Server error {0}".format(e)
        LOGGER.error(msg)
        out = {"error": msg}

    return jsonify(out)


@app.route("/api/clarify", methods=['POST'])
def api_clarify_data():
    if request.method == 'POST':
        try:
            raw_data = request.get_data().decode("UTF8")
            clarify_request_json = json.loads(raw_data)
            key = clarify_request_json['key']
            obscured_text = clarify_request_json['obscured_text']
            papi = prolix.api(logger=LOGGER)
            results = papi.clarify(text=obscured_text,key=key)
            if results['success']:
                clarified_text = results['clarified_text']
                out = {"clarified_text": clarified_text}
            else:
                msg = "Server error API Error {0)".format(results['errors'])
                LOGGER.error(msg)
                out = {"error": msg}

        except Exception as e:
            msg = "Server error {0}".format(e)
            LOGGER.error(msg)
            out = {"error": msg}

    else:
        msg = "/api/clarify only supports POST"
        out = {"error": msg}

    return jsonify(out)
