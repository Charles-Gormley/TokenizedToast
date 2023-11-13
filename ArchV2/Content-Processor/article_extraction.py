import newspaper
import feedparser
from datetime import datetime


import queue
import threading
import logging

def process_feed(feed:dict):
    output_queue = queue.Queue()
    thread = threading.Thread(target=extract_feed, args=(feed, output_queue,))
    try:

        thread.daemon = True
        thread.start()
        logging.debug("Thread Started: %s", feed)
        thread.join(timeout=50)
        logging.debug('Thread Stopped: %s', feed)
        if thread.is_alive():
            thread.terminate()
            logging.debug("Killing Thread: %s", feed)
            thread.join()
        else:
            logging.debug("Successful Thread: %s", feed)
            output = output_queue.get()
    except:
        pass

    try: 
        output['articles']
        return output
    except:
        return None

def extract_feed(rss:dict, output_queue):
    articles = []
    output = dict()

    feed_url = rss['u']
    last_date = rss['dt']
    max_date = last_date

    try:
        feed = feedparser.parse(feed_url)

        for entry in feed['entries']:
            pub_date =  datetime.strptime(entry['published'], "%a, %d %b %Y %H:%M:%S %z")
            print("PubDate:", pub_date)
            if pub_date > last_date:
                print("Passed Pub date check")
                link = entry.link
                title, text = extract_article(link)
                logging.debug("Feed retrieved article %s", feed_url)

                # Changing datetime format of pub_date
                article = dict()
                article['link'] = link
                article['title'] = title
                article['content'] = text
                article['unixTime'] = pub_date

                if pub_date > max_date:
                    max_date = pub_date
                articles.append(article)

                output['articles'] = articles
                output['max_date'] = max_date
                output['feed'] = feed
                
    
    except:
        logging.debug("Feed Failed %s", feed_url)
        output['articles'] = articles
        output['max_date'] = max_date
        output['feed'] = rss

    output_queue.put(output)

def extract_article(url):
    """
    Extracts the title and text of an article from the given URL.
    
    Args:
        url (str): The URL of the article.

    Returns:
        A tuple containing the title and text of the article, respectively.
    """
    # create a newspaper Article object
    logging.debug("Starting Newspaper Article Extraction %s", url)

    config = newspaper.Config()
    config.request_timeout = 45
    article = newspaper.Article(url)
    logging.debug("Obtained Article %s", url)


    # download and parse the article
    article.download()
    logging.debug("Downloaded Article %s", url)

    article.parse()
    logging.debug("Parsed Article %s", url)

    # extract the title and text of the article
    title = article.title
    text = article.text
    
    logging.debug("Starting Newspaper Article Extraction %s", url)

    config = newspaper.Config()
    config.request_timeout = 45
    article = newspaper.Article(url)
    logging.debug("Obtained Article %s", url)


    # download and parse the article
    article.download()
    logging.debug("Downloaded Article %s", url)

    article.parse()
    logging.debug("Parsed Article %s", url)

    # extract the title and text of the article
    title = article.title
    text = article.text

    # return the title and text as a tuple
    return title, text