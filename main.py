import newsapi
import time
import pprint
from newsapi.articles import *
from newsapi.sources import *

article_handler = None
source_handler = None

pp = pprint.PrettyPrinter(indent=4)

def setup_newsapi():
    global article_handler
    global source_handler
    source_handler = Sources(API_KEY="f9f1206fc1e54d5ba63a09f34cc63af0")
    article_handler = Articles(API_KEY="f9f1206fc1e54d5ba63a09f34cc63af0")

    return (article_handler, source_handler)

def asking_date():
    current_date = time.strftime("%X")

def get_all_sources():
    english_sources = source_handler.get(language="en")
    return english_sources['sources']

def get_all_categories():
    return set([x['category'] for x in get_all_sources()])

def get_all_papers():
    return [(x['id'],x['name']) for x in get_all_sources()]

def get_relevant_articles(paper_id, datum = None):
    if datum is None:
        todays_date = asking_date()
    else:
        todays_date = datum

    all_relevant_articles = {}
    for each in paper_id:
        all_output = article_handler.get(source=each)
        all_relevant_articles[each] = all_output['articles']

    pp.pprint(all_relevant_articles['mashable'])

    print("Summary Count of Articles collected:")
    for key, value in all_relevant_articles.items():
        print("Source: ", key, "has relevant articles", len(value))

    # Iterate through the metadata and create another dictionary that has the source text, title, description
    # extracts tags from html source (meta),

if __name__ == '__main__':
    setup_newsapi()

    # considering only english articles
    all_possible_categories = get_all_categories()
    all_possible_countries = ["au", "us"] # more available but ignoring for now

    pp = pprint.PrettyPrinter(indent=4)

    # Journalist's preference
    Persons_of_interest = ["Paul Graham", "Elon Musk", "Bill Gates", "Mark Cuban"]
    Organizations = ["Microsoft", "Tiger Capital", "Y combinator", "Tesla"]
    Interests = ["technology", "business"]
    Source_list = ["techcrunch", "mashable", "the-wall-street-journal", "fortune", "engadget", "hacker-news", "the-new-york-times"]

    print(get_all_papers())
    get_relevant_articles(Source_list)

