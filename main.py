import newsapi
import time, os
import pprint
from newsapi.articles import *
from newsapi.sources import *
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tag.stanford import StanfordNERTagger
from nltk.tokenize import word_tokenize


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

def get_NER_Tagger(content):
    NER_classifier = "/Users/aparnaghosh87/Downloads/stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz"
    os.environ['CLASSPATH'] = "/Users/aparnaghosh87/Downloads/stanford-ner-2014-06-16"
    st = StanfordNERTagger(NER_classifier, encoding='utf-8')
    tokenized_text = word_tokenize(content)
    classified_text = st.tag(tokenized_text)
    # output looks like this:
    # [('While', 'O'), ('in', 'O'), ('France', 'LOCATION'), (',', 'O'), ('Christine', 'PERSON'), ('Lagarde', 'PERSON'), ('discussed', 'O'), ('short-term', 'O'), ('stimulus', 'O'), ('efforts', 'O'), ('in', 'O'), ('a', 'O'), ('recent', 'O'),
    # ('interview', 'O'), ('with', 'O'), ('the', 'O'), ('Wall', 'O'), ('Street', 'O'), ('Journal', 'O'), ('.', 'O')]
    return classified_text

def getContent(url):
    # TODO improve this with more tags for metadata
    content = {}
    body_text = ""

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    if soup.title is not None:
        heading = soup.title.string
    else:
        heading = url.split("/")[-1].replace("-"," ")

    content["heading"] = heading

    for script in soup.find_all('script'):
        script.extract()

    paragraphs = soup.find_all('p')
    for paragraph in paragraphs:
        body_text = body_text + " " + (paragraph.get_text(strip=True))

    content["body_text"] = body_text

    return content


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

def main(poi, orgs, src, tags):
    # havent done NER on headings for both person and org
    src_url_list = get_relevant_articles(src)

    persons = [word_tokenize(x) for x in poi]
    organizations = [word_tokenize(x) for x in orgs]

    source_scores = {}
    for src in src_url_list:
        article_scores = {}
        print("Debug: Working on ", src)
        for each_url in src_url_list[src]:
            print("Debug: Working on url: ", each_url)
            score = 0
            all_content = getContent(each_url)
            article_content = all_content["body_text"]
            article_heading = all_content["heading"]

            # Rewrite this bit to only check the contents that are tagged with NP/PP etc.
            for each in persons:
                for term in each:
                    if term in article_content:
                        score = score + 1
                    if term in article_heading:
                        score = score + 3

            for each in persons:
                if (" ".join(each)) in article_content:
                    score = score + 2
                if (" ".join(each)) in article_heading:
                    score = score + 4

            NER_tagged = get_NER_Tagger(article_content)
            only_personalities = [x[0] for x in NER_tagged if x[1] == 'PERSON']
            for each in persons:
                if each[0] in only_personalities:
                    score = score + 3
                if each[1] in only_personalities:
                    score = score + 3

            score_for_only_personalities = score

            # Organizations
            only_organizations = [x[0] for x in NER_tagged if x[1] == 'O']

            for each in organizations:
                for term in each:
                    if term in article_content:
                        score = score + 3
                    if term in article_heading:
                        score = score + 3

            for each in organizations:
                if (" ".join(each)) in article_content:
                    score = score + 2
                if (" ".join(each)) in article_heading:
                    score = score + 4

            # as the output of NER for organization doesnt always make sense, lets only check for the whole org name!!!
            for each in organizations:
                if (" ".join(each)) in only_organizations:
                    score = score + 3

            score_for_only_organizations = score - score_for_only_personalities
            article_scores[each_url] = score
            print("Debug: score for article", "each_url", score)
        # after testing this, go back and TODO: count the number of occurrences!!
        source_scores[src] = article_scores
        source_scores[src] = sorted(source_scores[src].items(), key=lambda x: x[1], reverse=True)
    print(source_scores)
    return source_scores


