import mysql.connector
import MySQLdb.cursors
import time
import datetime
import json
from .notification_generator import NotificationGenerator
class DatabaseQuery:
    def __init__ (self):
        self.database_name = 'sample_database'
        self.table_name = {}
        self.table_name['project_table'] = self.database_name + '.' + 'project_table'
        self.table_name['repo_table'] = self.database_name + '.' + 'repo_table'
        self.table_name['article_table'] = self.database_name + '.' + 'article_table'
        self.table_name['repo_to_article'] = self.database_name + '.' + 'repo_to_article'
        self.table_name['repo_interaction'] = self.database_name + '.' + 'repo_interaction'
        self.table_name['role_table'] = self.database_name + '.' + 'role_table'
        self.table_name['role_assignment'] = self.database_name + '.' + 'role_assignment'
        self.table_name['notification_table'] = self.database_name + '.' + 'notification_table'
        
    
    def get_connector (self):
        connector = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = '1234567'
        )
        return connector
    
    def execute_query (self, query, params = None):
        connector = self.get_connector ()
        cursor = connector.cursor (dictionary = True)
        if (params == None):
            cursor.execute (query)
        else:
            cursor.execute (query, params)
        return connector, cursor

    def execute_many_queries (self, query, params = None):
        connector = self.get_connector ()
        cursor = connector.cursor (dictionary = True)
        if (params == None):
            cursor.executemany (query)
        else:
            cursor.executemany (query, params)
        return connector, cursor

    def execute_modify_query (self, query, params = None):
        connector, cursor = self.execute_query (query, params)
        connector.commit()
        last_inserted_id = cursor.lastrowid # if there is any
        cursor.close ()
        return last_inserted_id

    def execute_many_modify_queries (self, query, list_params = None):
        connector, cursor = self.execute_many_queries (query, list_params)
        connector.commit()
        cursor.close ()


    def fetchone (self, query, params = None):
        connector, cursor =  self.execute_query (query, params)
        result = cursor.fetchone ()
        cursor.close()
        return result

    def fetchall (self, query, params = None):
        connector, cursor =  self.execute_query (query, params)
        result = cursor.fetchall ()
        cursor.close()
        return result

    def create_database (self):
        drop_db_query = "DROP DATABASE IF EXISTS {0}".format (self.database_name)
        self.execute_modify_query (drop_db_query)
        create_db_query = 'CREATE DATABASE {0}'.format (self.database_name)
        self.execute_modify_query (create_db_query)
        create_project_table_query = """CREATE TABLE {0} (
            project_id INT NOT NULL AUTO_INCREMENT,
            project_name CHAR (255) NOT NULL,
            project_desc CHAR (255),
            project_color CHAR (255) NOT NULL,
            account_id CHAR (255) NOT NULL,
            created_timestamp BIGINT NOT NULL,
            is_archived BOOLEAN NOT NULL,
            PRIMARY KEY (project_id),
            CONSTRAINT no_duplicated_name UNIQUE (project_name, account_id)
        )
        """.format (self.table_name['project_table'])

        create_repo_table_query = """CREATE TABLE {0} (
            repo_id INT NOT NULL AUTO_INCREMENT,
            repo_name CHAR (255) NOT NULL,
            repo_desc CHAR (255),
            account_id CHAR (255) NOT NULL,
            project_id INT NOT NULL,
            is_default BOOLEAN NOT NULL,
            created_timestamp BIGINT NOT NULL,
            PRIMARY KEY (repo_id),
            FOREIGN KEY (project_id) REFERENCES {1} (project_id),
            CONSTRAINT no_duplicated_repo_name UNIQUE (repo_name, project_id)
        )
        """.format (self.table_name['repo_table'], self.table_name['project_table'])

        create_article_table_query = """CREATE TABLE {0} (
            article_id INT NOT NULL AUTO_INCREMENT,
            article_title CHAR (255) NOT NULL,
            article_abstract TEXT,
            PRIMARY KEY (article_id)
        )
        """.format (self.table_name['article_table'])

        create_repo_to_article_table_query = """CREATE TABLE {0} (
            repo_id INT NOT NULL,
            article_id INT NOT NULL,
            FOREIGN KEY (repo_id) REFERENCES {1} (repo_id),
            FOREIGN KEY (article_id) REFERENCES {2} (article_id),
            CONSTRAINT no_duplicated_record UNIQUE (article_id, repo_id)
        )
        """.format (self.table_name['repo_to_article'], self.table_name['repo_table'], self.table_name['article_table'])
        
        create_repo_interaction_table_query = """ CREATE TABLE {0} (
            repo_id INT NOT NULL,
            interact_account_id CHAR (255) NOT NULL,
            interact_timestamp BIGINT NOT NULL
        )
        """.format (self.table_name['repo_interaction'])

        create_role_table_query = """ CREATE TABLE {0} (
            role_id INT NOT NULL AUTO_INCREMENT,
            role_description CHAR (255) NOT NULL,
            PRIMARY KEY (role_id)
        )
        """.format (self.table_name["role_table"])

        create_role_assignment_query = """ CREATE TABLE {0} (
            role_id INT NOT NULL,
            project_id INT NOT NULL,
            account_id CHAR (255) NOT NULL,
            FOREIGN KEY (role_id) REFERENCES {1} (role_id),
            FOREIGN KEY (project_id) REFERENCES {2} (project_id),
            CONSTRAINT no_duplicated_role UNIQUE (role_id, project_id, account_id)
        )
        """.format (self.table_name["role_assignment"], self.table_name["role_table"], self.table_name["project_table"])

        create_notification_table_query = """ CREATE TABLE {0} (
            notification_id INT NOT NULL AUTO_INCREMENT,
            notification_message TEXT,
            receiver_id CHAR (255) NOT NULL,
            associated_url CHAR (255),
            sent_timestamp INT NOT NULL,
            is_read BOOLEAN NOT NULL,
            PRIMARY KEY (notification_id)
        )
        """.format (self.table_name['notification_table'])


        self.execute_modify_query (create_project_table_query)
        self.execute_modify_query (create_repo_table_query)
        self.execute_modify_query (create_article_table_query)
        self.execute_modify_query (create_repo_to_article_table_query)
        self.execute_modify_query (create_repo_interaction_table_query)
        self.execute_modify_query (create_role_table_query)
        self.execute_modify_query (create_role_assignment_query)
        self.execute_modify_query (create_notification_table_query)
        self.add_dummy_article ()
        self.add_role_definition ()
    

    # dummy section
    def add_dummy_article (self):
        query = "INSERT INTO {0} (article_title, article_abstract) VALUES (%s, %s)".format (self.table_name["article_table"])
        list_fake_article = []
        list_fake_article.append ( ("Covid-19 Situation in Korea", "Dr.Kim discussing about the situation with New York Times"))
        list_fake_article.append ( ("Vaccine factories in Japan", "Pfizer's decision to put factory in Japan"))
        list_fake_article.append ( ("The change in vaccine market", "Sputnik, Sinopharm, Pfizer, Moderna"))
        self.execute_many_modify_queries (query, list_fake_article)

    def add_role_definition (self):
        query = "INSERT INTO {0} (role_description) VALUES (%s)".format (self.table_name["role_table"])
        list_role = []
        list_role.append (("admin", ))
        list_role.append (("contributor", ))
        self.execute_mnay_modify_queries (query, list_role)
    
    def get_all_article (self):
        query = "SELECT * FROM {0}".format (self.table_name['article_table'])
        return self.fetchall (query, None)
    

    # check section
    def valid_new_project (self, project_name, project_desc, account_id):
        query = "SELECT * FROM {0} WHERE account_id = %s AND project_name = %s".format (self.table_name['project_table'])
        params = (account_id, project_name)
        return len (self.fetchall (query, params)) == 0

    def valid_new_repository (self, project_id, repo_name):
        query = "SELECT * FROM {0} WHERE project_id = %s AND repo_name = %s".format (self.table_name['repo_table'])
        params = (project_id, repo_name)
        return len (self.fetchall (query, params)) == 0

    # add section
    def add_project (self, project_name, project_desc, project_color, account_id, role_assignment):
        
        query = "INSERT INTO {0} (project_name, project_desc, project_color, account_id, created_timestamp, is_archived) VALUES (%s, %s, %s, %s, %s, %s)".format (self.table_name['project_table'])
        created_timestamp = int (time.time())
        params = (project_name, project_desc, project_color, account_id, created_timestamp, 0)
        new_project_id = self.execute_modify_query (query, params) # add a new project
        self.add_repository (account_id, "Default repository", "A starting place for you to add articles", new_project_id, True)

        list_account_id = []
        list_assigned_role = []
        for assignment in role_assignment:
            list_account_id.append (assignment['username'])
            list_assigned_role.append (assignment['role'])
        
        self.add_role_to_project (new_project_id, list_assigned_role, list_account_id)

        # send the notification to everybody involved
        noti_generator = NotificationGenerator ()
        list_notification = []
        project_info = {
            'project_name' : project_name,
            'project_id' : new_project_id
        }
        list_notification.append (noti_generator.generate_created_notification_for_creator(account_id, project_info))
        for assignment in role_assignment:
            participant_id = assignment['username']
            role = assignment['role']
            list_notification.append (noti_generator.generate_created_notification_for_participant (account_id, participant_id, project_info, role))
            
        self.add_notification (list_notification)

        
        
        
    def add_repository (self, account_id, repo_name, repo_desc, project_id, is_default):
        if (is_default):
            is_default_value = 1
        else:
            is_default_value = 0
        created_timestamp = int (time.time())
        query = "INSERT INTO {0} (repo_name, repo_desc, account_id, project_id, is_default, created_timestamp) VALUES (%s, %s, %s, %s, %s, %s)".format (self.table_name['repo_table'])
        params = (repo_name, repo_desc, account_id, project_id, is_default_value, created_timestamp)
        new_repo_id =  self.execute_modify_query (query, params)
        self.add_repo_interaction (account_id, new_repo_id)

    def add_repo_interaction (self, account_id, repo_id):
        interact_timestamp = int (time.time() )
        query = "INSERT INTO {0} (interact_account_id, repo_id, interact_timestamp) VALUES (%s, %s, %s)".format (self.table_name['repo_interaction'])
        params = (account_id, repo_id, interact_timestamp)
        self.execute_modify_query (query, params)

    def add_article (self, repo_id, article_id):
        query =  "INSERT INTO {0} (repo_id, article_id) VALUES (%s, %s)".format (self.table_name['repo_to_article'])
        params = (int (repo_id), int (article_id))
        self.execute_modify_query (query, params)

    def add_role_to_project (self, project_id, list_role_desc, list_account_id):
        role_list = self.get_all_roles ()
        list_insert_row = []
        for index in range (len (list_role_desc)):
            # transfrom role desc into role id. If we see an invalid role, discard the whole operation
            role_desc = list_role_desc[index]
            account_id = list_account_id[index]
            if (role_desc in role_list):
                role_id = role_list[role_desc]
                insert_row = (project_id, role_id, account_id)
                list_insert_row.append (insert_row)
            else:
                return

    
        query = "INSERT INTO {0} (project_id, role_id, account_id) VALUES (%s, %s, %s)".format (self.table_name['role_assignment'])
        self.execute_many_modify_queries (query, list_insert_row )


    def add_notification (self, list_added_notification):
        query = "INSERT INTO {0} (notification_message, receiver_id, associated_url, is_read, sent_timestamp) VALUES (%s, %s, %s, %s, %s)".format (self.table_name['notification_table'])
        list_added_tuple = []
        for added_notification in list_added_notification:
            notification_message = added_notification['notification_message']
            receiver_id = added_notification['receiver_id']
            associated_url = added_notification['associated_url']
            is_read = 0 # newly added notification is always set 'unread'
            sent_timestamp = str (added_notification['sent_timestamp'])
            added_tuple = (notification_message, receiver_id, associated_url, is_read, sent_timestamp)
            list_added_tuple.append (added_tuple)

        self.execute_many_modify_queries (query, list_added_tuple) 
        

    # edit section
    def update_archive_status (self, project_id, new_status):
        query = "UPDATE {0} SET is_archived = %s WHERE project_id = %s".format (self.table_name['project_table'])
        params = (new_status, project_id)
        self.execute_modify_query (query, params)
    
    def edit_project (self, project_id, new_project_name, new_project_desc, new_project_color, new_role_assignment):
        query = "UPDATE {0} SET project_name = %s, project_desc = %s, project_color = %s WHERE project_id = %s".format (self.table_name['project_table'])
        params = (new_project_name, new_project_desc, new_project_color, project_id)
        self.execute_modify_query (query, params)

        # delete all old role assignments
        query = "DELETE FROM {0} WHERE project_id = %s".format (self.table_name['role_assignment'])
        params = (project_id, )
        self.execute_modify_query (query, params)

        # insert new role assignment
        list_account_id = []
        list_assigned_role = []
        for assignment in new_role_assignment:
            list_account_id.append (assignment['username'])
            list_assigned_role.append (assignment['role'])
        
        self.add_role_to_project (project_id, list_assigned_role, list_account_id)

    def edit_repository (self, account_id, project_id, repo_id, new_repo_name):
        query = "UPDATE {0} SET repo_name = %s WHERE project_id = %s AND repo_id = %s".format (self.table_name["repo_table"])
        params = (new_repo_name, project_id, repo_id)
        self.execute_modify_query (query, params)

    def set_notification_status (self, account_id, notification_id, new_status):
        query = "UPDATE {0} SET is_read = %s WHERE notification_id = %s AND receiver_id = %s".format (self.table_name ['notification_table'])
        params = (new_status, notification_id, account_id)
        self.execute_modify_query (query, params)

        
    

    # remove section
    def remove_project (self, project_id):
        # TARGET: remove the project_id

        # clean all articles inside all repositories
        repository_list_id = []
        for repo_id in self.get_repository_list (project_id):
            repository_list_id.append (repo_id)


        
        if (len (repository_list_id) > 0):
            tuple_string = "("
            for index in range (len (repository_list_id)):
                if (index == len (repository_list_id) - 1):
                    tuple_string += str (repository_list_id[index])
                else:
                    tuple_string += (str (repository_list_id[index]) + ', ')
            tuple_string += ')'
            query = "DELETE FROM {0} WHERE repo_id IN {1}".format (self.table_name['repo_to_article'], tuple_string)
            self.execute_modify_query (query, None)
        

        # clean all repositories of that project
        query =  "DELETE FROM {0} WHERE project_id = %s ".format (self.table_name['repo_table'])
        params =  (project_id, )
        self.execute_modify_query (query, params)

        # clean all roles in the project
        query = "DELETE FROM {0} WHERE project_id = %s".format (self.table_name['role_assignment'])
        params = (project_id, )
        self.execute_modify_query (query, params)

        # delete the actual project
        query =  "DELETE FROM {0} WHERE project_id = %s ".format (self.table_name['project_table'])
        params = (project_id, )
        self.execute_modify_query (query, params)
    
    def leave_project (self, account_id, project_id):
        query = "DELETE FROM {0} WHERE account_id = %s AND project_id = %s".format (self.table_name['role_assignment'])
        params = (account_id, project_id)
        self.execute_modify_query (query, params)


    def remove_repository (self, project_id, repo_id):
        # TARGET: remove the repository with repo_id

        # delete the repositories
        query = "DELETE FROM {0} WHERE repo_id = %s".format (self.table_name['repo_to_article'])
        params = (repo_id, )
        self.execute_modify_query (query, params)
        query =  "DELETE FROM {0} WHERE repo_id = %s".format (self.table_name['repo_table'])
        params =  (repo_id, )
        self.execute_modify_query (query, params)

    def clear_all_repositories (self, project_id):
        #TARGET: remove all artilces from all repositories in project_id
        query = """DELETE FROM {0} 
        WHERE repo_id IN ( SELECT repo_id FROM {1} WHERE project_id = %s)
        """.format (self.table_name['repo_to_article'], self.table_name['repo_table'])
        params = (project_id, )

        self.execute_modify_query (query, params)


    def remove_article (self, repo_id, article_id):
        # TARGET: remove the article_id from repo_id

        query =  "DELETE FROM {0} WHERE repo_id = %s AND article_id = %s".format (self.table_name['repo_to_article'])
        params = (int (repo_id), int (article_id))
        self.execute_modify_query (query, params)

    
    def remove_notification (self, account_id, notification_id):
        # TARGET: remove the article_id from repo_id

        query =  "DELETE FROM {0} WHERE receiver_id = %s AND notification_id = %s".format (self.table_name['notification_table'])
        params = (account_id, int (notification_id))
        self.execute_modify_query (query, params)


    # get section
    def get_project_list (self, account_id):
        # TARGET: get the list of all projects of which the account_id are the creator, the admin, or the contributor
        created_project = {
            "active_project" : [],
            "archived_project" : []
        }
        admin_project = {
            "active_project" : [],
            "archived_project" : []
        }
        contributor_project = {
            "active_project" : [],
            "archived_project" : []
        }

        # get the project that user created
        query = """SELECT proj.*, 
        COUNT(repo.repo_id) AS repo_count FROM {0} AS proj
        LEFT JOIN {1} AS repo
        ON proj.project_id = repo.project_id
        WHERE proj.account_id = %s
        GROUP BY (proj.project_id)""".format (self.table_name['project_table'], self.table_name['repo_table'])

        params = (account_id, )
        result = self.fetchall (query, params)

        # format the result 
        for project in result:
            project['role_assignment'] = self.get_role_of_project (project['project_id'])
            if (project['is_archived']):
                created_project["archived_project"].append (project)
            else:
                created_project["active_project"].append (project)

        for project in created_project["active_project"]:
            project["role_description"] = 'creator'

        for project in created_project["archived_project"]:
            project["role_description"] = 'creator'

        # get the project that user administered or cotributed
        query = """SELECT proj.*, MIN(role.role_description) AS role_description,
        COUNT(repo.repo_id) AS repo_count 
        FROM {0} AS assignment
        LEFT JOIN {1} AS role ON assignment.role_id = role.role_id
        LEFT JOIN {2} AS proj ON assignment.project_id = proj.project_id
        LEFT JOIN {3} AS repo ON proj.project_id = repo.project_id
        WHERE assignment.account_id = %s
        GROUP BY (proj.project_id)
        """.format (self.table_name["role_assignment"], self.table_name["role_table"], self.table_name["project_table"], self.table_name["repo_table"])
        params = (account_id, )
        raw_result = self.fetchall (query, params)

        for project in raw_result:
            current_status = ""
            if (project["is_archived"]):
                current_status = "archived_project"
            else:
                current_status = "active_project"

            if (project["role_description"] == "admin"):
                admin_project[current_status].append (project)
            elif (project["role_description"] == "contributor"):
                contributor_project[current_status].append (project)
        final_result = {
            "created_project" : created_project,
            "admin_project" : admin_project,
            "contributor_project" : contributor_project
        }
        return final_result
        

    def get_project (self, project_id, account_id):
        # TARGET: get the info about the project id and the role of account_id in this project

        # find the project with that id and that creator
        query = "SELECT * FROM {0} WHERE project_id = %s AND account_id = %s".format (self.table_name['project_table'])
        params = (project_id, account_id)
        project_info = self.fetchone (query, params)
        if (project_info != None):
            project_info["role_description"] = "creator"
            project_info ["role_assignment"] = self.get_role_of_project (project_info['project_id'])
            return project_info

        # if the user did not create any project with that id, perhaps he wants to get info of the project he joined in 
        # (and that project should not be archived)
        query = """SELECT proj.*, role.role_description  FROM {0} AS assignment
        LEFT JOIN {1} AS role ON role.role_id = assignment.role_id
        LEFT JOIN {2} AS proj ON assignment.project_id = proj.project_id
        WHERE proj.project_id = %s 
        AND assignment.account_id = %s 
        AND proj.is_archived = 0
        """.format (self.table_name['role_assignment'], self.table_name['role_table'], self.table_name['project_table'])
        params = (project_id, account_id)

        return self.fetchone (query, params)

    def get_role_of_project (self, project_id):

        query = """ SELECT role.role_description, assignment.account_id
        FROM {0} AS assignment 
        LEFT JOIN {1} AS role ON role.role_id = assignment.role_id
        WHERE project_id = %s
        """.format (self.table_name['role_assignment'], self.table_name['role_table'])
        params = (project_id, )
        return self.fetchall (query, params)
        

    def get_repository_list (self, project_id):
        # TARGET: get the list of repositories of that project

        #query = "SELECT repo_id, repo_name, repo_desc FROM {0} WHERE project_id = %s".format (self.table_name['repo_table'])
        query = """SELECT repo.repo_id, repo.repo_name, repo.repo_desc, repo.is_default, repo.created_timestamp, repo.account_id,
        article.article_id, 
        article_details.article_title FROM {0} AS repo 
        LEFT JOIN {1} AS article ON repo.repo_id = article.repo_id 
        LEFT JOIN {2} AS article_details ON article.article_id = article_details.article_id
        WHERE project_id = %s""".format (self.table_name['repo_table'], self.table_name['repo_to_article'], self.table_name['article_table'])
        params = (project_id, )
        result =  self.fetchall (query, params)
        # format the result
        list_repository = {
        }
        for repo in result:
            repo_id = repo['repo_id']
            repo_name = repo['repo_name']
            repo_desc = repo['repo_desc']
            repo_creator = repo['account_id']
            created_timestamp = repo['created_timestamp']
            article = {
                'article_id' : repo['article_id'],
                'article_title' : repo['article_title']
            }
            is_default = repo['is_default']
            if (repo_id not in list_repository):
                list_repository[repo_id] = {
                    'repo_id' : repo_id,
                    'repo_name' : repo_name,
                    'repo_desc' : repo_desc,
                    'repo_creator' : repo_creator,
                    'is_default' : is_default,
                    'created_timestamp' : created_timestamp,
                    'list_articles': {}
                }
            if (article['article_id'] != None):
                list_repository[repo_id]['list_articles'][article['article_id']] = article

        return list_repository

    def get_most_recent_repository (self, account_id):
        # TARGET: get the most 3 recent non-empty repository interaction of account id 
        query = """SELECT interaction.repo_id, interaction.interact_timestamp,
        repo.repo_name,
        proj.project_id, proj.project_name,
        COUNT(repo_mapping.article_id) as article_count
        FROM  sample_database.repo_interaction as interaction
        LEFT JOIN sample_database.repo_to_article as repo_mapping on interaction.repo_id = repo_mapping.repo_id 
        LEFT JOIN sample_database.repo_table as repo on interaction.repo_id = repo.repo_id
        LEFT JOIN sample_database.project_table as proj on repo.project_id = proj.project_id
        WHERE interaction.interact_account_id = %s AND repo.repo_name IS NOT NULL
        GROUP BY (interaction.repo_id)
        ORDER BY interaction.interact_timestamp DESC
        LIMIT 3
        """
        params = (account_id, )
        
        return self.fetchall (query, params)

    def get_all_roles (self):
        # TARGET: get the full list of roles in role_table
        query = "SELECT * FROM {0}".format (self.table_name['role_table'])
        raw_result = self.fetchall (query, None)
        formatted_result = {}
        for role in raw_result:
            formatted_result[role['role_description']] = role['role_id']
        return formatted_result

    def get_full_project_and_repository_detail (self, account_id) :
        # TARGET: get all the projects and repositories created or participated by account_id (basically calling get_project_list () and call get_project () in the previous reuslt)
        # this is a costly operation and is only used for ProjectDetails.html when we want to save articles across project
        raw_project_list = self.get_project_list (account_id)
        formatted_project_list = []
        for project in raw_project_list['created_project']['active_project'] + raw_project_list['admin_project']['active_project'] + raw_project_list['contributor_project']['active_project']:
            add_project = {}
            add_project["project_id"] = project["project_id"]
            add_project["project_name"] = project["project_name"]
            add_project["account_id"] = project["account_id"]
            add_project["repository_list"] = self.get_repository_list (add_project["project_id"])
            formatted_project_list.append (add_project)
        return formatted_project_list

    
    def get_search_article (self, keyword_query, focus):
        data_str = open ('lekq_999998.json', 'r').read ()
        data_dict = json.loads (data_str)
        for article in data_dict["abstract"]:
            abstract_only = article["abstract"].split ("<span style = 'color: blue'>Key Sentences:</span><br>")[0]
            article['first_para'] = abstract_only[:400] + "..."
        return data_dict


    def get_all_notification (self, account_id):
        query = "SELECT * FROM {0} WHERE receiver_id = %s ORDER BY sent_timestamp DESC".format (self.table_name['notification_table'])
        params = (account_id, )
        list_notification =  self.fetchall (query, params)
        noti_generator = NotificationGenerator ()
        for notification in list_notification:
            notification['timestamp_expression'] = noti_generator.parse_timestamp (notification['sent_timestamp'])
        return list_notification


        
        



    

    


