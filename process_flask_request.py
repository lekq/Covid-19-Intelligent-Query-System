
import os
import time
import datetime
from .database_query import DatabaseQuery
sql_query = DatabaseQuery ()



def process_login_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "", 
            "target" : "" 
        },
        "params" : {
        }
    }
    if ('username' in input_dict and 'password' in input_dict):
        session['loggedin'] = True
        session['id'] = input_dict['username']
        session['username'] = input_dict['username']
        session['firstname'] = 'Khanh'
        session.pop ('project_info', None)
        return_action_guide["action"]["behavior"] = "redirect"
        return_action_guide["action"]["target"] = "select_project"
    else:
        return_action_guide["action"]["behavior"] = "render" 
        return_action_guide["action"]["target"] = "Login.html"
    return return_action_guide

def process_select_project_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "", 
            "target" : "" 
        },
        "params" : {
        }
    }
    if ('id' not in session):
        return_action_guide["action"]["behavior"] = "redirect"
        return_action_guide["action"]["target"] = "login"
        return return_action_guide

    project_list = sql_query.get_project_list (session['id'])
    return_action_guide["action"]["behavior"] = "render"
    return_action_guide["action"]["target"] = "AskForProject.html"
    return_action_guide["params"]["project_list"] =  project_list
    return_action_guide["params"]["account_id"] = session["id"]
    return_action_guide["params"]["list_notification"] = sql_query.get_all_notification (session["id"])
    print (return_action_guide["params"]["list_notification"])
    return return_action_guide

def process_manage_projects_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "", 
            "target" : "" 
        },
        "params" : {
        }
    }
    if ('id' not in session):
        return_action_guide["action"]["behavior"] = "redirect"
        return_action_guide["action"]["target"] = "login"
        return return_action_guide
    

    return_action_guide["action"]["behavior"] = "render"
    return_action_guide["action"]["target"] = "ManageProjects.html"
    project_list = sql_query.get_project_list(session['id'])
    most_recent_repository = sql_query.get_most_recent_repository (session['id'])
    return_action_guide["params"]["project_list"] = project_list
    return_action_guide["params"]["most_recent_repositories"] = most_recent_repository
    return_action_guide["params"]["account_id"] = session["id"]
    return_action_guide["params"]["list_notification"] = sql_query.get_all_notification (session["id"])
    return return_action_guide


def process_all_projects_request (session, input_dict = None):
    project_list = sql_query.get_project_list(session["id"])
    for project_category in project_list:
        for project_status in project_list[project_category]:
            for project in project_list[project_category][project_status]:
                project['created_timestamp'] = str (datetime.date.fromtimestamp (project['created_timestamp']))

    return_action_guide = {
        "action": {
            "behavior" : "render", 
            "target" : "AllProjects.html" 
        },
        "params" : {
            "project_list" : project_list
        }
    }
    return_action_guide["params"]["account_id"] = session["id"]
    return_action_guide["params"]["list_notification"] = sql_query.get_all_notification (session["id"])
    
    return return_action_guide

def process_project_details_request (session, input_dict = None):
    specific_project_info = sql_query.get_project (input_dict["project_id"], session["id"])
    specific_repository_list = sql_query.get_repository_list (input_dict["project_id"])
    all_project_info = sql_query.get_full_project_and_repository_detail (session["id"])

    for repo in specific_repository_list.values():
        repo['created_timestamp'] = str (datetime.date.fromtimestamp (repo['created_timestamp']))
        
    return_action_guide = {
        "action": {
            "behavior" : "render", 
            "target" : "ProjectDetails.html" 
        },
        "params" : {
            "project_info" : specific_project_info,
            "repository_list" : specific_repository_list,
            "all_project_info" : all_project_info
        }
    }

    return_action_guide["params"]["account_id"] = session["id"]
    return_action_guide["params"]["list_notification"] = sql_query.get_all_notification (session["id"])
    
    return return_action_guide

def process_home_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : {

        }
    }
    if ("id" not in session):
        return_action_guide["action"]["behavior"] = "redirect" 
        return_action_guide["action"]["target"] = "login"
        return return_action_guide
    elif ("project_info" not in session and "project_id" not in input_dict):
        return_action_guide["action"]["behavior"] = "redirect" 
        return_action_guide["action"]["target"] = "select_project"
        return return_action_guide
    else:
        if ("project_id" in input_dict):
            project_id = input_dict["project_id"]
        else:
            project_id = session["project_info"]["project_id"]

        project_info = sql_query.get_project (project_id, session["id"])

        if (project_info == None):
            return_action_guide["action"]["behavior"] = "redirect" 
            return_action_guide["action"]["target"] = "select_project"
        else:
            session["project_info"] = project_info
            return_action_guide["action"]["behavior"] = "render" 
            return_action_guide["action"]["target"] = "index.html"
            return_action_guide["params"]["project_info"] = project_info
        return_action_guide["params"]["account_id"] = session["id"]
        return_action_guide["params"]["list_notification"] = sql_query.get_all_notification (session["id"])
        return return_action_guide


        

