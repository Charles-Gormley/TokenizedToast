from transformers import BertTokenizer, BertModel

# Define your custom cache directory
cache_dir = "/home/ec2-user/model_cache/"

# Download and cache the tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Save both the tokenizer and model to your specified directory
tokenizer.save_pretrained(cache_dir+"tokenizer/")
model.save_pretrained(cache_dir+"model/")