from bs4 import BeautifulSoup
import urllib2

url="http://pinterest.com/nordic_design/following/"
htmlfile=urllib2.urlopen(url)
source=htmlfile.read()
soup=BeautifulSoup(source)
