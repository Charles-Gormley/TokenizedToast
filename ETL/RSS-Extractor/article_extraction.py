import newspaper
import feedparser
import queue
import threading

import logging

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
    published_date = article.publish_date

    # return the title and text as a tuple
    return title, text, published_date

def process_feed(feed):
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

def extract_feed(feed_url, output_queue ):
    links = []
    output = dict()
    
    try:
        feed = feedparser.parse(feed_url)
        print(feed_url)
        print(len(feed.entries))
    
        for entry in feed.entries:
            nested_link = dict()
            nested_link['link'] = entry.link
            logging.debug("Feed retrieved link %s", feed_url)

            title, text, pub_date = extract_article(nested_link['link'])
            logging.debug("Feed retrieved article %s", feed_url)

            # Changing datetime format of pub_date
            nested_link['title'] = title
            nested_link['content'] = text
            nested_link['date'] = pub_date

            links.append(nested_link)
            output['articles'] = links
    
    except:
        logging.debug("Feed Failed %s", feed_url)
        output['articles'] = links
        

    output_queue.put(output)


