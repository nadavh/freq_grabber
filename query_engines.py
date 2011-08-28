"""
Classes for query engines
"""
import urllib2
import base64
import re

class WSError (Exception):
    """
    General Error
    """
    def __init__(self, message, debug_info=""):
        self.message = message
        self.debug_info = debug_info

    def __str__(self):
        return str(self.message)

    def get_debug_info(self):
        return str(self.debug_info)

class WSLoginError (WSError):
    """
    Error while logging-in or login timeout
    """

class WordStatsQuery:
    """
    Generic class for querying frequency of a word in text search engines
    """

    def __init__(self, user, password, debug=False):
        self.user = user
        self.password = password
        self.debug = debug

    def query(self, word):
        """
        Query word, and return frequency.
        Returns: (word, hit_count, per_million)
        """
        raise WSError("WordStatsQuery.query: Not yet Implemented")

class SCN (WordStatsQuery):
    """
    Query the SCN site
    """

    base_url  = "http://scn.jkn21.com"
    query_url = base_url + "/~perc04/cgi-bin/pat8.cgi"
    login_url = base_url + "/~perc04/cgi-bin/login1.cgi"

    def query(self, word):
        """
        Query word, and return frequency.
        Login if needed.
        Returns: (word, hit_count, per_million)
        Exceptions: WSError
        """

        try:
            result = self.__query(word)
        except WSLoginError, err:
            # login timeout, try to log-in and re-run
            if self.debug: print "Logging in to SCN.."
            self.__login()
            result = self.query(word)

        return result

    def __login(self):
        """
        Login to site with user and password
        Exceptions: WSLoginError
        """

        # set login parameters
        login_data_list = [
            ('username', self.user),
            ('password', self.password),
            ('ui_lang', 'e'),
            ('func', 'login'),
            ('lang', 'eng')
            ]
        login_data = '&'.join(["%s=%s" % (field, value)
                               for field, value in login_data_list])

        # login to server
        try:
            request = urllib2.Request(self.login_url)
            request.add_data(login_data)
            response = urllib2.urlopen(request)
            response_html = response.read()
        except Exception, err:
            raise WSError("Can't connect to SCN (%s): %s" %
                          (self.query_url, str(err)))

        # validate login
        if "Login incorrect." in response_html:
            raise WSLoginError("Couldn't login to SCN. Bad user/password", response_html)
        elif "<TITLE>SCN [ user:" not in response_html:
            raise WSLoginError("Couldn't login to SCN", response_html)

    def __query(self, word):
        """
        Query word, and return frequency.
        Returns: (word, hit_count, per_million)
        Exceptions: WSError, WSLoginError
        """

        # set word query parameters
        query_data_list = (
            ('username', self.user),
            ('swd', word),
            ('sort', '0'),
            ('matchclass', '0'),
            ('pagenum', '0'),
            ('Winwidth', '1000'),
            ('Sclass', 'PH'),
            ('Winposy', '4'),
            ('Winposx', '4'),
            ('char', ''),
            ('sortdet3', ''),
            ('Dwnldwnum', '0'),
            ('pagewid', '120'),
            ('sortdet4', ''),
            ('WinName', 'perc040607rw'),
            ('sortkeyw', 'w'),
            ('sortdet1', ''),
            ('sortdet5', ''),
            ('lang', 'eng'),
            ('prdetp', ''),
            ('sortkeyp', ''),
            ('WinID', 'A'),
            ('phlm', '0'),
            ('prdetw', '1'),
            ('prdetl', ''),
            ('pagewidcl', 'p'),
            ('Winheight', '720'),
            ('pagelensaved', '34'),
            ('maxrow', '3000'),
            ('range', '1'),
            ('sortdet2', ''),
            ('subc', '1111111111111111111111'),
            ('pagelen', '34'),
            ('pagedest', '1'),
            ('sortkeyl', ''))

        query_data = '&'.join(["%s=%s" % (field, value)
                               for field, value in query_data_list])

        # run word query
        try:
            request = urllib2.Request(self.query_url)
            request.add_data(query_data)
            response = urllib2.urlopen(request)
            response_html = response.read()
        except Exception, err:
            raise WSError("Can't query SCN (%s): %s" %
                          (self.query_url, str(err)))

        # parse result page URL
        matches = re.findall("""<FRAME name=headFrm src="([^"]*)">""",
                             response_html)
        if not matches:
            if "Please log in again" in response_html:
                raise WSLoginError("Login timeout", response_html)
            else:
                raise WSError("Can't get result page URL", response_html)

        result_url = "%s%s" % (self.base_url, matches[0])

        # get result page
        request = urllib2.Request(result_url)
        response = urllib2.urlopen(request)
        response_html = response.read()

        # parse results
        re_txt = "<b>hit count&nbsp;</b>[^0-9]*([0-9]+) \( ([0-9.]+) / 1M \)"
        matches = re.findall(re_txt, response_html)
        if not matches:
            raise WSError("Error: Can't get results", response_html)
        hit_count, per_million = matches[0]

        return (word, hit_count, per_million)

class BNC (WordStatsQuery):
    """
    Query the BNC site
    """

    query_url = "http://bncweb.lancs.ac.uk/cgi-binbncXML/processQuery.pl"

    def query(self, word):
        """
        Query word, and return frequency.
        Returns: (word, hit_count, per_million)
        """

        query_data_list = (
            ('theData', word),
            ('chunk', '1'),
            ('queryType', 'CQL'),
            ('qMode', 'Simple+query+%28ignore+case%29'),
            ('inst', 'count+hits'),
            ('max', 'INIT'),
            ('qname', 'INIT'),
            ('thMode', 'INIT'),
            ('thin', '0'),
            ('qtype', '0'),
            ('view', 'list'),
            ('theAction', 'Start+Query'),
            ('urlTest', 'yes'))

        query_data = '&'.join(["%s=%s" % (field, value)
                               for field, value in query_data_list])

        final_url = "%s?%s" % (self.query_url, query_data)

        # run word query
        try:
            request = urllib2.Request(final_url)
            base64string = base64.encodestring('%s:%s' %
                                               (self.user,
                                                self.password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)
            response = urllib2.urlopen(request)
            response_html = response.read()
        except Exception, err:
            if "Authorization Required" in str(err):
                raise WSLoginError("Couldn't login to BNC. Bad user/password",
                                   str(err))
            else:
                raise WSError("Can't query BNC (%s): %s" %
                              (self.query_url, str(err)))

        # parse results
        if "There are no matches for your query" in response_html:
            hit_count   = '0'
            per_million = '0'
        else:
            re_txt = "returned ([0-9]+) hit.* frequency: ([0-9.]+) instances per million"
            matches = re.findall(re_txt, response_html)
            if not matches:
                raise WSError("Error: Can't get results", response_html)
            hit_count, per_million = matches[0]

        return (word, hit_count, per_million)
