import time
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from spoiler.articles import ArticleError, public_target, fetch_article


class PublicArticleTests(unittest.TestCase):
    def test_publisher_denial_is_distinct_from_local_connection_failure(self):
        response = SimpleNamespace(status=403, getheader=lambda *args: None)
        connection = SimpleNamespace(
            sock=SimpleNamespace(shutdown=lambda *args: None), connect=lambda: None,
            request=lambda *args, **kwargs: None, getresponse=lambda: response, close=lambda: None)
        with patch('spoiler.articles.public_target',return_value=('https','example.com',443,'/blocked','93.184.216.34','https://example.com/blocked')), \
             patch('spoiler.articles.PinnedHTTPS',return_value=connection):
            with self.assertRaises(ArticleError) as failure:
                fetch_article('https://example.com/blocked')
        self.assertEqual(failure.exception.code, 'publisher_http_error')
        self.assertEqual(failure.exception.publisher_status, 403)
        self.assertIn('local server is connected', str(failure.exception))

    def test_rejects_local_and_non_http_destinations(self):
        for url in ['file:///etc/passwd','http://127.0.0.1/a','http://localhost/a',
                    'http://169.254.169.254/latest','http://[::1]/a','http://10.0.0.1/a',
                    'https://user:password@example.com/a','https://example.com:8443/a']:
            with self.subTest(url=url), self.assertRaises(ArticleError):
                public_target(url,time.monotonic()+5)

    def test_dns_is_validated_and_address_returned_for_pinning(self):
        with patch('socket.getaddrinfo',return_value=[(2,1,6,'',('93.184.216.34',443))]):
            scheme,host,port,path,address,url=public_target('https://example.com/article?q=1#part',time.monotonic()+5)
        self.assertEqual((host,address,path),('example.com','93.184.216.34','/article?q=1'))
        self.assertEqual(url,'https://example.com/article?q=1')

    def test_mixed_public_private_dns_is_rejected(self):
        with patch('socket.getaddrinfo',return_value=[(2,1,6,'',('93.184.216.34',443)),(2,1,6,'',('192.168.0.1',443))]):
            with self.assertRaises(ArticleError):public_target('https://example.com',time.monotonic()+5)

    def test_redirect_to_private_network_is_rejected_before_connect(self):
        class Redirect:
            status=302
            def getheader(self,name,default=None):return 'http://127.0.0.1/private' if name=='Location' else default
        class Socket:
            def shutdown(self,*args):pass
        class Connection:
            connections=[]
            def __init__(self,host,*args):self.connections.append(host);self.sock=Socket()
            def connect(self):pass
            def request(self,*args,**kwargs):pass
            def getresponse(self):return Redirect()
            def close(self):pass
        def resolve(host,*args):return [(2,1,6,'',('127.0.0.1' if host=='127.0.0.1' else '93.184.216.34',443))]
        with patch('socket.getaddrinfo',side_effect=resolve),patch('spoiler.articles.PinnedHTTPS',Connection):
            with self.assertRaises(ArticleError):fetch_article('https://example.com/redirect')
        self.assertEqual(Connection.connections,['example.com'])
