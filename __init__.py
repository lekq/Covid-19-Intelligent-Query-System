from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify, abort
import os
import sys
import os.path
from os import path
from operator import getitem
import operator
from operator import itemgetter
from datetime import datetime
from werkzeug.wrappers import Response
import csv
from io import BytesIO as StringIO
from io import BytesIO
if sys.version_info.major < 3:
    reload(sys)
#sys.setdefaultencoding('utf8')
import json

app = Flask(__name__)
from .process_flask_request import *




#print (os.path('/var/www/flask/covid_iqs/static'))

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'iCDCU_202006'






def execute_action_guide (action_guide):
      behavior = action_guide["action"]["behavior"]
      target = action_guide["action"]["target"]
      params = action_guide["params"]
      if (behavior == "render"):
        return render_template (target, **params)
      elif (behavior == "redirect"):
        return redirect (url_for (target))
      elif (behavior == "send_file"):
        return send_file (target, **params)
      elif (behavior == "return"):
        return target
      return "Cannot understand the action guide"



@app.route ('/debug', methods = ['GET'])
def debug ():
    def dummy_func ():
        return "Hello Wolrd"
    return "Nothing here"


@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    input_dict = {}
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        input_dict['username'] = request.form['username']
        input_dict['password'] = request.form['password']
    
    action_guide = process_login_request (session, input_dict)
    return execute_action_guide (action_guide)


@app.route('/select_project', methods=['GET'])
def select_project ():
    action_guide = process_select_project_request (session, None)
    return execute_action_guide (action_guide)

@app.route('/create_project', methods=['POST'])
def create_project ():
    input_dict = {}
    input_dict["project_name"] = request.form["project_name"]
    input_dict["project_desc"] = request.form["project_desc"]
    input_dict["project_color"] = request.form["project_color"]
    input_dict["project_role_assignment"] = json.loads (request.form["json_project_role_assignment"])
    action_guide = process_create_project_request (session, input_dict)
    return execute_action_guide (action_guide)

@app.route('/edit_project', methods=['POST'])
def edit_project ():
    input_dict = {}
    input_dict["project_id"] = request.form["project_id"]
    input_dict["project_name"] = request.form["project_name"]
    input_dict["project_desc"] = request.form["project_desc"]
    input_dict["project_color"] = request.form["project_color"]
    input_dict["project_role_assignment"] = json.loads (request.form["json_project_role_assignment"])
    action_guide = process_edit_project_request (session, input_dict)
    return execute_action_guide (action_guide)



@app.route('/delete_project', methods=['POST'])
def delete_project ():
    input_dict = {}
    input_dict["project_id"] = request.form["project_id"]
    action_guide = process_delete_project_request (session, input_dict)
    return execute_action_guide (action_guide)

@app.route('/leave_project', methods=['POST'])
def leave_project ():
    input_dict = {}
    input_dict["project_id"] = request.form["project_id"]
    action_guide = process_leave_project_request (session, input_dict)
    return execute_action_guide (action_guide)

@app.route('/set_archive_status', methods=['POST'])
def archive_project ():
    print (request.form)
    input_dict = {}
    input_dict["new_archive_status"] = request.form["new_archive_status"]
    input_dict["project_id"] = request.form["project_id"]
    action_guide = process_archive_project_request (session, input_dict)
    return execute_action_guide (action_guide)

@app.route('/create_repository', methods=['POST'])
def create_repository ():
    input_dict = {}
    input_dict["project_id"] = request.form["project_id"]
    input_dict["repo_name"] = request.form["repo_name"]
    action_guide = process_create_repository_request (session, input_dict)
    return execute_action_guide (action_guide)

@app.route('/delete_repository', methods=['POST'])
def delete_repository ():
    input_dict = {}
    input_dict["project_id"] = request.form["project_id"]
    input_dict["repo_id"] = request.form["repo_id"]
    action_guide = process_delete_repository_request (session, input_dict)
    return execute_action_guide (action_guide)

