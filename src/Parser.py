import urllib.request
from bs4 import BeautifulSoup


def getTitlesFromAll(amount, rating='all'):
    output = ''
    for i in range(1, amount + 1):
        try:
            if rating == 'all':
                html = urllib.request.urlopen('https://www.smartspate.com/smart-topics/page' + str(i) + '/').read()
            else:
                html = urllib.request.urlopen(
                    'https://www.smartspate.com/smart-topics/' + rating + '/page' + str(i) + '/').read()
        except urllib.error.HTTPError:
            print('Error 404 Not Found')
            break
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find_all('a', class_='post_title_link')
        for i in title:
            i = i.get_text()
            output += ('-"' + i + '", \n')
        return output


def getTitlesFromTop(amount, age='daily'):
    output = ''
    for i in range(1, amount + 1):
        try:
            html = urllib.request.urlopen(
                'https://www.smartspate.com/webdeveloper-topics' + age + '/page' + str(i) + '/').read()
        except urllib.error.HTTPError:
            print('Error 404 Not Found')
            break
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find_all('a', class_='post_title_link')
        for i in title:
            i = i.get_text()
            output += ('-"' + i + '", \n')
        return output
