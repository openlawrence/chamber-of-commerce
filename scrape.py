#
import mechanize
import cookielib
from shove import Shove
from bs4 import BeautifulSoup
import urllib
import urlparse

class LawrenceChamber:
    def __init__(self):
        # Browser
        self.br = mechanize.Browser()

        # Cookie Jar
        self.cj = cookielib.LWPCookieJar()
        self.br.set_cookiejar(self.cj)


        # Store persistent objects in files
        self.file_data = Shove('file://cache')     
        self.file_data2 = Shove('file://cache2')     

    def categories(self):
        URL='http://www.lawrencechamber.com/CWT/External/wcpages/WCDirectory/Directory.aspx?&action=catlist&adkeyword=categorylist'

        # Open some site, let's pick a random one, the first that pops in mind:
        r = self.br.open(URL)
        html = r.read()

        # Show the source
        #print html
        # or
        #self.br.response().read()

        # Show the html title
        print self.br.title()

        # Show the response headers
        #print r.info()
        # or
        #print self.br.response().info()

        # Show the available forms
        for f in self.br.forms():
            print f

        # Select the first (index zero) form
        self.br.select_form(nr=0)

        # # Let's search
        # br.form['q']='weekend codes'
        # br.submit()
        # print br.response().read()

        # Looking at some results in link format
        for l in self.br.links():
            if l.url.find("CategoryID"): 
                print "link",l
                self.link(l)

    def category(self, url):

        if url in self.file_data:
            print "skip", url
            return
        # Open some site, let's pick a random one, the first that pops in mind:
        r = self.br.open(url)
        # Show the html title
        print self.br.title()

        self.file_data2[self.br.title()]=self.br.response().read()

    def link(self, l):
        self.file_data[l.url]=l


    def read_categories(self):
        for l in self.file_data:
            if l not in self.file_data:
                print "missing", l
            else:
                d =self.file_data[l]
                if isinstance(d, str):
                    pass
                else:
                    print d.absolute_url
                    if d.absolute_url.find("Category") > 0:
                        self.category(d.absolute_url)

    def parse_categories(self):
        for l in self.file_data2:
            d =self.file_data2[l]
            #print l
            parts =l.split("-")
            parts2=[]
            for x in parts:
                x = x.strip()
                if x != 'Lawrence Chamber of Commerce | Lawrence, KS':
                    parts2.append(x.capitalize())


            soup = BeautifulSoup(d)
            
            for l in soup.find_all('a') :
                href = l.get('href')
                if (href):
                    if href.find('DirectoryEmailForm.aspx') ==0 :
                        pass
                    elif href.find('action=map') > 0 :
                        pass
                    elif href.find('action=uweb') > 0 :
                        url=urllib.unquote(href).decode('utf8')  
                        parsed = urlparse.parse_qs(url)
                        print parsed['url'][0]
                        # p = int(url.find('url=')) + 4
                        # l2 = int(len(url))
                        # if p > -1:
                        #     #print "Index",p,l2
                        #     url2= url[p:l2]
                        #     if url2:
                        #         print "URL"," ".join(parts2), url2
