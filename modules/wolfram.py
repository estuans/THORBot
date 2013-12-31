"""
Wolfram Alpha code courtesy of http://advencode.wordpress.com/2011/10/17/simple-query-request-with-wolfram-api/
"""

import urllib2
import urllib
import sys
import httplib
from xml.etree import ElementTree as eTree

appid = "YT6T34-E7L5L5YWWK"


class wolfram(object):
    def __init__(self, appid):
        self.appid = appid
        self.base_url = "http://api.wolframalpha.com/v2/query?"
        self.headers = {'User-Agent':None}

    def __get__xml(self, ip):
        url_params = {'input': ip, 'appid': self.appid}
        data = urllib.urlencode(url_params)
        req = urllib2.Request(self.base_url, data, self.headers)
        xml = urllib2.urlopen(req).read()
        return xml

    def _xmlparser(self, xml):
        data_dics = {}
        tree = eTree.fromstring(xml)
        for e in tree.findall('pod'):
            for item in [ef for ef in list(e) if ef.tag == 'subpod']:
                for it in [i for i in list(item) if i.tag == 'plaintext']:
                    if it.tag == 'plaintext':
                        data_dics[e.get('title')] = it.text
        return data_dics

    def search(self, ip):
        xml = self.__get__xml(ip)
        result_dics = self._xmlparser(xml)
        return result_dics

if __name__ == "__main__":
    appid = sys.argv[0]
    query = sys.argv[1]
    w = wolfram(appid)
    w.search(query)