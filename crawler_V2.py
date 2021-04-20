from bs4 import BeautifulSoup
import csv
import requests
import re
from goose3 import Goose
from retry import retry


# get the link to each news from the home page
def get_linklists(soup):
    # create a list to contain the unselected links
    link_raw = []
    # create a list to contain the selected links
    link_lists = []
    # get all <a> tags
    for k in soup.find_all('a'):
        # get all href in the <a> tags
        link = k.get('href')
        # if the link contains '/article', this is a link to an article
        if '/article' in link:
            # append all links to articles to the unselected list
            link_raw.append(link)
    # because each news has picture links and content links, the links will be repeated, and the duplicate links need to be removed
    for i in range(len(link_raw) - 1):
        # remove the repeated links
        if link_raw[i] != link_raw[i + 1]:
            # append the selected links to link_list
            link_lists.append(link_raw[i])
    return link_lists

# the network is not stable, so use retry() to execute this function again after failure
@retry()
# get the content of each news
def get_newscontent(link_lists):
    # create a list to contain news of each page
    news_contents = []
    # traverse the links of news to get the content of each news
    for link in link_lists:
        html = 'https://www.reuters.com' + link
        g = Goose({'enable_image_fetching': False})
        article = g.extract(url=html)
        news_contents.append(article.cleaned_text)
        
    return news_contents

    


def Load_csv(csv_file_name=""):
    """
    从CSV文件中读取数据信息
    :param csv_file_name: CSV文件名
    :return: Data：二维数组
    """
    csv_reader = csv.reader(open(csv_file_name))
    Data=[]
    for row in csv_reader:
        Data.append(row)
#     print("Read All!")
    return Data


def get_current_id(file_name = ''):
    file_id = Load_csv('Reuters_news_id.csv')
    
    tmp_set = set()
    
    for i in file_id:
        tmp_set.add(i[0])
    return tmp_set

if __name__ == '__main__':
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Referer': "https://item.jd.com/100000177760.html#comment"}
        
        
    # create a CSV to contain data of news
    ff = open('Reuters_news.csv', 'a+', newline='', encoding='utf-8')
    csv_writer = csv.writer(ff)
      # add header
#    csv_writer.writerow(['Id', 'Date', 'Title', 'Content'])
    
    ff_id = open('Reuters_news_id.csv', 'a+', newline='', encoding='utf-8')
    id_writer = csv.writer(ff_id)
    
    #get store id
    
    id_set = get_current_id('./Reuters_news_id.csv')
    
    
    print('start!')
    
  
    
   
    
    #The top ten are news
    num = 10
    
    
    
    # get news data in the given page range
    for page in range(100):
        print('{} page start!'.format(page))
        requests.packages.urllib3.disable_warnings()
        url = 'https://www.reuters.com/news/archive/businessnews?view=page&page={}&pageSize=10'.format(str(page))
        print('url: {}'.format(url))
        r = requests.get(url, headers=headers, verify=False)
        print('request done')
        soup = BeautifulSoup(r.content, 'lxml')
        # get title of each news
        title = soup.find_all('h3', class_='story-title')[:num]
        
        
        
        # get release time of each news
        time = soup.find_all('time')[:num]
        # get 10 links to news of each page
        link_lists = get_linklists(soup)[:num]
        
        # create a list to contain the id of each news
        id_list = []
        # get news id
        for link in link_lists:
            id_list.append(str(link[:: -1][0:11][::-1]))
        # get news content
        news_lists = get_newscontent(link_lists)

       
        for i in range(len(id_list)):
            if(id_list[i] in id_set):
                continue
            else:
#               write news data to CSV
                csv_writer.writerow([id_list[i], time[i].text, str(title[i].text).strip(), news_lists[i]])
                id_writer.writerow([id_list[i]])
        
       
        print("Page {} is finished".format(page + 1))    
        
        break
ff.close()
ff_id.close()