def process_create_project_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : None
    }

    project_name = input_dict["project_name"]
    project_desc = input_dict["project_desc"]
    project_color = input_dict['project_color']
    account_id = session['id']
    role_assignment = input_dict['project_role_assignment']

    if (len (project_name.strip()) == 0):
        return_action_guide["action"]["behavior"] = "return"
        return_action_guide["action"]["target"] = {
            "error_msg" : "Cannot leave the project name empty"
        }
    elif (not sql_query.valid_new_project (project_name, project_desc, account_id)):
        return_action_guide["action"]["behavior"] = "return"
        return_action_guide["action"]["target"] = {
            "error_msg" : "Cannot have duplicated name for projects in your account"
        }
    else:
        print (project_name, project_desc, project_color)
        sql_query.add_project (project_name, project_desc, project_color, account_id, role_assignment)
        return_action_guide["action"]["behavior"] = "return"
        return_action_guide["action"]["target"] = {
            "success_msg" : "Successfully create your project"
        }

    return return_action_guide


def process_edit_project_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : None
    }
    new_project_name = input_dict["project_name"]
    new_project_desc = input_dict["project_desc"]
    project_id = input_dict["project_id"]
    new_project_color = input_dict['project_color']
    new_role_assignment = input_dict['project_role_assignment']
    account_id = session['id']

    if (len (new_project_name.strip()) == 0):
        return_action_guide["action"]["behavior"] = "return"
        return_action_guide["action"]["target"] = {
            "error_msg" : "Cannot leave the project name empty"
        }
    elif (sql_query.get_project (project_id, account_id) == None):
        return_action_guide["action"]["behavior"] = "return"
        return_action_guide["action"]["target"] = {
            "error_msg" : "Cannot edit project from someone else"
        }
    else:
        try:
            sql_query.edit_project (project_id, new_project_name, new_project_desc, new_project_color, new_role_assignment)
            return_action_guide["action"]["behavior"] = "return"
            return_action_guide["action"]["target"] = {
                "success_msg" : "Successdully edit your project"
            }
        except Exception as e:
            return_action_guide["action"]["behavior"] = "return"
            return_action_guide["action"]["target"] = {
                "error_msg" : "Either error in our database or you pick a duplicated name for your project"
            }
    
    return return_action_guide

def process_delete_project_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : {
        }
    }
    sql_query.remove_project (input_dict["project_id"])
    return_action_guide["action"]["behavior"] = "return"
    return_action_guide["action"]["target"] = {
        "success_msg" : "Successfully delete the project"
    }
    return return_action_guide

def process_leave_project_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : {
        }
    }
    sql_query.leave_project (session["id"], input_dict["project_id"])
    return_action_guide["action"]["behavior"] = "return"
    return_action_guide["action"]["target"] = {
        "success_msg" : "Successfully delete the project"
    }
    return return_action_guide


def process_archive_project_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : {
        }
    }
    project_id = input_dict['project_id']
    new_status = input_dict['new_archive_status']
    sql_query.update_archive_status (project_id, new_status)
    return_action_guide["action"]["behavior"] = "return"
    return_action_guide["action"]["target"] = "ok"
    return return_action_guide

def process_create_repository_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : {
        }
    }
    project_id = input_dict['project_id']
    repo_name = input_dict['repo_name']
    if (len (repo_name.strip()) == 0):
        return_action_guide["action"]["behavior"] = "return"
        return_action_guide["action"]["target"] = {
            "error_msg" : "Cannot leave the repository name empty"
        }
    elif (sql_query.get_project (project_id, session["id"]) == None):
        return_action_guide["action"]["behavior"] = "return"
        return_action_guide["action"]["target"] = {
            "error_msg" : "Cannot modify project of someone else"
        }
    elif (not sql_query.valid_new_repository (project_id, repo_name)):
        return_action_guide["action"]["behavior"] = "return"
        return_action_guide["action"]["target"] = {
            "error_msg" : "Cannot have duplicated name for repositories in one project"
        }
    else:
        sql_query.add_repository (session["id"], repo_name, "", project_id, False)
        return_action_guide["action"]["behavior"] = "return"
        return_action_guide["action"]["target"] = {
            "success_msg" : "Successfully create your repository"
        }
        
    return return_action_guide