@app.route('/edit_repository', methods=['POST'])
def edit_respotiroy ():
    input_dict = {}
    input_dict["project_id"] = request.form["project_id"]
    input_dict["repo_id"] = request.form["repo_id"]
    input_dict["repo_name"] = request.form["repo_name"]
    action_guide = process_edit_repository_request (session, input_dict)
    return execute_action_guide (action_guide)



@app.route ('/clear_all_repositories', methods=['POST'])
def clear_all_repositories ():
    input_dict = {}
    input_dict["project_id"] = request.form["project_id"]
    action_guide = process_clear_all_repositories_request (session, input_dict)
    return execute_action_guide (action_guide)

@app.route('/save_article', methods=['POST'])
def save_article ():
    input_dict = {}
    input_dict["article_id"] = request.form["article_id"]
    input_dict["repo_id"] = request.form["repo_id"]
    action_guide = process_save_article_request (session, input_dict)
    return execute_action_guide (action_guide)


@app.route('/delete_article', methods=['POST'])
def delete_article ():
    input_dict = {}
    input_dict["article_id"] = request.form["article_id"]
    input_dict["repo_id"] = request.form["repo_id"]
    action_guide = process_delete_article_request (session, input_dict)
    return execute_action_guide (action_guide)


@app.route('/manage_projects', methods=['GET'])
def manage_projects ():
    action_guide = process_manage_projects_request (session, None)
    return execute_action_guide (action_guide)

@app.route('/manage_projects/all_projects', methods=['GET'])
def all_projects ():
    action_guide = process_all_projects_request (session, None)
    return execute_action_guide (action_guide)

@app.route('/manage_projects/all_projects/<project_id>', methods=['GET'])
def project_details (project_id):
    input_dict=  {}
    input_dict['project_id'] = project_id
    action_guide = process_project_details_request (session, input_dict)
    return execute_action_guide (action_guide)


@app.route('/set_notification_status', methods = ['POST'])
def set_notification_stauts ():
    input_dict = {}
    input_dict['notification_id'] = request.form['notification_id']
    input_dict['new_status'] = request.form['new_status']
    action_guide = process_set_notification_status_request (session, input_dict)
    return execute_action_guide (action_guide)


@app.route('/delete_notification', methods = ['POST'])
def delete_notification ():
    input_dict = {}
    input_dict['notification_id'] = request.form['notification_id']
    action_guide = process_delete_notification_request (session, input_dict)
    return execute_action_guide (action_guide)

@app.route('/logout')
def logout():
    action_guide = process_logout_request (session, None)
    return execute_action_guide (action_guide)
                        
@app.route('/search', methods = ['GET','POST'])
def search():
    input_dict = {}
    if request.method == 'POST':
      input_dict["search_content"] = request.form["search_content"]
      input_dict["search_focus"] =request.form['optradio']
    else:
      input_dict["search_content"] = request.args.get('search_content')
      input_dict["search_focus"] = request.args.get('q_focus')
      input_dict["t_id"] = request.args.get('task_id')

    action_guide = process_search_request (session, input_dict)
    return execute_action_guide (action_guide)

@app.route('/home', methods = ['GET', 'POST'])
def home():
    print (request.form)
    input_dict = {}
    if ("project_id" in request.form):
        input_dict["project_id"] = request.form["project_id"]
    action_guide = process_home_request (session, input_dict)
    return execute_action_guide (action_guide)


@app.route('/QA_page/<QA_page_id>', methods = ['GET'])
def QA_page (QA_page_id):
    list_available_QA_page_id = ["start", "1", "2", "3", "4", "5", "6"]
    if (QA_page_id in list_available_QA_page_id):
        page_template = 'QA_page/QAPage-' + QA_page_id + '.html'
        return render_template (page_template)
    else:
        abort (404)


if __name__ == "__main__":
    app.run(debug=True)
