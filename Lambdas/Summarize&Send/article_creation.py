import openai
import base64
from obtain_keys import load_api_keys


api_keys = load_api_keys()
print(api_keys)

openai.api_key = api_keys['OPEN_AI']



###### Article Creation ######
def create_title(article:str, preferences:str) -> str:
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k",
    messages=[
        {"role": "system", "content": f"Create a title for this article with the following preferences: {preferences}. Keep only the title in the response, which should be 1-3 words which should have aim to be informative."},
        {"role": "user", "content": article }
      ],
    temperature=0.82,
    max_tokens=5,
    top_p=.9,
    frequency_penalty=0,
    presence_penalty=0
     )
    return response['choices'][0]['message']['content']

def summarize(article:str, preferences:str) -> str:
    response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": f"You are a newsletter writer tailoring articles for your user with these preferences: {preferences}. Keep only the content summary and inlcude nothing else in the response."},
        {"role": "user", "content": article }
      ],
    temperature=0.82,
    max_tokens=300,
    top_p=.9,
    frequency_penalty=0,
    presence_penalty=0
     )
    return response['choices'][0]['message']['content']

def create_email_subject(content:list, preferences:str) -> str:
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k",
    messages=[
              {"role": "system", "content": f"Create a sujbect line to catch the users attention and describe the list of articles with the following preferences: {preferences}. Keep only the email subject in your respoonse, which should be 1-3 words which should have aim for a high email open rate."},
              {"role": "user", "content": str(content)}
             ],
    temperature=0.82,
    max_tokens=5,
    top_p=.9,
    frequency_penalty=0,
    presence_penalty=0
     )
    return response['choices'][0]['message']['content']

def create_content(article:str, preferences:str) -> dict:
    content_dict = dict()
    content_dict['title'] = create_title(article, preferences)
    content_dict['body'] = summarize(article, preferences)
    return content_dict

###### Formatting ######
light_mode = '''
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: transparent;
            color: white;
            padding: 20px;
        }

        .container {
            max-width: 80%;
            margin: 0 auto;
            border: 2px solid white;
            padding: 20px;
            border-radius: 15px;
        }

        .header-box {
            background-color: white;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 10px;
            border: 2px solid #555;
        }

        .header {
            text-align: center;
        }

        .header img {
            display: block;
            width: 500px;
            margin: 0 auto 10px auto;
        }

        .header h1 {
            font-size: 24px;
            color: black;
            padding: 10px 20px;
            border-radius: 10px;
        }

        .article {
            background-color: white;
            color: black;
            padding: 20px 30px;
            margin-bottom: 30px;
            border-radius: 10px;
            border: 2px solid #555;
        }

        .author {
            display: flex;
            align-items: center;
        }

        .author:before {
            content: '✍️';
            margin-right: 10px;
        }

        h2 {
            font-size: 22px;
            border-bottom: 2px solid #555;
            padding-bottom: 10px;
            color: #0077b6;
        }

        .market {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: white;
            color: black;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            border: 2px solid #555;
        }

        .percentage.green {
            color: green;
            background-color: #dafac5;
            padding: 5px;
            border-radius: 5px;
        }

        .percentage.red {
            color: red;
            background-color: #f9d6d5;
            padding: 5px;
            border-radius: 5px;
        }

    </style>'''

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

logo_encoded = image_to_base64('ToastLogo-removebg-preview.png')

def format_passage(content_dict:list) -> str:
    html = f'''
    <h2>{content_dict['title']}</h2>
    <div class="article">
        <p>{content_dict['body']}</p>
        <!-- Omitting the author for now, add it if you have that data -->
    </div>
    '''
    return html

def create_email_html(content:list, preferences:str, style:str) -> dict:
    email = dict()
    email['subject'] = create_email_subject(content, preferences)
    
    passages = []
    for content_dict in content:
        passage = format_passage(content_dict)
        passages.append(passage)
    
    # Combine passages
    combined_passages = ''.join(passages)
    
    # Generate final email HTML
    email_html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        {light_mode}
    </head>
    <body>
        <div class="container">
            <div class="header-box">
                <div class="header">
                    <img src="https://toast-logos-newsletter.s3.amazonaws.com/ToastLogo-removebg-preview.png" alt="Logo">
                    <h1>Here's your Morning Toast</h1>
                </div>
            </div>
            {combined_passages}
        </div>
    </body>
    </html>
    '''
    
    email['body'] = email_html

    return email
