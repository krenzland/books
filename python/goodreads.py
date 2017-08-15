#!/usr/bin/env python3

import requests as r
import xml.etree.ElementTree as x
import datetime
import os

def make_api_req(user, key, page=1):
    params = {'v': '2', 'key': key, 'id': user, 'page': page, 'per_page': 200}
    url = 'https://www.goodreads.com/review/list'
    resp = r.get(url, params=params)
    content = resp.content
    return content

class Book:
    def __init__(self, xml):
        self.id = xml.find('id').text
        self.rating = xml.find('rating').text
        
        raw_date = xml.find('read_at').text
        self.read_date = datetime.datetime.strptime(raw_date, '%a %b %d %H:%M:%S %z %Y')
        
        self.review = xml.find('body').text.strip().replace('<br />', '\n')
        if (self.review == ''):
            raise Exception()
        
        self.title = xml.find("book/title_without_series").text
        self_title_with_series = xml.find("book/title").text
        self.author = xml.find("book/authors/author/name").text
        self.published = xml.find("book/published").text
        return
    
    def to_org(self):
        head_sep = "---"
        title = "title: {} - {}".format(self.author, self.title)
        date = "date: {}".format(self.read_date.date())
        tags = "tags: books, {}".format(self.author)
        return "\n".join([head_sep, title, date, tags, head_sep, self.review])
    
    def get_filename(self):
        title =  "_".join([self.author, self.title])
        title = title.replace(" ", "").replace(".", "")
        return title + ".org"

def parse_response(reviews, books):
    for rev in reviews:
        try:
            books.append(Book(rev))
        except:
            pass
        
def get_reviews(user, key):
    finished = False
    page = 1
    books = []

    # Pagination
    while not finished:
        raw_response = make_api_req(user, key, page)

        reviews = x.fromstring(raw_response).find('reviews')

        num_books = int(reviews.attrib['total'])
        num_end = int(reviews.attrib['end'])
        num_start = int(reviews.attrib['start'])

        parse_response(reviews, books)

        page += 1
        finished = num_end >=num_books

    return books

def generate_org_files(folder, books):
     for book in books:
         filename = folder + book.get_filename()
         with open(filename, 'w') as f:
             f.write(book.to_org())
             print(filename)
             
def main():
    user = 9769674
    key = os.environ["GOODREADS_KEY"]

    books = get_reviews(user, key)
    folder = '../posts/'
    generate_org_files(folder, books)

if __name__ == "__main__":
    main()
