import newspaper
import feedparser
import queue
import threading
import logging
from dateutil import parser

from datetime import datetime

def process_feed(rss, curUnixTime):
    output_queue = queue.Queue()
    thread = threading.Thread(target=new_content, args=(rss, curUnixTime, output_queue, ))
    try:

        thread.daemon = True
        thread.start()
        logging.debug("Thread Started: %s", rss)
        thread.join(timeout=50)
        logging.debug('Thread Stopped: %s', rss)
        if thread.is_alive():
            thread.terminate()
            logging.debug("Killing Thread: %s", rss)
            thread.join()
        else:
            logging.debug("Successful Thread: %s", rss)
            output = output_queue.get()
    except:
        pass

    try:
        return output
    except:
        return None
    

def new_content(rss, curUnixTime, output_queue):
    try:
        feed = feedparser.parse(rss)
        lastPubUnixTime = int(parser.parse(feed['headers']['last-modified']).timestamp())
        if curUnixTime < lastPubUnixTime: # Last pub is older meaning new content exists since last check.
            output = True
        else:
            output = False

    except:
        output = None


    output_queue.put(output)