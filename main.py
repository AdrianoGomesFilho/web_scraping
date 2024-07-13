from bs4 import BeautifulSoup
# first >  pip install requests
import requests

html_text = requests.get('https://www.timesjobs.com/candidate/job-search.html?searchType=Home_Search&from=submit&asKey=OFF&txtKeywords=&cboPresFuncArea=35').text
print(html_text)