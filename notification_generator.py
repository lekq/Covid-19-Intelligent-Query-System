import time
import datetime
import math

class NotificationGenerator:
    def __init__ (self):
        self.host_url = 'http://127.0.0.1:5000'
        self.url_table = {}
        self.url_table['specific_project'] = self.host_url + '/manage_projects/all_projects'

    
    def get_plural (self, number, noun):
        if (abs (number) <= 1):
            return noun
        return noun + 's'

    def parse_timestamp (self, target_timestamp):
        # target: reprent the target timestampe into a comparative expression of the current timestamp. For example: 1 min ago, 2 weeks ago
        minute_length = 60
        hour_length = minute_length * 60
        day_length = hour_length * 24
        week_length = day_length * 7
        year_length = day_length * 365

        current_timestamp = int (time.time())
        target_timestamp = int (target_timestamp)
        time_difference = current_timestamp - target_timestamp

        if (time_difference < minute_length):
            return 'Just Now'
        elif (time_difference < hour_length):
            num_min = int (time_difference / minute_length)
            return '{0} {1} ago'.format (num_min, self.get_plural (num_min, 'minute'))
        elif (time_difference < day_length):
            num_hour = int (time_difference / hour_length)
            return '{0} {1} ago'.format (num_hour, self.get_plural (num_hour, 'hour'))
        elif (time_difference < week_length):
            num_day = int (time_difference / day_length)
            return '{0} {1} ago'.format (num_day, self.get_plural (num_day, 'day'))
        elif (time_difference < year_length):
            num_week =  int (time_difference / week_length)
            return '{0} {1} ago'.format (num_week, self.get_plural (num_week, 'week'))
        else:
            num_year = int (time_difference / year_length)
            return '{0} {1} ago'.format (num_year, self.get_plural (num_year, 'year'))




        pass

    def generate_created_notification_for_creator (self, creator_id, project_info):
        return {
            'notification_message' : 'Project <b>{0}</b> had been created for you.'.format (project_info['project_name']),
            'receiver_id' : creator_id,
            'associated_url' : self.url_table['specific_project'] + '/' + str (project_info['project_id']),
            'sent_timestamp' : str (int (time.time()))
        }

    def generate_created_notification_for_participant (self, creator_id, participant_id,  project_info, role_desc):
        return {
            'notification_message': '<b>{0}</b> had invited you into project <b>{1}</b> as {2}.'.format (creator_id, project_info['project_name'], role_desc),
            'receiver_id' : participant_id,
            'associated_url' : self.url_table['specific_project'] + '/' + str (project_info['project_id']),
            'sent_timestamp' : str (int (time.time()))
        }

    def generate_edited_notification_for_creator (self, creator_id, old_project_info, new_project_info):
        notification_message = ''
        if (old_project_info['project_name'] == new_project_info['project_name']):
            notification_message = 'Project <b>{0}</b> had been updated.'.format (old_project_info['project_name'])
        else:
            notification_message = 'Project <b>{0}</b> had been renamed to <b>{1}</b>.'.format (old_project_info['project_name'], new_project_info['project_name'])
        
        return {
            'notification_message' : notification_message,
            'receiver_id' : creator_id,
            'associated_url' : self.url_table['specific_project'] + '/' + str (new_project_info['project_id']),
            'sent_timestamp' : str (int (time.time()))
        }
    
    def generate_edited_notification_for_participant (self, creator_id, participant_id, old_project_info, new_project_info, old_role_desc, new_role_desc):
        if (old_role_desc == None):
            # if before the project was edited and the participant was not invited yet, this notification message will look like this project is newly created
            return self.generate_created_notification_for_participant (creator_id, participant_id, new_project_info, new_role_desc)

        if (new_role_desc == None):
            # if the creator removed the participant project (which means new_role == None)
            return {
                'notification_message': '<b>{0}</b> had removed you from project <b>{1}</b>.'.format (creator_id, old_project_info['project_name']),
                'receiver_id' : participant_id,
                'associated_url' : '',
                'sent_timestamp' : str (int (time.time()))
            }

        
        notification_message = ''
        if (old_project_info['project_name'] != new_role_desc['project_name']):
            notification_message += '<b>{0}</b> had renamed Project <b>{1}</b> to <b>{2}</b>. '.format (creator_id, old_project_info['project_name'], new_project_info['project_name'])
        else:
            notification_message += '<b>{0}</b> had updated Project <b>{1}</b>. '.format (creator_id, old_project_info['project_name'])

        if (old_role_desc != new_role_desc):
            notification_message += 'Your role had been changed from <b>{0}</b> to <b>{1}</b>'.format (old_role_desc, new_role_desc)
        
        return {
            'notification_message': notification_message,
            'receiver_id' : participant_id,
            'associated_url' : self.url_table['specific_project'] + '/' + str (new_project_info['project_id']),
            'sent_timestamp' : str (int (time.time()))
        }


    