if __name__ == '__main__':
    setup_newsapi()

    # considering only english articles
    all_possible_categories = get_all_categories()
    all_possible_countries = ["au", "us"] # more available but ignoring for now

    pp = pprint.PrettyPrinter(indent=4)

    # Journalist's preference: 1
    #Persons_of_interest = ["Paul Graham", "Elon Musk", "Bill Gates", "Mark Cuban"]
    #Organizations = ["Microsoft", "Tiger Capital", "Y combinator", "Tesla"]
    #Source_list = ["techcrunch", "mashable", "the-wall-street-journal", "fortune", "engadget", "hacker-news", "the-new-york-times"]

    # Journalist's preference: 2
    #Persons_of_interest = ["Paul Graham", "Elon Musk", "Warren Buffet", "Michael Bloomberg"]
    #Organizations = ["Google", "Amazon", "Uber", "Apple", "Facebook"]
    #Source_list = ["techcrunch", "mashable", "the-wall-street-journal", "financial-times", "engadget", "hacker-news",
    #               "recode", "bloomberg", "the-verge"]

    # Journalist's preference: 3
    Persons_of_interest = ["Donald Trump", "Vladimir Putin", "Emmanuel Macaron", "Pope Francis", "Narendra Modi"]
    Organizations = ["United Nations", "Supreme Court", "Republican Party", "Democratic Party", "Kennedy School"]
    Source_list = ["abc-news-au", "al-jazeera-english", "bbc-news", "associated-press", "cnn", "reuters",
                   "the-guardian-uk", "the-washington-post", "usa-today", "daily-mail"]

    Interests = ["technology", "business"]
    print(get_all_papers())
    print(get_relevant_articles(Source_list))
    main(Persons_of_interest, Organizations, Source_list, None)

#[('abc-news-au', 'ABC News (AU)'), ('al-jazeera-english', 'Al Jazeera English'),
# ('ars-technica', 'Ars Technica'), ('associated-press', 'Associated Press'),
# ('bbc-news', 'BBC News'), ('bbc-sport', 'BBC Sport'), ('bloomberg', 'Bloomberg'),
# ('breitbart-news', 'Breitbart News'), ('business-insider', 'Business Insider'),
# ('business-insider-uk', 'Business Insider (UK)'), ('buzzfeed', 'Buzzfeed'), (
# 'cnbc', 'CNBC'), ('cnn', 'CNN'), ('daily-mail', 'Daily Mail'), ('engadget', 'Engadget'), (
# 'entertainment-weekly', 'Entertainment Weekly'), ('espn', 'ESPN'), ('espn-cric-info', 'ESPN Cric Info'),
# ('financial-times', 'Financial Times'), ('football-italia', 'Football Italia'), ('fortune', 'Fortune'),
# ('four-four-two', 'FourFourTwo'), ('fox-sports', 'Fox Sports'), ('google-news', 'Google News'),
# ('hacker-news', 'Hacker News'), ('ign', 'IGN'), ('independent', 'Independent'), ('mashable', 'Mashable'),
# ('metro', 'Metro'), ('mirror', 'Mirror'), ('mtv-news', 'MTV News'), ('mtv-news-uk', 'MTV News (UK)'),
# ('national-geographic', 'National Geographic'), ('new-scientist', 'New Scientist'), ('newsweek', 'Newsweek'),
# ('new-york-magazine', 'New York Magazine'), ('nfl-news', 'NFL News'), ('polygon', 'Polygon'), ('recode', 'Recode'),
# ('reddit-r-all', 'Reddit /r/all'), ('reuters', 'Reuters'), ('talksport', 'TalkSport'), ('techcrunch', 'TechCrunch'),
# ('techradar', 'TechRadar'), ('the-economist', 'The Economist'), ('the-guardian-au', 'The Guardian (AU)'),
# ('the-guardian-uk', 'The Guardian (UK)'), ('the-hindu', 'The Hindu'), ('the-huffington-post', 'The Huffington Post'),
# ('the-lad-bible', 'The Lad Bible'), ('the-new-york-times', 'The New York Times'), ('the-next-web', 'The Next Web'),
# ('the-sport-bible', 'The Sport Bible'), ('the-telegraph', 'The Telegraph'), ('the-times-of-india', 'The Times of India'),
# ('the-verge', 'The Verge'), ('the-wall-street-journal', 'The Wall Street Journal'), ('the-washington-post', 'The Washington Post'),
# ('time', 'Time'), ('usa-today', 'USA Today')]


