"""Public-only article retrieval with pinned DNS, bounded redirects/body/time.

No cookies, JavaScript, proxy environment variables, or article subresources.
"""
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
import hashlib
import http.client
import ipaddress
import socket
import ssl
import threading
import time
from urllib.parse import urljoin, urlsplit, urlunsplit

MAX_BYTES = 2_000_000
DEADLINE_SECONDS = 20
DNS_POOL = ThreadPoolExecutor(max_workers=4)
FETCH_SLOTS = threading.BoundedSemaphore(4)
CACHE = {}
CACHE_LOCK = threading.Lock()


class ArticleError(ValueError):
    def __init__(self, message, code='article_unavailable', publisher_status=None):
        super().__init__(message)
        self.code = code
        self.publisher_status = publisher_status


def public_target(url, deadline):
    if not isinstance(url, str) or len(url) > 4000 or any(ord(c) < 33 for c in url):
        raise ArticleError('Use a valid public HTTP(S) article URL')
    try:
        parsed = urlsplit(url)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError()
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        if port != (443 if parsed.scheme == 'https' else 80):
            raise ValueError()
        host = parsed.hostname.encode('idna').decode('ascii')
    except (ValueError, UnicodeError):
        raise ArticleError('Only public HTTP(S) article URLs on standard ports are supported')
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise ArticleError('Article fetch timed out')
    future = DNS_POOL.submit(socket.getaddrinfo, host, port, 0, socket.SOCK_STREAM)
    try:
        addresses = future.result(timeout=min(5, remaining))
    except (FutureTimeout, OSError):
        future.cancel()
        raise ArticleError('Article hostname could not be resolved in time')
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise ArticleError('Private, local, reserved, or mixed public/private destinations are blocked')
    path = urlunsplit(('', '', parsed.path or '/', parsed.query, ''))
    canonical = urlunsplit((parsed.scheme, host, parsed.path or '/', parsed.query, ''))
    return parsed.scheme, host, port, path, addresses[0][4][0], canonical


class PinnedHTTP(http.client.HTTPConnection):
    def __init__(self, host, port, address, timeout):
        super().__init__(host, port, timeout=timeout)
        self.address = address

    def connect(self):
        self.sock = socket.create_connection((self.address, self.port), self.timeout)


class PinnedHTTPS(PinnedHTTP):
    def connect(self):
        super().connect()
        try:
            self.sock = ssl.create_default_context().wrap_socket(self.sock, server_hostname=self.host)
        except Exception:
            self.sock.close()
            raise


def fetch_article(url):
    started = time.perf_counter()
    # An already-fetched exact URL can be reused without DNS/network, including offline.
    if isinstance(url, str):
        with CACHE_LOCK:
            cached = CACHE.get(url)
            if cached and time.time()-cached['cached_at'] < 1800:
                return dict(cached['article'],fetch_cache_hit=True,fetch_ms=round((time.perf_counter()-started)*1000,2))
    # URL validation is repeated for redirects; socket connects to the validated IP,
    # while TLS SNI/certificate validation and HTTP Host use the original hostname.
    deadline = time.monotonic() + DEADLINE_SECONDS
    if not FETCH_SLOTS.acquire(blocking=False):
        raise ArticleError('Too many article fetches; try again shortly')
    try:
        original = url
        for redirect in range(4):
            scheme, host, port, path, address, canonical = public_target(url, deadline)
            with CACHE_LOCK:
                cached = CACHE.get(canonical)
                if cached and time.time() - cached['cached_at'] < 1800:
                    return dict(cached['article'], fetch_cache_hit=True,
                                fetch_ms=round((time.perf_counter()-started)*1000, 2))
            timeout = max(.1, min(8, deadline-time.monotonic()))
            connection = (PinnedHTTPS if scheme == 'https' else PinnedHTTP)(host, port, address, timeout)
            timer = None
            try:
                connection.connect()
                connected_socket = connection.sock
                def expire(sock=connected_socket):
                    try: sock.shutdown(socket.SHUT_RDWR)
                    except OSError: pass
                timer = threading.Timer(max(.01, deadline-time.monotonic()), expire)
                timer.daemon = True
                timer.start()
                connection.request('GET', path, headers={'Host': host, 'User-Agent':'GetToThePoint/0.2 (local article reader)',
                                                        'Accept':'text/html,application/xhtml+xml', 'Accept-Encoding':'identity'})
                response = connection.getresponse()
                if response.status in (301,302,303,307,308):
                    location = response.getheader('Location')
                    if not location or redirect == 3:
                        raise ArticleError('Article redirected too many times')
                    url = urljoin(canonical, location)
                    continue
                if response.status != 200:
                    raise ArticleError(
                        'The publisher refused the article fetch (HTTP %s). '
                        'The local server is connected. Open the source normally; '
                        'if the article is readable, use the extension’s Read this open article button.' % response.status,
                        code='publisher_http_error', publisher_status=response.status)
                content_type = response.getheader('Content-Type','').lower()
                if not any(t in content_type for t in ('text/html','application/xhtml+xml')):
                    raise ArticleError('This link is not an HTML article')
                if response.getheader('Content-Encoding','identity').lower() not in ('identity',''):
                    raise ArticleError('Publisher sent an unsupported compressed response')
                length = response.getheader('Content-Length')
                if length and int(length) > MAX_BYTES:
                    raise ArticleError('Article exceeds the 2 MB download limit')
                chunks = []; total = 0
                while True:
                    remaining = deadline-time.monotonic()
                    if remaining <= 0:
                        raise ArticleError('Article fetch timed out')
                    if connection.sock:
                        connection.sock.settimeout(min(5,remaining))
                    chunk = response.read1(min(65536, MAX_BYTES-total+1))
                    if not chunk: break
                    total += len(chunk)
                    if total > MAX_BYTES:
                        raise ArticleError('Article exceeds the 2 MB download limit')
                    chunks.append(chunk)
                if time.monotonic() >= deadline:
                    raise ArticleError('Article fetch timed out')
                if length and total < int(length):
                    raise ArticleError('Publisher closed the connection before the article finished downloading')
                html = b''.join(chunks)
            except (socket.timeout, TimeoutError, OSError, http.client.HTTPException) as error:
                raise ArticleError('Could not retrieve this article: '+str(error))
            finally:
                if timer: timer.cancel()
                connection.close()
            try:
                import trafilatura
            except ImportError:
                raise ArticleError('Install article dependencies: .venv/bin/pip install -r requirements.txt')
            extracted = trafilatura.bare_extraction(html, url=canonical, include_comments=False,
                                                   include_tables=False, favor_precision=True, with_metadata=True, as_dict=True)
            article = (extracted or {}).get('text','').strip()
            if len(article) < 120:
                raise ArticleError('No readable article found. This publisher may require JavaScript or block automated access.')
            result = {'article':article,'article_title':extracted.get('title') or host,
                      'source_url':canonical,'requested_url':original,'download_bytes':total,
                      'article_sha256':hashlib.sha256(article.encode()).hexdigest(),
                      'fetched_at':time.time(),'fetch_ms':round((time.perf_counter()-started)*1000,2),'fetch_cache_hit':False}
            with CACHE_LOCK:
                if len(CACHE) >= 50: CACHE.pop(next(iter(CACHE)))
                CACHE[canonical] = {'cached_at':time.time(),'article':result}
                if original != canonical:
                    CACHE[original] = CACHE[canonical]
            return result
        raise ArticleError('Could not retrieve article')
    finally:
        FETCH_SLOTS.release()
