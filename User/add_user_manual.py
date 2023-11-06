from user_events import UserStructure

u = UserStructure()

# Add topics
email = ''
name = ''
preferences = ''
topic_list = [] # List of topics

user_name, info = u.add_user(email, name, preferences)
u.add_user_interests(name, user_name, topic_list)