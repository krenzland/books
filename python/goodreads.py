#!/usr/bin/env python3

import requests as r
import xml.etree.ElementTree as x
import datetime
import os
import re

def make_api_req(user, key, page=1):
    params = {'v': '2', 'key': key, 'id': user, 'page': page, 'per_page': 200}
    url = 'https://www.goodreads.com/review/list'
    resp = r.get(url, params=params)
    content = resp.content
    return content


def parse_series(title, title_with_series):
    # Remove title from series string
    series_str = title_with_series.replace(title, "")
    
    # string now has format " (series1, #number; series2, #number)"
    # Extract text in brackets
    match = re.match(' \((.*)\)', series_str)
    if not match:
        return ''
    
    series_str = match.group(1)
    return series_str
    
    # Split in list of series
    series = series_str.split(';')

    def s_to_t(s):
        #series, count = s.split(',')
        count = ''.join(re.findall(r'\d+', s))
        series = s.replace(count, '').replace('#', '').replace(',', '')
        return series.strip(), count.strip()

    series = [s_to_t(s) for s in series] 
    return series

class Book:
    def __init__(self, xml):
        self.id = xml.find('id').text
        self.rating = xml.find('rating').text
        
        raw_date = xml.find('read_at').text
        self.read_date = datetime.datetime.strptime(raw_date, '%a %b %d %H:%M:%S %z %Y')
        
        self.review = xml.find('body').text.strip().replace('<br />', '\n')
        self.has_review = self.review != ''
        
        self.title = xml.find('book/title_without_series').text
        self.title_with_series = xml.find('book/title').text
        self.series = parse_series(self.title, self.title_with_series)
        self.author = xml.find('book/authors/author/name').text
        self.published = xml.find('book/published').text
    
    def to_org(self):
        head_sep = "---"
        title = "title: {} - {}".format(self.author, self.title)
        date = "date: {}".format(self.read_date.date())
        tags = "tags: books, {}".format(self.author)
        return "\n".join([head_sep, title, date, tags, head_sep, self.review])
    
    def get_filename(self):
        title =  '_'.join([self.author, self.title])
        title = title.replace(' ', '').replace('.', '')
        return title + '.org'

    
def parse_response(reviews, books):
    for rev in reviews:
        try:
            books.append(Book(rev))
        except Exception as e:
            print(e)

        
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
         if book.has_review:
            filename = folder + book.get_filename()
            with open(filename, 'w') as f:
                f.write(book.to_org())
                print("Created review for {}.".format(filename))
             
def generate_org_table(folder, books):
    def stringify_series(series):
        return series
        return "; ".join(["{}: {}".format(s[0], s[1]) for s in series])

    header = "|author(s)|title|series|read data|"
    sep = "|--|--|--|--|"
    
    rows = [header, sep]
    for book in books:
        row = "|{}|{}|{}|{}|".format(book.author,
                                  book.title,
                                  stringify_series(book.series),
                                  book.read_date.date())
        rows.append(row)
    with open(folder + '/books.org', 'w') as f:
        f.write("\n".join(rows))
        print("Created table of read books")

                
def main():
    user = 9769674
    key = os.environ['GOODREADS_KEY']

    books = get_reviews(user, key)
    folder_posts = 'posts/'
    folder_list = 'lists/'
    generate_org_files(folder_posts, books)
    generate_org_table(folder_list, books)

if __name__ == '__main__':
    main()
