"""
A python client for the Freesound API.

Find the API documentation at http://www.freesound.org/docs/api/.

Apply for an API key at http://www.freesound.org/api/apply/.

The client automatically maps function arguments to http parameters of the API. JSON results are converted to python objects. The main object types (Sound, User, Pack) are augmented with the corresponding API calls.

Note that POST resources are not supported. Downloading full quality sounds requires Oauth2 authentication (see http://freesound.org/docs/api/authentication.html). Oauth2 authentication is supported, but you are expected to implement the workflow.
"""

import re
import json
import ssl
from os.path import join
from collections import namedtuple
import requests
from urllib.request import urlopen, Request
from urllib.parse import urlparse, urlencode, quote, parse_qs
from urllib.error import HTTPError

class URIS():
    HOST = 'freesound.org'
    BASE =  'https://'+HOST+'/apiv2'
    TEXT_SEARCH = '/search/text/'
    CONTENT_SEARCH= '/search/content/'
    COMBINED_SEARCH = '/search/combined/'
    SOUND = '/sounds/<sound_id>/'
    SOUND_ANALYSIS = '/sounds/<sound_id>/analysis/'
    SIMILAR_SOUNDS = '/sounds/<sound_id>/similar/'
    COMMENTS = '/sounds/<sound_id>/comments/'
    DOWNLOAD = '/sounds/<sound_id>/download/'
    UPLOAD = '/sounds/upload/'
    DESCRIBE = '/sounds/<sound_id>/describe/'
    PENDING = '/sounds/pending_uploads/'
    BOOKMARK = '/sounds/<sound_id>/bookmark/'
    RATE = '/sounds/<sound_id>/rate/'
    COMMENT = '/sounds/<sound_id>/comment/'
    AUTHORIZE = '/oauth2/authorize/'
    LOGOUT = '/api-auth/logout/'
    LOGOUT_AUTHORIZE = '/oauth2/logout_and_authorize/'
    ME = '/me/'
    USER = '/users/<username>/'
    USER_SOUNDS = '/users/<username>/sounds/'
    USER_PACKS = '/users/<username>/packs/'
    USER_BOOKMARK_CATEGORIES = '/users/<username>/bookmark_categories/'
    USER_BOOKMARK_CATEGORY_SOUNDS = '/users/<username>/bookmark_categories/<category_id>/sounds/'
    PACK = '/packs/<pack_id>/'
    PACK_SOUNDS = '/packs/<pack_id>/sounds/'
    PACK_DOWNLOAD = '/packs/<pack_id>/download/'

    @classmethod
    def uri(cls, uri, *args):
        for a in args:
            uri = re.sub('<[\w_]+>', quote(str(a)), uri, 1)
        return cls.BASE+uri

class FreesoundClient():
    """
    Start here, create a FreesoundClient and set an authentication token 
    using set_token

    >>> c = FreesoundClient()

    >>> c.set_token("<your_api_key>")

    """
    client_secret = ""
    client_id = ""
    token = ""
    header =""

    def check_access(self):
        uri = URIS.uri(URIS.SOUND,6)
        request = FSRequest.request(uri, {}, self, Sound)
        if hasattr(request, 'code'):
            return False
        else:
            return True

    def get_sound(self, sound_id):
        """
        Get a sound object by id
        http://freesound.org/docs/api/resources_apiv2.html#sound-resources

        >>> sound = c.get_sound(6)
        """
        uri = URIS.uri(URIS.SOUND,sound_id)
        return FSRequest.request(uri, {}, self, Sound)

    def text_search(self, **params):
        """
        Search sounds using a text query and/or filter. Returns an iterable 
        Pager object. The fields parameter allows you to specify the information 
        you want in the results list
        http://freesound.org/docs/api/resources_apiv2.html#text-search

        >>> sounds = c.text_search(query="dubstep", filter="tag:loop", fields="id,name,url")
        >>> for snd in sounds: print snd.name
        """
        uri = URIS.uri(URIS.TEXT_SEARCH)
        return FSRequest.request(uri, params, self, Pager)

    def content_based_search(self, **params):
        """
        Search sounds using a content-based descriptor target and/or filter
        See essentia_example.py for an example using essentia
        http://freesound.org/docs/api/resources_apiv2.html#content-search

        >>> sounds = c.content_based_search(target="lowlevel.pitch.mean:220",descriptors_filter="lowlevel.pitch_instantaneous_confidence.mean:[0.8 TO 1]",fields="id,name,url")
        >>> for snd in sounds: print snd.name
        """
        uri = URIS.uri(URIS.CONTENT_SEARCH)
        return FSRequest.request(uri, params, self, Pager)

    def combined_search(self, **params):
        """
        Combine both text and content-based queries.
        http://freesound.org/docs/api/resources_apiv2.html#combined-search

        >>> sounds = c.combined_search(target="lowlevel.pitch.mean:220", filter="single-note")
        """
        uri = URIS.uri(URIS.COMBINED_SEARCH)
        return FSRequest.request(uri,params,self,CombinedSearchPager)

    def get_user(self,username):
        """
        Get a user object by username
        http://freesound.org/docs/api/resources_apiv2.html#combined-search

        >>> u=c.get_user("xserra")
        """
        uri = URIS.uri(URIS.USER, username)
        return FSRequest.request(uri,{},self,User)

    def get_pack(self,pack_id):
        """
        Get a user object by username
        http://freesound.org/docs/api/resources_apiv2.html#combined-search

        >>> p = c.get_pack(3416)
        """
        uri = URIS.uri(URIS.PACK, pack_id)
        return FSRequest.request(uri,{},self,Pack)

    def set_token(self, token, auth_type="token"):
        """
        Set your API key or Oauth2 token
        http://freesound.org/docs/api/authentication.html
        http://freesound.org/docs/api/resources_apiv2.html#combined-search

        >>> c.set_token("<your_api_key>")
        """
        self.token = token#TODO
        self.header = 'Bearer '+token if auth_type=='oauth' else 'Token '+token


