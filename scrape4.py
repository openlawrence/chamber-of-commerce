#
import mechanize
import cookielib
from shove import Shove
from scrape import LawrenceChamber
                
l = LawrenceChamber()
l.parse_categories()