def process_delete_repository_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : {
        }
    }
    project_id = input_dict["project_id"]
    repo_id = input_dict["repo_id"]
    sql_query.remove_repository (project_id, repo_id)
    return_action_guide["action"]["behavior"] = "return"
    return_action_guide["action"]["target"] = {
        "success_msg" : "Successfully delete your repository"
    }
    return return_action_guide

def process_edit_repository_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : {
        }
    }
    project_id = input_dict['project_id']
    new_repo_name = input_dict['repo_name']
    repo_id = input_dict['repo_id']
    try:
        sql_query.edit_repository (session["id"], project_id, repo_id, new_repo_name)
        return_action_guide["action"]["behavior"] = "return"
        return_action_guide["action"]["target"] = {
            "success_msg" : "Successdully edit your project"
        }
    except Exception as e:
        return_action_guide["action"]["behavior"] = "return"
        return_action_guide["action"]["target"] = {
            "error_msg" : "Either error in our database or you pick a duplicated name for your project"
        }
    
    return return_action_guide
    


def process_clear_all_repositories_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : {
        }
    }
    project_id = input_dict['project_id']
    sql_query.clear_all_repositories (project_id)

    return_action_guide["action"]["behavior"] = "return"
    return_action_guide["action"]["target"] = {
        "success_msg" : "Successfully clear all your repositories"
    }
    return return_action_guide

def  process_set_notification_status_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : {
        }
    }
    notification_id = input_dict ['notification_id']
    account_id = session['id']
    new_status = input_dict['new_status']
    sql_query.set_notification_status (account_id, notification_id, new_status)
    return_action_guide["action"]["behavior"] = "return"
    return_action_guide["action"]["target"] = {
        "success_msg" : "Successfully updated your notification status"
    }
    return return_action_guide

def  process_delete_notification_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : {
        }
    }
    notification_id = input_dict ['notification_id']
    account_id = session['id']
    sql_query.remove_notification (account_id, notification_id)
    return_action_guide["action"]["behavior"] = "return"
    return_action_guide["action"]["target"] = {
        "success_msg" : "Successfully deleted your notification status"
    }
    return return_action_guide
    
def process_logout_request (session, input_dict = None):
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('firstname', None)
    session.pop ('project_info', None)
    # Redirect to login page
    return_action_guide = {
        "action": {
            "behavior" : "redirect",
            "target" : "login" 
        },
        "params" : None
    }
    return return_action_guide


def process_search_request (session, input_dict = None):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : None
    }
    if ("id" not in session):
        return_action_guide["action"]["behavior"] = "redirect"
        return_action_guide["action"]["target"] = "login"
        return return_action_guide

    if ("project_info" not in session):
        return_action_guide["action"]["behavior"] = "redirect"
        return_action_guide["action"]["target"] = "select_project"
        return return_action_guide

    project_id = session["project_info"]["project_id"]
    project_info = sql_query.get_project (project_id, session["id"]) # prevent from using the information of a deleted project
    if (project_info == None):
        return_action_guide["action"]["behavior"] = "redirect"
        return_action_guide["action"]["target"] = "select_project"
        return return_action_guide

    return_action_guide["action"]["behavior"] = "render"
    return_action_guide["action"]["target"] = "new_Search.html"
    #article_list = sql_query.get_all_article ()
    search_content = input_dict['search_content']
    search_focus = input_dict['search_focus']
    article_list = sql_query.get_search_article (search_content, search_focus)
    for article in article_list['abstract']:
        article['publish_time'] = article['publish_time'].split ('T')[0]
        time_number = int (article['publish_time'].replace ('-', ''))
        article['publish_time_number'] = time_number #convert something like 2012-12-24 to 20121224

    repository_list = sql_query.get_repository_list (project_id)
    return_action_guide["params"] = {
        "project_info" : project_info,
        "article_list" : article_list,
        "repository_list": repository_list,
        "query_focus" : search_focus,
        "search_content" : search_content
    } 
    return_action_guide["params"]["account_id"] = session["id"]
    return return_action_guide


def process_save_article_request (session, input_dict):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : None
    }
    article_id = input_dict['article_id']
    repo_id = input_dict['repo_id']
    sql_query.add_article (repo_id, article_id)
    return_action_guide["action"]["behavior"] = "return"
    return_action_guide["action"]["target"] = {
        "success_msg" : "Successfully save your article"
    }
    return return_action_guide

def process_delete_article_request (session, input_dict):
    return_action_guide = {
        "action": {
            "behavior" : "",
            "target" : ""
        },
        "params" : None
    }
    article_id = input_dict['article_id']
    repo_id = input_dict['repo_id']
    sql_query.remove_article (repo_id, article_id)
    return_action_guide["action"]["behavior"] = "return"
    return_action_guide["action"]["target"] = {
        "success_msg" : "Successfully delete your article"
    }
    return return_action_guide