class FreesoundObject:
    """
    Base object, automatically populated from parsed json dictionary
    """
    def __init__(self,json_dict, client):
        self.client=client
        def replace_dashes(d):
            for k, v in list(d.items()):
                if "-" in k:
                    d[k.replace("-","_")] = d[k]
                    del d[k]
                if isinstance(v, dict):replace_dashes(v)

        replace_dashes(json_dict)
        self.__dict__.update(json_dict)
        for k, v in json_dict.items():
            if isinstance(v, dict):
                self.__dict__[k] = FreesoundObject(v, client)

class FreesoundException(Exception):
    """
    Freesound API exception
    """
    def __init__(self, http_code, detail):
        self.code = http_code
        self.detail = detail
    def __str__(self):
        return '<FreesoundException: code=%s, detail="%s">' % \
                (self.code,  self.detail)

class FSRequest:
    """
    Makes requests to the freesound API. Should not be used directly.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    @classmethod
    def request(cls, uri, params={}, client=None, wrapper=FreesoundObject, 
                method='GET', data=False):
        p = params if params else {}
        url = '%s?%s' % (uri, urlencode(p)) if params else uri
        d = urllib.urlencode(data) if data else None
        headers = {'Authorization':client.header}
        req = Request(url,d,headers)
        try:
            f = urlopen(req, context=cls.ctx)
        except HTTPError as e:
            resp = e.read()
            if e.code >= 200 and e.code < 300:
                return resp
            else:
                return FreesoundException(e.code, 
                                          json.loads(resp.decode("utf-8")))
        resp = f.read()
        f.close()
        result = None
        try:
            result = json.loads(resp.decode("utf-8"))
        except:
            raise FreesoundException(0,"Couldn't parse response")
        if wrapper:
            return wrapper(result,client)
        return result

    @classmethod
    def retrieve(cls, url, client, path):
        r = requests.get(url)
        with open (path, 'wb') as audiofile:
            audiofile.write(r.content)
        return path

class Pager(FreesoundObject):
    """
    Paginates search results. Can be used in for loops to iterate its results array.
    """
    def __getitem__(self, key):
        return Sound(self.results[key], self.client)

    def next_page(self):
        """
        Get a Pager with the next results page.
        """
        return FSRequest.request(self.next, {}, self.client, Pager)

    def previous_page(self):
        """
        Get a Pager with the previous results page.
        """
        return FSRequest.request(self.previous, {}, self.client, Pager)
    def get_page(self, n):
        url = self.next
        
        uri = urlparse(url)
        for index,item in enumerate(uri):
            if ('query' in item):
                urid=index

        query = uri[urid].split("&")

        for index,item in enumerate(query):
            if ("page" in item):
                query[index] = 'page=' + str(n)

        url = uri[0] + '://' + uri[1] + uri[2] + '?' + "&".join(query)
        return FSRequest.request(url, {}, self.client, Pager)

class GenericPager(Pager):
    """
    Paginates results for objects different than Sound.
    """
    def __getitem__(self, key):
        return FreesoundObject(self.results[key],self.client)

class CombinedSearchPager(FreesoundObject):
    """
    Combined search uses a different pagination style.
    The total amount of results is not available, and the size of the page is not guaranteed.
    Use :py:meth:`~freesound.CombinedSearchPager.more` to get more results if available.
    """
    def __getitem__(self, key):
        return Sound(self.results[key], None)

    def more(self):
        """
        Get more results
        """
        return FSRequest.request(self.more, {}, self.client, CombinedSearchPager)

class Sound(FreesoundObject):
    """
    Freesound Sound resources

    >>> sound = c.get_sound(6)
    """
    def retrieve(self, directory, name=False):
        """
        Download the original sound file (requires Oauth2 authentication).
        http://freesound.org/docs/api/resources_apiv2.html#download-sound-oauth2-required

         >>> sound.retrieve("/tmp")
        """
        path = join(directory, name if name else self.name)
        uri = URIS.uri(URIS.DOWNLOAD, self.id)
        return FSRequest.retrieve(uri, self.client,path)

    def retrieve_preview(self, directory, name=False, quality=False):
        """
        Download the high quality mp3 preview.

        >>> sound.retrieve_preview("/tmp")
        """
        if (not quality):
            path = join(directory, name if name else str(self.previews.preview_lq_mp3.split("/")[-1]))
            return FSRequest.retrieve(self.previews.preview_lq_mp3, self.client,path)
        else:
            path = join(directory, name if name else str(self.previews.preview_hq_mp3.split("/")[-1]))
            return FSRequest.retrieve(self.previews.preview_hq_mp3, self.client,path)

    def get_analysis(self, descriptors=None):
        """
        Get content-based descriptors.
        http://freesound.org/docs/api/resources_apiv2.html#sound-analysis

        >>> a = sound.get_analysis(descriptors="lowlevel.pitch.mean")
        >>> print(a.lowlevel.pitch.mean)
        """
        uri = URIS.uri(URIS.SOUND_ANALYSIS,self.id)
        params = {}
        if descriptors:
            params['descriptors']=descriptors
        return FSRequest.request(uri, params,self.client,FreesoundObject)

    def get_similar(self):
        """
        Get similar sounds based on content-based descriptors.
        http://freesound.org/docs/api/resources_apiv2.html#similar-sounds

        >>> s = sound.get_similar()
        """
        uri = URIS.uri(URIS.SIMILAR_SOUNDS,self.id)
        return FSRequest.request(uri, {},self.client, Pager)

    def get_comments(self):
        """
        Get user comments.
        http://freesound.org/docs/api/resources_apiv2.html#sound-comments

        >>> comments = sound.get_comments()
        """
        uri = URIS.uri(URIS.COMMENTS,self.id)
        return FSRequest.request(uri, {}, self.client, GenericPager)

    def __repr__(self):
        return '<Sound: id="%s", name="%s">' % \
                (self.id, self.name)

class User(FreesoundObject):
    """
    Freesound User resources.

    >>> u=c.get_user("xserra")
    """
    def get_sounds(self):
        """
        Get user sounds.
        http://freesound.org/docs/api/resources_apiv2.html#user-sounds

        >>> u.get_sounds()
        """
        uri = URIS.uri(URIS.USER_SOUNDS,self.username)
        return FSRequest.request(uri, {}, self.client, Pager)

    def get_packs(self):
        """
        Get user packs.
        http://freesound.org/docs/api/resources_apiv2.html#user-packs

        >>> u.get_packs()
        """
        uri = URIS.uri(URIS.USER_PACKS,self.username)
        return FSRequest.request(uri, {}, self.client, GenericPager)

    def get_bookmark_categories(self):
        """
        Get user bookmark categories.
        http://freesound.org/docs/api/resources_apiv2.html#user-bookmark-categories

        >>> u.get_bookmark_categories()
        """
        uri = URIS.uri(URIS.USER_BOOKMARK_CATEGORIES,self.username)
        return FSRequest.request(uri, {}, self.client, GenericPager)

    def get_bookmark_category_sounds(self, category_id):
        """
        Get user bookmarks.
        http://freesound.org/docs/api/resources_apiv2.html#user-bookmark-category-sounds

        >>> p=u.get_bookmark_category_sounds(0)
        """
        uri = URIS.uri(URIS.USER_BOOKMARK_CATEGORY_SOUNDS,self.username,category_id)
        return FSRequest.request(uri, {}, self.client, Pager)

    def __repr__(self): return '<User: "%s">' % ( self.username)

class Pack(FreesoundObject):
    """
    Freesound Pack resources.

    >>> p = c.get_pack(3416)
    """
    def get_sounds(self):
        """
        Get pack sounds
        http://freesound.org/docs/api/resources_apiv2.html#pack-sounds

        >>> sounds = p.get_sounds()
        """
        uri = URIS.uri(URIS.PACK_SOUNDS,self.id)
        return FSRequest.request(uri, {}, self.client, Pager)

    def __repr__(self):
        return '<Pack:  name="%s">' % ( self.name)

