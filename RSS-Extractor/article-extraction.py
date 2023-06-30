import newspaper
import feedparser

def extract_article(url):
    """
    Extracts the title and text of an article from the given URL.
    
    Args:
        url (str): The URL of the article.
        
    Returns:
        A tuple containing the title and text of the article, respectively.
    """
    # create a newspaper Article object
    article = newspaper.Article(url)

    # download and parse the article
    article.download()
    article.parse()

    # extract the title and text of the article
    title = article.title
    text = article.text
    published_date = article.publish_date

    # return the title and text as a tuple
    return title, text, published_date


def extract_feed(feed_url, output_queue):
    links = []
    output = dict()

    try:
        feed = feedparser.parse(feed_url)
    
        for entry in feed.entries:
            nested_link = dict()
            nested_link['link'] = entry.link
            title, text, pub_date = extract_article(nested_link['link'])

            # Changing datetime format of pub_date
            nested_link['title'] = title
            nested_link['content'] = text
            nested_link['date'] = pub_date

            links.append(nested_link)
            output['articles'] = links
    
    except:
        output['articles'] = links

    output_queue.put(output)


