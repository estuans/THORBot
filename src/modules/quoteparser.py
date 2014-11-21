
from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class QuoteParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        pass
        '''
        if tag == "img":
            #This could be the percentage image, let's test it.
        '''
    def handle_endtag(self, tag):
        print "Encountered an end tag :", tag
    def handle_data(self, data):
        print "Encountered some data  :", data