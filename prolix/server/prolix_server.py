import sys
import os
from os import path

import tempfile

import standard_logger
LOGGER = standard_logger.get_logger('prolix_server', level_str='ERROR', console=True)

from pyxutils import paths as pxpaths
TEMPLATES_DIR = path.normpath(path.join(pxpaths.get_package_path('prolix'),'server','templates'))

from flask import Flask, render_template, request

app=Flask("prolix_server", template_folder=TEMPLATES_DIR)

import prolix


@app.route("/", methods=['GET'])
def display_form():
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
