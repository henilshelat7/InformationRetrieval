from bs4 import BeautifulSoup
from time import sleep
import requests
from random import randint
from html.parser import HTMLParser
import time
from collections import defaultdict
import json

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
class SearchEngine:
    @staticmethod
    def search(query, sleep=True):
        if sleep: # Prevents loading too many pages too soon
          time.sleep(randint(10, 100))
        temp_url = '+'.join(query.replace("\n", "").strip().split()) #for adding + between words forthe query
        url = 'https://www.duckduckgo.com/html?q=' + temp_url
        page = requests.get(url, headers=USER_AGENT)
        soup = BeautifulSoup(page.text,"html.parser")
        #return soup.prettify()
        new_results = SearchEngine.scrape_search_result(soup)
        return new_results
    @staticmethod
    def scrape_search_result(soup):
        raw_results = soup.find_all("a", attrs = {"class" : "result__a"})
        results = []
        #implement a check to get only 10 results and also check that URLs must not be duplicated
        for result in raw_results:
            link = result.get('href')
            results.append(link)
        return results[:10]

class GenerateResults:
    @staticmethod
    def queryToResult():
        results = {}
        with open('queries.txt','r') as queries:
            for query in queries:
                results[query] = SearchEngine.search(str(query))
        return results
    @staticmethod
    def output(queryResults):
        with open("queryResults.json", "w") as outfile:
            json.dump(queryResults, outfile, indent=4)
            
class CompareResults:
    matching_url = []
    @staticmethod
    def __clean_Result(url):
        index = url.find("//")
        if index > -1:
            url = url[index + 2:]
        # Ignore "www." in the URL
        if "www." in url:
            url = url[4:]
        # Ignore "/" at the end of the URL
        if url[-1] == "/":
            url = url[:-1]
        return url.lower()

    def sendQueries(queries, google_data, duckduck_data):
        
        compare_results = defaultdict(list)
        for i, query in enumerate(queries):
            query_results = duckduck_data[query]
            google_results = google_data[query]
            for j, qr in enumerate(query_results):
                qr = CompareResults.__clean_Result(qr)
                for k, google_qr in enumerate(google_results):
                    google_qr = CompareResults.__clean_Result(google_qr)
                    if qr == google_qr:
                        compare_results[i].append((j,k))
        return compare_results
    
    @staticmethod
    def calculate_rho(compare_results, queries):
        coefficient = 0
        query_number = set()
        stats = {}
        for s, qr in enumerate(queries):
            query_number.add(s)

        for i,results in compare_results.items():
            if int(i) not in query_number:
                coefficient = 0
            elif len(results) == 1:
                if results[0][0] == results[0][1]:
                    coefficient = 1
                else:
                    coefficient = 0
            else:
                for a,b in results:
                    print(a,b)
                difference = sum([(a - b) ** 2 for a,b in results])
                coefficient = 1 - ((6 * difference) / (len(results) * (len(results) ** 2 - 1)))
            stats[i] = {'Overlap': len(results), 'Percent': (len(results)/10) * 100, 'Rho': coefficient}
        return stats
    
    @staticmethod
    def calculate_avg_stats(stats):
        avg_overlap, avg_percent_overlap, avg_coefficient = 0, 0, 0
        for _, value in stats.items():
            avg_overlap += value["Overlap"] / 100
            avg_percent_overlap += value["Percent"] / 100
            avg_coefficient += value["Rho"] / 100
        stats["Averages"] = {"Overlap": avg_overlap, "Percent": avg_percent_overlap, "Rho": avg_coefficient}
        CompareResults.write_result(stats)

    @staticmethod
    def write_result(stats):
        with open("hw1.csv", "w") as f:
            f.write("Queries, Number of Overlapping Results, Percent Overlap, Spearman Coefficient\n")
            for query_number, values in stats.items():
                if type(query_number) == int:
                    query_number+=1
                f.write(f"Query {query_number}, {values['Overlap']}, {values['Percent']}, {values['Rho']}\n")

            
#############Driver code############

def main():
    # queryResults = GenerateResults.queryToResult()
    queries = []
    with open('hw1.json','r') as f:
        queryResults = json.load(f)

    for query in queryResults.keys():
        queries.append(query)
    GenerateResults.output(queryResults=queryResults)
    with open("google-results.json", "r") as f:
        google_results = json.load(f)
    compare_results = CompareResults.sendQueries(queries, google_results, queryResults)
    stats = CompareResults.calculate_rho(compare_results, queries)
    stats_1 = CompareResults.calculate_avg_stats(stats)
    #CompareResults.write_result(stats_1)


if __name__ == "__main__":
    main()
    
    

    #x = SearchEngine.search("Cristiano Ronaldo")
    # with open('resultoutput.html','w') as f:
    #     for l in x:
    #         f.write(l + "\n")