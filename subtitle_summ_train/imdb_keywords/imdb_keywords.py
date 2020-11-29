import requests
from lxml import etree
from bs4 import BeautifulSoup
import urllib.parse as url_parse
import re


def imdb_key_words(imdb_url):
    return_tuple_kw_votes = []
    page_url_parts = url_parse.urlparse(imdb_url)
    print(page_url_parts)
    new_url = url_parse.ParseResult(scheme=page_url_parts.scheme, 
                                    netloc=page_url_parts.netloc, 
                                    path=page_url_parts.path + "/keywords", 
                                    params='', query='', fragment='')

    keywords_url = url_parse.urlunparse( new_url)
    print(keywords_url)
    page = requests.get(keywords_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    keyword_list = soup.findAll("td", {"class":"soda sodavote"})
    print(keyword_list)
    for keyword_entry in keyword_list:
        keyword = (keyword_entry.find('div', {"class": "sodatext"}).find('a').text)
        vote_text = keyword_entry.find('div', {'class':'interesting-count-text'}).find('a').text
        m = re.match(" ([0-9]+)", vote_text)
        #print(vote_text)
        if m and int(m.group(0)) > 0:
            return_tuple_kw_votes.append((keyword, int(m.group(0)) ))
            print(keyword, int(m.group(0)))
        
        #print(keyword_entry.a.text)
        #print(len(movie_desc))
    return return_tuple_kw_votes
    


if __name__ == "__main__":
    imdb_url = "https://www.imdb.com/title/tt0050083"
    imdb_key_words(imdb_url)