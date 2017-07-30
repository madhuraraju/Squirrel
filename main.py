import newsapi
import time
import pprint
from newsapi.articles import *
from newsapi.sources import *
import requests
from bs4 import BeautifulSoup
import nltk
from urllib import urlopen


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

    #pp.pprint(all_relevant_articles['mashable'])
    print("Summary Count of Articles collected:")

    source_url_dict = {}
    for key, value in all_relevant_articles.items():
        print("Source: ", key, "has relevant articles", len(value))
        source_url_dict[key] = [x['url'] for x in value]
    return source_url_dict

def getContent(url):
    #page = requests.get(url)
    #soup = BeautifulSoup(page.content, 'html.parser')
    #headings = soup.find_all('title')

    html_content = urlopen(url).read()
    soup = BeautifulSoup(html_content, 'html')
    # body_content = "// only paragraph"
    # metadata_content = "// only metadata"
    all_content = nltk.clean_html(html_content)
    heading = soup.find_all("title") ## for optimization later
    return all_content

def bigrams(all_content):
    # Check finders here:
    ## http: // www.nltk.org / howto / collocations.html

    tokens = nltk.wordpunct_tokenize(all_content)
    bigram_list = nltk.bigrams(tokens)

    fdist = nltk.FreqDist(bigram_list)
    # fdist.items() contains the bigrams with frequency

def trigrams(all_content):
    #TODO use the inbuild nltk functions to filter and cross check only for top
    #frequently occurring bigrms / trigrams
    tokens = nltk.wordpunct_tokenize(all_content)
    trigram_list = nltk.trigrams(tokens)

    fdist = nltk.FreqDist(trigram_list)
    # fdist.items() contains the trigrams with frequency


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
    print(get_relevant_articles(Source_list))

