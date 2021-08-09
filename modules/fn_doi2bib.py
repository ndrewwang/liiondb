import requests
import re

def doi2citation_entry(doi_str):
    def doi2bib(doi):


      url = "http://dx.doi.org/" + doi

      headers = {"accept": "application/x-bibtex"}
      r = requests.get(url, headers = headers)

      return r.text


    DOI = doi_str
    str = doi2bib(doi_str)
    str_array = re.split('@article{|\n\t| = ',str)
#     print(str_array)


#     print(str_array)
    CitationTag = str_array[1][0:-1]
    for i in range(0,len(str_array)):
        istr = str_array[i]

        if istr == 'url': 
            URL = str_array[i+1][1:-2]
#         else:
#             URL = ''
#             print(URL)

        if istr == 'year': 
            Year = str_array[i+1][0:-1]
#             print(Year)
#         else:
#             Year = ''

        if istr == 'title': 
            Title = str_array[i+1][1:-2]
#             print(Title)

        if istr == 'author': 
            author_str = str_array[i+1][1:-2]
            author_str = author_str.replace(' and',',')
#             author_str = author_str.split(' and ')
            Authors = author_str
            
    data = {
        'Citation Tag': CitationTag,
        'DOI': DOI,
        'URL': URL,
        'Year': Year,
        'Title': Title,
        'Authors': [Authors],
            }
    return data