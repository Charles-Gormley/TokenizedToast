import json
from random import randint
import os


class UserStructure:
    
    def __init__(self, s3_bucket_name="toast-users"):
        self.s3_bucket_name = s3_bucket_name
        self.local_path = 'home/ec2-user/TokenizedToast/User'

    def add_user(self, email, name, summarization_preferences):
        user_id = str(randint(10000, 99999))  # generate unique user_id using randint

        new_user = {
            "user_id": user_id,
            "name": name,
            "new": True,
            "s3": None
        }
        self.save_user_to_s3(new_user) # Save the users.json file to s3.

        user_info = {
            "Email": email,
            "Name": name,
            "Summarization preferences": summarization_preferences
        }
        self.save_user_info_json_to_s3(user_info, name, user_id) # Save users info to s3 key under the the user_id-name of the user.
        
        return new_user, user_info
    
    def load_users_from_s3(self) -> list:
        os.system(f'aws s3 cp s3://{self.s3_bucket_name}/users.json {self.local_path}/users.json')
        with open(f'{self.local_path}/users.json', 'r') as json_file:
            json_data = json.load(json_file)
        return json_data

    def add_user_interests(self, name, user, topic_list, **kwargs):

        interests = dict()
        interests['topics'] = topic_list
        for key, value in kwargs.items():
            interests[key] = value

        self.save_users_interests_to_s3(name, user, interests)
    
    def save_user_to_s3(self, new_user):
        json_data = self.load_users_from_s3()
        json_data.append(new_user)
        with open(f'{self.local_path}/users.json', 'w') as json_file:
            json.dump(json_data, json_file)

        os.system(f'aws s3 cp {self.local_path}/users.json s3://{self.s3_bucket_name}')

    def save_user_info_json_to_s3(self, user_info, name, user_id):
        file_name = f"{user_id}-{name}/user-info.json"
        with open(f'{self.local_path}/{file_name}', 'w') as f:
            json.dump(user_info, f)
        os.system(f'aws s3 cp {self.local_path}/{file_name} s3://{self.s3_bucket_name}/{file_name}')

    def save_users_interests_to_s3(self, name, user_id, intersts_dict):
        file_name = f"{user_id}-{name}/user-interests.json"
        with open(f'{self.local_path}/{file_name}', 'w') as json_file:
            json.dump(intersts_dict, json_file)
        os.system(f'aws s3 cp {self.local_path}/{file_name} s3://{self.s3_bucket_name}/{file_name}')

    
    def load_users_interests(self, name, user_id) -> dict:
        file_name = f"{user_id}-{name}/user-interests.json"
        os.system(f'aws s3 cp s3://{self.s3_bucket_name}/{file_name} {self.local_path}')
        with open(f'{self.local_path}/{file_name}', 'r') as json_file:
            json_data = json.load(json_file)
        return json_data

    def update_users_interests_to_s3(self, name:str, user_id:str, new_interests:dict):
        json_data = self.load_users_interests(name, user_id)
        file_name =  f"{user_id}-{name}/user-interests.json"
        
        for key, value in new_interests.items():
            json_data[key] = value
        
        with open(f'{self.local_path}/{file_name}', 'w') as json_file:
            json.dump(json_data, json_file)
        
        os.system(f'aws s3 cp {self.local_path}/{file_name} s3://{self.s3_bucket_name}/{file_name}')