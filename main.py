from bs4 import BeautifulSoup

with open('home.html', 'r') as html_file: #open the file with "r" read mode, #with open and closes
    content = html_file.read()

    soup = BeautifulSoup(content, 'lxml')
    course_cards = soup.find_all('div', class_='card')
    for course in course_cards:
        course_name = course.h5.text
        course_price = course.a.text.split()[-1] #split the words by blank space and return the last (-1)

        print(f'{course_name} costs {course_price}')