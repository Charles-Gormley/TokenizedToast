# Class for obtaining API Key from Repository. (API Key should only be held locally)
# Has different prompt engineering techniques for different summarization styles.
#### Fun
#### Develop own Opinion on the topic
#### Just generate text
#### Send text to a set.
#### Have the set-newsletters be formatted as the preffered content type (Newsletter, Podcast, etc...)
#### Call the Delivery Package for specific formats (Emails) 


import os

class ContentGenerator:
    def __init__(self, summarization_style):
        self.api_key = self._get_api_key_from_repo()
        self.summarization_styles = summarization_style
        
        content_formats = ['newsletter', 'podcast']
        self.content_format = content_formats[0] # This stuff 

    def _get_api_key_from_repo(self):
        """
        Retrieve API Key from a local text file.
        The file is ignored by version control for security reasons.
        """
        try:
            with open('api_key.txt', 'r') as file:
                return file.readline().strip()  # Reads the key and removes any leading/trailing whitespace
        except FileNotFoundError:
            raise Exception("API Key file not found.")
        
    def base_summary(self, article, style):
        prompt = self._get_prompt(article, style, "base")
        response = openai.Completion.create(prompt=prompt, max_tokens=100)  # Adjust max_tokens as needed
        return response.choices[0].text.strip()

    def long_summary(self, article, style):
        prompt = self._get_prompt(article, style, "long")
        response = openai.Completion.create(prompt=prompt, max_tokens=200)  # Adjust max_tokens as needed
        return response.choices[0].text.strip()

    def _get_prompt(self, article, style, summary_length):
        # You can customize this method to return a prompt based on style and summary_length.
        # This is a basic implementation and you might want to refine it further based on your requirements.
        if style == 'fun':
            return f"Summarize this article in a fun way: {article}"
        elif style == 'opinion':
            return f"Write an opinionated summary of the article: {article}"
        elif style == 'plain':
            return f"Provide a {summary_length} summary of the article: {article}"



    def _fun_summary(self, topic):
        # Logic to generate fun summary
        pass

    def _opinion_summary(self, topic):
        # Logic to generate opinionated summary
        pass

    def _plain_summary(self, topic):
        # Logic to generate plain summary
        pass

    def _send_to_set_summary(self, topic):
        # Logic to generate set summary
        pass

    def format_content(self, content, content_format):
        if content_format == 'newsletter':
            return self._format_newsletter(content)
        elif content_format == 'podcast':
            return self._format_podcast(content)
        else:
            raise Exception("Invalid content format.")

    def _format_newsletter(self, content):
        # Logic to format content as a newsletter
        pass

    def _format_podcast(self, content):
        # Logic to format content as a podcast
        pass

    def deliver_content(self, formatted_content, delivery_method):
        if delivery_method == 'email':
            return self._deliver_email(formatted_content)
        # Add more delivery methods as needed
        else:
            raise Exception("Invalid delivery method.")

    def _deliver_email(self, formatted_content):
        # Logic to deliver content via email
        pass

# Usage:
generator = ContentGenerator()
summary = generator.generate_content('fun', 'some topic')
formatted_content = generator.format_content(summary, 'newsletter')
generator.deliver_content(formatted_content, 'email')
