import urllib.request
import requests
from bs4 import BeautifulSoup
import re
import json


if(1):
    #**************************FOR ROTTEN TOMATOES ********************************
    urlMain = 'https://www.rottentomatoes.com/browse/dvd-all/?services=netflix_iw;amazon_prime;hbo_go;amazon;vudu;itunes;flixster&sortBy=tomato'
    r = requests.get(urlMain)
    soup = BeautifulSoup(r.text, "html.parser")

    #print(soup)

    #ml = soup.findAll(text=re.compile('a'))

    #movieList = soup.find_all()
    #mydivs = soup.findAll("div", { "class" : "mb-movie" })
    #print(mydivs)
    #print (ml)

    '''
    for div in mydivs:
        print(div)
        break
    '''

    urlList = soup.find_all('a', href=re.compile('/m/'))  #"/m/phantasm_remastered_2016/")

    #print(urlList)

    filteredUrlList = re.findall('(/m/.+)/',str(urlList))
    #print(filteredUrlList)

    testFlag =0
    siteCounter = 0
    pageCounter = 402

    while (siteCounter < 12000):
        for url in filteredUrlList:
            if (testFlag != 1):
                break
                url = url + '/'
            errorFlag = 1
            url = 'https://www.rottentomatoes.com/' + url
            try:
                response = urllib.request.urlopen(url)
            except:
                errorFlag = 0
                print('')

            if errorFlag != 0:
                webContent = response.read().decode('utf-8')

                movieName = url.split('m/',1)[1][2:-1]
                #print(movieName)
                f = open('rotten/'+ movieName + '.html', 'w')
                f.write(webContent)
                f.close
                siteCounter = siteCounter + 1

    # with requests.Session() as session:
     #   response = session.post("https://www.rottentomatoes.com/browse/dvd-all/?services=netflix_iw;amazon_prime;hbo_go;amazon;vudu;itunes;flixster", data={'start':0})
      #  print(response.content)
        testFlag = 1
        pageCounter = pageCounter + 1
        with requests.Session() as session:
            response = session.get('https://www.rottentomatoes.com/api/private/v1.0/m/list/find?page=' + str(pageCounter) + '&limit=30&type=dvd-all&services=amazon%3Bamazon_prime%3Bflixster%3Bhbo_go%3Bitunes%3Bnetflix_iw%3Bvudu&sortBy=release').json()
        #print(response.content)
        #jsonUrlList = str(response.content)
        #k = json.loads(jsonUrlList)
        #k = json.loads(response.content.read)
        filteredUrlList = []
        for result in response["results"]:
            #print(result)
            filteredUrlList.append(result["url"])

    pageCountString = str(pageCounter)
    try:
        f = open('rotten/pageDetails', 'w')
        f.write(pageCountString)
        f.close
    except:
        print('')


    #**************************FOR TMDB********************************

if(0):
    urlMain = 'https://www.themoviedb.org/movie?page='
    i = 0
    for i in range(1,981):
        print('page: ' + str(i))
        r = requests.get(urlMain + str(i))
        soup = BeautifulSoup(r.text, "html.parser")

        urlList = soup.find_all('a',{ "class" : "result" })
        #href=re.compile('/movie/'))  #"/m/phantasm_remastered_2016/")

        #print(urlList)

        filteredUrlList = re.findall('"(/movie/[^\s]+)',str(urlList))
        #print(filteredUrlList)


        for j in range(0,len(filteredUrlList)):
            errorFlag = 1
            url = filteredUrlList[j]
            url = 'https://www.themoviedb.org' + url[0:-1]
            try:
                response = urllib.request.urlopen(url)
            except:
                errorFlag = 0
                print('')

            if errorFlag != 0:
                webContent = response.read().decode('utf-8')

                movieName = url.split('movie/',1)[1]
                #print(movieName)
                f = open('tmdb/'+ movieName + '.html', 'w')
                try:
                    f.write(webContent)
                except:
                    print('')
                f.close

            j = j+3

    pageCountString = str(i)
    try:
        f = open('tmdb/pageDetails.txt', 'w')
        f.write(pageCountString)
        f.close
    except:
        print('')

    #STOPPED AT PAGE 17
