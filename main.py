import requests
from bs4 import BeautifulSoup

url = "https://dejt.jt.jus.br/dejt/f/n/diariocon"

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Find relevant sections containing notifications
notifications = soup.find_all("div", class_="notification-class")  # Adjust the class name as needed

for notification in notifications:
    if "Vitor Leandro de Oliveira" in notification.text:
        print(notification.text)
