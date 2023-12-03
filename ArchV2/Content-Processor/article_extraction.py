import newspaper
import feedparser
from datetime import datetime


import queue
import threading
import logging

def process_feed(feed: dict):
    output_queue = queue.Queue()
    stop_thread = threading.Event()  # Flag to signal the thread to stop

    # Define the thread
    thread = threading.Thread(target=extract_feed, args=(feed, output_queue, stop_thread,))
    thread.daemon = True
    thread.start()
    logging.debug(f"Thread Started: {feed}")

    thread.join(timeout=50)
    if thread.is_alive():
        stop_thread.set()  # Signal the thread to stop
        logging.debug(f"Killing Thread: {feed}")
        thread.join()  # Ensure thread has stopped
    else:
        try:
            output = output_queue.get_nowait()
            logging.debug("Successful Thread!: %s", feed)
            print("Outpute Max Date " + output['max_date'])
            output["articles"]
            return output
        except:
            logging.debug("Queue is empty, no output generated.")

    return None

def extract_feed(rss:dict, output_queue, stop_thread):
    articles = []
    output = dict()

    feed_url = rss['u']
    last_date = rss['dt']
    issues = 0
    try: 
        issues = rss['issues']
    except:
        rss['issues'] = 0 # This is a new feed.
        issues = rss['issues']

    max_date = last_date

    try:
        feed = feedparser.parse(feed_url)

        for entry in feed['entries']:
            pub_date =  int(datetime.strptime(entry['published'], "%a, %d %b %Y %H:%M:%S %z").timestamp())
            if pub_date > last_date:
                logging.info("Passed Published date check")
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
                output['feed'] = rss
                
    
    except:
        logging.debug("Feed Failed %s", feed_url)
        output['articles'] = articles
        output['max_date'] = max_date
        rss['issues'] += 1
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