from user_events import UserStructure

u = UserStructure()

# Add topics
email = 'Zarin.carlos@gmail.com'
name = 'Carlos'
preferences = 'Summarize the articles in a morning brew like fashion as in business casual.'
topic_list = ["Business Compliance & Tech Compliance. Any change in regulations about tech", "Decentralized Blockchain Emerging tech or regulations", "New breakthroughs in Rocket Technology"] # List of topics

new_user, info = u.add_user(email, name, preferences)
user_name = new_user['user_id']

u.add_user_interests(name, user_name, topic_list)