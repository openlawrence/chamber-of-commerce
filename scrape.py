import pprint
import re
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
        # Select the first (index zero) form
        self.br.select_form(nr=0)

        # # Let's search
        # br.form['q']='weekend codes'
        # br.submit()
        # print br.response().read()

        # Looking at some results in link format
        for l in self.br.links():
            if l.url.find("CategoryID"):
                #print "link",l
                self.link(l)

    def category(self, url):

        if url in self.file_data:
            #print "skip", url
            return
        # Open some site, let's pick a random one, the first that pops in mind:
        r = self.br.open(url)
        # Show the html title
        #print self.br.title()

        self.file_data2[self.br.title()]=self.br.response().read()

    def link(self, l):
        self.file_data[l.url]=l


    def read_categories(self):
        for l in self.file_data:
            if l not in self.file_data:
                #print "missing", l
                pass
            else:
                d =self.file_data[l]
                if isinstance(d, str):
                    pass
                else:
                    #print d.absolute_url
                    if d.absolute_url.find("Category") > 0:
                        self.category(d.absolute_url)

    def parse_categories_links(self):
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
                        #print parsed['url'][0]
                        # p = int(url.find('url=')) + 4
                        # l2 = int(len(url))
                        # if p > -1:
                        #     #print "Index",p,l2
                        #     url2= url[p:l2]
                        #     if url2:
                        #         print "URL"," ".join(parts2), url2

    def process(self, l, data2):
        #name = ''
        #name = name + str(l)
        href = l.get('href')
        if (href):
            url=urllib.unquote(href).decode('utf8')
            parsed = urlparse.parse_qs(url)
            parsed2 = urlparse.urlparse(url)
            #data2['name']=name
            if 'profileid' in parsed:
                for x in ('listingid,''profileid','Address','City','Zip','State','latitude','longitude'):
                    if x in parsed :
                        v = parsed[x][0]
                        data2[x]=v

                if href.find('DirectoryEmailForm.aspx') ==0 :
                    pass
                elif href.find('action=map') > 0 :
                    #print parsed
                    pass
                elif href.find('action=uweb') > 0 :
                    url=urllib.unquote(href).decode('utf8')
                    parsed = urlparse.parse_qs(url)
                    data2['href']=parsed['url'][0]


    def parse_address(self, t):
        data1 = []
        row = 0
        for tr in t.children:
            #print "Table Row",row,tr
            if tr.name == "tr":
                if not tr.get("class") :
                    continue
                data2={}
                row = row + 1
                clasz = tr.get("class")[0]
                strings = []
                if clasz == "GeneralBody":
                    for td in tr.children:
                        valign = td.get("valign")

                        if not valign:
                            continue
                        if  valign != 'top':
                            continue

                        for br in td.children:
                            if br.name:
                                for l in br.find_all('a') :
                                    self.process(td,data2)
                            else:
                                strings.append(str(br))
                strings = ",".join(strings)
                if strings:
                    data2["row%d" % row]= strings
                    data1.append(data2)
                #data.append(data2)
        if (row > 1):
            #print "Data",pprint.pformat(data1)
            return data1


    def parse_main_table(self,t):
        data = {}
        for tr in t.children:
            for td in tr:
                for c in td:
                    if c.name == "b":
                        for a in c:
                            if a.name == "a":
                                data["name"]=a.string
                                self.process(a,data)
                    elif c.name == "p":
                        for i in c:
                            for b in i :
                                m = re.match(r"Member Since (\d\d\d\d)",b.text )
                                if m:
                                    data["member_since"]=m.group(1)
                    elif c.name == "table":
                        if "addr" not in data:
                            data["addr"]=self.parse_address(c)
                    else:
                        print "SKIP",c.name, c
                        pass
                    #print "Content",c
        return data
        
    def parse_categories_addresses(self):

        total =[]

        for l in self.file_data2:
            print "Loading", l
            d =self.file_data2[l]
            soup = BeautifulSoup(d)
            #print l
            parts =l.split("-")
            parts2=[]

            for x in parts:
                x = x.strip()
                if x != 'Lawrence Chamber of Commerce | Lawrence, KS':
                    parts2.append(x.capitalize())
            new_category=[" ".join(parts2)]


            for t in soup.findAll('table') :
                if t.get("width") == "100%":
                    if t.get("cellspacing") =="0":
                        if t.get("cellpadding") =="3":
                            data1= self.parse_main_table(t)
                            data1['category']=new_category
                            total.append(data1)
        print pprint.pprint(total)
