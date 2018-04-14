import json, os
import urllib, urllib.request
from bs4 import BeautifulSoup
from socket import timeout
import threadpool
import queue

BASE_URL = r"http://8bbzgj41nl-dsn.algolia.net/1/indexes/textbook_index?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.24.11\
&x-algolia-application-id=8BBZGJ41NL&x-algolia-api-key=ed21ea5a6b4a9a84643f2a0e81171470&callback=algoliaJSONP_2&query=&facets=*\
&facetFilters=%5B%22subject_ids%3A30%22%5D&maxValuesPerFacet=50&hitsPerPage=50&page="

CS_JSON = "all_cs.json"

def page_books(url):
	res_str = urllib.request.urlopen(url).read().decode("utf-8")
	l, r = res_str.find("{"), res_str.rfind("}")
	if l > 0 and r > 0:
		js_str = res_str[l:(r+1)]

	json_obj = json.loads(js_str)
	return json_obj["hits"]


def get_all_books(page_count):
	all_books = []
	for pg in range(page_count):
		url = BASE_URL + str(pg)
		all_books += page_books(url)
	all_books_dict = {"books": all_books}
	with open(CS_JSON, "w") as outfile:
		json.dump(all_books_dict, outfile)
	return all_books_dict


def is_empty(url):
	try:
		html = urllib.request.urlopen(url, timeout = 10).read().decode("utf-8")
	except timeout:
		return False
	soup = BeautifulSoup(html, "html.parser")
	toc = soup.find("article", {"class": "toc"})
	return bool(len(toc.find_all("section")) < 2)


def check_book(book, filled_queue):
	print("Processing: " + book["isbn"], book["title"])
	if not is_empty(SLADER_BASE + book["get_absolute_url"]):
		filled_queue.put((book["isbn"], book["title"]))


def print_new_books(filled_books):
	""" Print the newly added books since the last check """
	old_books = {}
	if os.path.exists(FILLED_BOOKS_FILE):
		with open(FILLED_BOOKS_FILE, "r") as fbf:
			old_books = json.load(fbf)

	print("************** Newly Added Books **************")
	for isbn, title in filled_books:
		if isbn not in old_books:
			print(isbn, title)


SLADER_BASE = "https://slader.com"
FILLED_BOOKS_FILE = ".sladerfilledcs"
def find_all_filled_books(file_name):
	with open(file_name, "r") as infile:
		g = json.load(infile)

	filled_queue = queue.Queue()
	pool = threadpool.ThreadPool(20)
	for book in g["books"]:
		pool.add_task(check_book, book, filled_queue)
	pool.wait_completion()
	filled_books = list(filled_queue.queue)

	print_new_books(filled_books)
	# Dump to file
	with open(FILLED_BOOKS_FILE, "w") as fbf:
		json.dump({isbn: title for isbn, title in filled_books}, fbf, indent=4)

if __name__ == "__main__":
	if not os.path.exists(CS_JSON):
		get_all_books(10)
	find_all_filled_books(CS_JSON)
		

