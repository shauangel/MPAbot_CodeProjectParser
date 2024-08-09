import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import re
import json
from concurrent.futures import ThreadPoolExecutor


class CodeProjectData:
    def __init__(self, urls):
        self.__links = urls
        self.__results = []

    def get_posts(self):
        def progress_indicator(future):
            print('.', end='', flush=True)
            self.__results.append(future.result())

        with ThreadPoolExecutor(max_workers=len(self.__links)) as executor:
            futures = [executor.submit(CodeProjectData.parse_website, url) for url in self.__links]
            for future in futures:
                future.add_done_callback(progress_indicator)
        print("Done!!")

    @staticmethod
    def parse_website(url):
        try:
            data = {"question": {}, "answers": [], 'link': url}
            # find post id
            try:
                post_id = PurePosixPath(urlparse(unquote(url)).path).parts[2]
                data['question']['id'] = str(int(post_id))
            # response error when id found
            except ValueError:
                return "No post_id"

            # Scrape Questions
            resp = requests.get(url)
            soup = BeautifulSoup(resp.content, 'lxml')
            data['tags'] = [div.a.text for div in soup.findAll('div', attrs= {'class': 't'})]
            data['question']['title'] = soup.find('h1', attrs= {'id': 'ctl00_ctl00_MC_AMC_ItemTitle'}).text
            data['question']['content'] = soup.find("div", attrs={"id": "CC"}).find("div", attrs={"itemprop": "text"}).text

            # Scrape Answers
            data["answers"] = []
            for div in soup.findAll("div", attrs={"id": re.compile("AnswerGroup")}):
                user_link = div.find("div", attrs={"class": "member-rep-container"}).find("a")["href"]
                content = div.find("div", attrs={"class": "text"})
                object_ref = div.find("div", attrs={"id": re.compile("RatingTable")})
                vote, v_count = CodeProjectData.get_vote(object_ref['data-objectref'])
                answer = {'id': object_ref['data-objectref'],
                          'type': div['itemprop'],
                          'content': content.text,
                          'score': vote,
                          'vote_count': v_count,
                          'user_reputation': CodeProjectData.get_user_reputation(user_link)
                          }
                data["answers"].append(answer)
        except Exception as e:
            data = {"response":  e.__class__.__name__ + " : " + e.args[0]}
        return data

    @staticmethod
    def get_vote(ans_id):
        histogram = "https://www.codeproject.com/script/Ratings/ajax/Histogram.aspx?obrfgd=(ans_id)&wd=130"
        resp = requests.get(histogram.replace("(ans_id)", ans_id))
        soup = BeautifulSoup(resp.content, 'lxml')
        try:
            votes = soup.find('div', attrs= {'class': 'small-text align-center'})
            return float(votes.text.split("/")[0]), int(votes.text.split("-")[1].split(" ")[1])
        except AttributeError:
            return 0, 0

    @staticmethod
    def get_user_reputation(href):
        url_page = "https://www.codeproject.com" + href
        resp = requests.get(url_page)
        soup = BeautifulSoup(resp.content, 'lxml')
        div = soup.find_all("div", attrs={"class", "medium-text"})
        reputations = [int(d.text.replace(",", "")) for d in div]
        return sum(reputations)

    def get_results(self):
        return self.__results


if __name__ == "__main__":
    print("CodeProject Parser v.0")
    # test = "https://www.codeproject.com/Questions/5345658/Unable-to-pass-values-form-JS-func-ajax-to-Python"
    # test = "https://www.codeproject.com/Questions/5296802/Make-flask-socket-io-server-accessible"
    test = [
        "https://www.codeproject.com/Questions/5296802/Make-flask-socket-io-server-accessible",
        "https://www.codeproject.com/Questions/5345658/Unable-to-pass-values-form-JS-func-ajax-to-Python",
        "https://www.codeproject.com/Questions/5332367/Why-is-my-Python-server-always-returning-404-when",
        "https://www.codeproject.com/Questions/5251627/After-published-rest-api-returning-internal-server",
        "https://www.codeproject.com/Questions/5311037/How-to-retain-selected-columns-from-dropdown-for-n"
    ]
    parser = CodeProjectData(test)
    parser.get_posts()
    print(parser.get_results())
    with open("../../../DataController/app/models/test_cp.json", 'w', encoding="utf-8") as file:
        json.dump(obj=parser.get_results(), fp=file)

