class NoCache(object):
    """
    This never caches anything.
    """
    def getCache(self, service, url, headers):
        return None

    def processResponse(self, service, url, response):
        pass
