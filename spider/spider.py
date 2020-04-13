from urllib.request import urlopen
from bs4 import BeautifulSoup
from link_finder import LinkFinder
from domain import *
from general import *
from nltk.corpus import stopwords

import re

class Spider:
    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    crawledDict_file = ''
    queue = set()
    crawled = set()
    crawledDict = set()

    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        Spider.crawledDict_file = Spider.project_name + '/crawledDict.txt'
        self.boot()
        self.crawl_page('First spider', Spider.base_url)


    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)


    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        try:
            if page_url not in Spider.crawled:
                print(thread_name + ' now crawling ' + page_url)
                print('Queue ' + str(len(Spider.queue)) + ' | Crawled  ' + str(len(Spider.crawled)))
                Spider.add_links_to_queue(Spider.gather_links(page_url))
                Spider.queue.remove(page_url)
                # Show all the crawled links so u can check the same url input
                Spider.crawled.add(page_url)
                keywords = Spider.get_keywords(page_url)
                if len(keywords) > 0:
                    Spider.crawledDict.add(f"{page_url} : {str(keywords)}")

                Spider.update_files()
        except Exception as e:
            pass

    @staticmethod
    def removeStopWord(text):

        easy_word = {'however', "'m", "'ll", "'d", 'already', 'thank', 'thanks', 'such', 'as',
                     'please', 'since', 'also', 'help', "this", "is", "headlines", "deadline", "catalog",
                     "requirements", "for", "search", "university", 'work', 'working', 'learn', 'learning',
                     'that', 'those', 'these', 'if', 'with', 'would', 'want', 'both', 'us', 'me', 'have'
                     "for", "the", "and", "all", "earn", "who", "to", "use", "in", "of", "at", "my", "you", "I", "your"}

        new_text = [' '.join(w for w in word.split() if w.lower() not in easy_word)
                 for word in text
                 ]
        return new_text

    # reformat email and phone_number with in the list
    @staticmethod
    def formatWord(text):

        # format jax5 @ calstatela.edu to jax5@calstatela.edu
        emails = re.findall("[A-Za-z0-9._%+-]+[] @ []+[A-Za-z0-9.-]+\.[A-Za-z]{2,4}", text)
        for email in emails:
            newEmail = email.replace(' ', '')
            text = text.replace(email, newEmail + ' ')

        # format ( 111 ) 222-3333 to (111)222-3333
        phones = re.findall('[\+\(+\]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
        for phone in phones:
            newPhone = phone.replace(' ', '')
            text = text.replace(phone, newPhone + ' ')

        # format e & t to e&t
        et_buildings = re.findall('e & t', text)
        for et_building in et_buildings:
            new_et = et_building.replace(' ', '')
            text = text.replace(et_building, new_et)

        return text

    @staticmethod
    def removeComment(text):
        text = re.sub("(<!--.*?-->)", "", text, flags=re.MULTILINE)
        # not case sensitive :D
        csula_hardCode =['Ph.D.', 'Jump to navigation', 'Skip to content', 'Ways to Give', 'Cal State LA on Twitter',
                         'AN EQUAL OPPORTUNITY/TITLE IX EMPLOYER', '90032(323)343-3000',
                         'CARE Team', 'Cal State LA on YouTube', 'LAunchPad', 'Cal State LA on Instagram',
                         '5151 State University Drive Los Angeles CA 90032(323)343-3000 © 2019 Trustees of the California State University',
                         '© 2019 Trustees of the California State University',
                         'Cal State LA on Facebook', 'Cal State LA on LinkedIn', 'ConnectContact Us', 'Social Media Hub',
                         'California State University Los Angeles', 'campus safety', 'Mind Matters', 'Jobs', '5151 State Drive',
                         '5151 State Drive Los Angeles CA 90032(323)343-3000']

        for i in csula_hardCode:
            text = text.replace(i, '')

        return text

    @staticmethod
    def get_keywords(page_url):
        html_string = ''
        keywords = set()

        try:
            # check url,
            # Remove dead links
            response = urlopen(page_url)

            # Only show active links to crawled.txt
            Spider.crawled.add(page_url)

            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")

            soup = BeautifulSoup(html_string, 'lxml')

			# Remove header and Styles
            [tag.decompose() for tag in soup(["head", "style", "script", "header", "img"])]

            hugeString = (soup.get_text())

            hugeString = Spider.formatWord(hugeString)
            hugeString = Spider.removeComment(hugeString)

            htmlSplit = hugeString.split('\n')

            htmlSplit = Spider.removeStopWord(htmlSplit)

            keyword_list = []
            for line in htmlSplit:
                line = line.strip()
                if line:
                    line = line.replace('\"', '').replace('\'', '').replace(',', '')
                    keyword_list.append(line)

##################################################################################################
# Add extract data for database
# h1 = +10
# h2 = +7
# h3 = +5
# strong = +3
# italic = +2
# ##################################################################################################

            for i in soup.find_all('h1'):
                keyword = Spider.removeStopWord(i)

                if (len(keyword) > 0):
                    for j in range(10):
                        keyword_list.append(keyword)

            for i in soup.find_all('h2'):
                keyword = Spider.removeStopWord(i)
                if (len(keyword) > 0):
                    for j in range(7):
                        keyword_list.append(keyword)

            for i in soup.find_all('h3'):
                keyword = Spider.removeStopWord(i)
                if (len(keyword) > 0):
                    for j in range(5):
                        keyword_list.append(keyword)

            for i in soup.find_all('strong'):
                keyword = Spider.removeStopWord(i)
                if (len(keyword) > 0):
                    for j in range(3):
                        keyword_list.append(keyword)

            for i in soup.find_all('i'):
                keyword = Spider.removeStopWord(i)

                if (len(keyword) > 0):
                    for j in range(2):
                        keyword_list.append(keyword)

##################################################################################################
##################################################################################################

            # Save the keywords as list
            # Convert the whole list to string
            # Store this to set

            keywords = {str(keyword_list)}

        except Exception as e:
            pass
        return keywords

    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")
            finder = LinkFinder(Spider.base_url, page_url)
            finder.feed(html_string)
        except Exception as e:
            pass
            return set()
        return finder.page_links()

    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            if Spider.domain_name != get_domain_name(url):
                continue
            if "/login?" in url or "calendar/" in url or "group-calendar-event" in url or "#" in url or "//moodle-" in url or "default/files" in url:
                continue
            Spider.queue.add(url)

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)
        set_to_file(Spider.crawledDict, Spider.crawledDict_file)
