# -*- coding: utf-8 -*-
from urllib.parse import urlparse, parse_qs, unquote, quote_plus, urlencode
try:
    from lib.client import cfscraper
except ImportError:
    from client import cfscraper
try:
    from lib.helper import *
except ImportError:
    from helper import *
import re
try:
    from lib import jsunpack
except ImportError:
    import jsunpack
try:
    from lib import tear
except ImportError:
    import tear
import socket
import requests
from bs4 import BeautifulSoup
import base64
import json

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'

class DNSResolver:
    def __init__(self, dns_server='1.1.1.1'):
        self.etc_hosts = {}
        self.cache_resolve_dns = {}
        self.DNS_SERVER = dns_server


    def resolver(self, builtin_resolver):
        def wrapper(*args, **kwargs):
            try:
                # Tentar resolver com o cache personalizado
                return self.etc_hosts[args[:2]]
            except KeyError:
                # Resolver com o comportamento padrão
                return builtin_resolver(*args, **kwargs)
        return wrapper

    def dns_query_custom(self, hostname):
        query = b'\xaa\xbb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' + \
                b''.join(bytes([len(part)]) + part.encode() for part in hostname.split('.')) + \
                b'\x00\x00\x01\x00\x01'
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.sendto(query, (self.DNS_SERVER, 53))
        response, _ = sock.recvfrom(512)
        sock.close()
        ip_start = response.find(b'\xc0') + 12
        ip_bytes = response[ip_start:ip_start + 4]
        ip_address = '.'.join(map(str, ip_bytes))
        return ip_address

    def _change_dns(self, domain_name, port, ip):
        key = (domain_name, port)
        value = (socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, port))
        self.etc_hosts[key] = [value]

    def change(self, url):
        socket.getaddrinfo = self.resolver(socket.getaddrinfo)
        parsed_url = urlparse(url)
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        host = parsed_url.hostname
        try:
            ip_address = self.cache_resolve_dns[host]
        except:
            try:
                ip_address = self.dns_query_custom(host)
            except:
                ip_address = '127.0.0.1'
            self.cache_resolve_dns[host] = ip_address
            
        self._change_dns(host, port, ip_address)

dnsresolver_ = DNSResolver()    


class VOD1:
    def __init__(self,url):
        self.headers = {'User-Agent': USER_AGENT}
        self.base = self.get_last_base(url)
        #self.base = url

    def get_last_base(self, url):
        host_base = url
        last_url = ''
        try:
            dnsresolver_.change(url)
            r = requests.get(host_base,headers=self.headers,timeout=4)
            last_url = r.url
        except:
            pass     

        if last_url and last_url.endswith('/'):
            last_url = last_url[:-1]
        return last_url        

    def soup(self,src):
        soup = BeautifulSoup(src,'html.parser')
        return soup
    
    def get_packed_data(self,html):
        packed_data = ''
        try:
            for match in re.finditer(r'''(eval\s*\(function\(p,a,c,k,e,.*?)</script>''', html, re.DOTALL | re.I):
                r = match.group(1)
                t = re.findall(r'(eval\s*\(function\(p,a,c,k,e,)', r, re.DOTALL | re.IGNORECASE)
                if len(t) == 1:
                    if jsunpack.detect(r):
                        packed_data += jsunpack.unpack(r)
                else:
                    t = r.split('eval')
                    t = ['eval' + x for x in t if x]
                    for r in t:
                        if jsunpack.detect(r):
                            packed_data += jsunpack.unpack(r)
        except:
            pass
        return packed_data

    def pesquisa_filmes(self,url,pesquisa):
        itens_pesquisa = []
        next_page = False
        page = ''
        if pesquisa:
            url = '%s/?s=%s'%(self.base,quote_plus(pesquisa))           
        try:
            headers = {'User-Agent': USER_AGENT}
            headers.update({'Cookie': 'XCRF%3DXCRF'})
            dnsresolver_.change(url)
            r = requests.get(url,headers=headers)
            src = r.text
            soup = self.soup(src)
            box = soup.find("div", {"id": "box_movies"})
            movies = box.findAll("div", {"class": "movie"})
            for i in movies:
                name = i.find('h2').text
                try:
                    name = name.decode('utf-8')
                except:
                    pass
                try:
                    year = i.find('span', {'class': 'year'}).text
                    year = year.replace('–', '')
                except:
                    year = ''
                img = i.find('div', {'class': 'imagen'})
                iconimage = img.find('img').get('src', '')
                iconimage = iconimage.replace('-120x170', '')
                link = img.find('a').get('href', '')
                if '/tvshows/' in link:
                    name = '%s (Série)'%name
                else:
                    if 'hdcam' in link and not 'hdcam' in name.lower():
                        name = '%s (Filme) (HDCAM)'%name
                    else:
                        name = '%s (Filme)'%name
                if year:
                    name = '[B]%s (%s)[/B]'%(name,str(year))
                else:
                    name = '[B]%s[/B]'%name                
                itens_pesquisa.append((name,iconimage,link))
            try:
                div = soup.find('div', {'id': 'paginador'}).find('div', {'class': 'paginado'})
                current = div.find('span', {'class': 'current'}).text
                a = div.findAll('a')
                for i in a:
                    href = i.get('href', '')
                    nxt = str(int(current) + 1)
                    if nxt in href:
                        next_page = href
                        try:
                            page_ = next_page.split('page/')[1]
                            try:
                                page = page_.split('/')[0]
                            except:
                                page = page_
                        except:
                            pass
                        break

            except:
                pass
        except:
            pass
        return itens_pesquisa, next_page, page 

    def scraper_filmes(self, url=''):
        if not url:
            url = self.base + '/category/ultimos-filmes/'
        filmes = []
        next_page = False
        page = ''
        try:
            headers = {'User-Agent': USER_AGENT}
            headers.update({'Cookie': 'XCRF%3DXCRF'})
            dnsresolver_.change(url)
            r = requests.get(url,headers=headers)
            src = r.text
            soup = self.soup(src)
            box = soup.find("div", {"id": "box_movies"})
            movies = box.findAll("div", {"class": "movie"})
            for i in movies:
                name = i.find('h2').text
                img = i.find('div', {'class': 'imagen'})
                iconimage = img.find('img').get('src', '')
                iconimage = iconimage.replace('-120x170', '')
                link = img.find('a').get('href', '')                
                try:
                    name = name.decode('utf-8')
                except:
                    pass
                try:
                    year = i.find('span', {'class': 'year'}).text
                    year = year.replace('–', '')
                except:
                    year = ''
                if year:
                    if 'hdcam' in link and not 'hdcam' in name.lower():
                        name = '[B]%s (%s) (HDCAM)[/B]'%(name,str(year))
                    else:
                        name = '[B]%s (%s)[/B]'%(name,str(year))
                else:
                    if 'hdcam' in link and not 'hdcam' in name.lower():
                        name = '[B]%s (HDCAM)[/B]'%name
                    else:
                        name = '[B]%s[/B]'%name
                filmes.append((name,iconimage,link))
            try:
                div = soup.find('div', {'id': 'paginador'}).find('div', {'class': 'paginado'})
                current = div.find('span', {'class': 'current'}).text
                a = div.findAll('a')
                for i in a:
                    href = i.get('href', '')
                    nxt = str(int(current) + 1)
                    if nxt in href:
                        next_page = href
                        try:
                            page_ = next_page.split('page/')[1]
                            try:
                                page = page_.split('/')[0]
                            except:
                                page = page_
                        except:
                            pass
                        break

            except:
                pass
        except:
            pass
        return filmes, next_page, page

    def opcoes_filmes(self,url):
        opcoes = []      
        try:
            headers = {'User-Agent': USER_AGENT}
            headers.update({'Cookie': 'XCRF%3DXCRF'})
            dnsresolver_.change(url)
            r = requests.get(url,headers=headers)
            src = r.text
            soup = self.soup(src)
            player = soup.find('div', {'id': 'player-container'})
            botoes = player.find('ul', {'class': 'player-menu'})
            op = botoes.findAll('li')
            op_list = []
            if op:
                for i in op:
                    a = i.find('a')
                    id_ = a.get('href', '').replace('#', '')
                    op_name = a.text
                    try:
                        op_name = op_name.decode('utf-8')
                    except:
                        pass
                    op_name = op_name.replace(' 1', '').replace(' 2', '').replace(' 3', '').replace(' 4', '').replace(' 5', '')
                    op_name = op_name.strip()
                    op_name = op_name.upper()
                    op_list.append((op_name,id_))
            if op_list:
                for name, id_ in op_list:
                    iframe = player.find('div', {'class': 'play-c'}).find('div', {'id': id_}).find('iframe').get('src', '')
                    if not 'streamtape' in iframe:
                        link = self.base + '/' + iframe
                    else:
                        link = iframe
                    opcoes.append((name,link))

        except:
            pass
        return opcoes

    def scraper_series(self, url=''):
        if not url:
            url = self.base + '/tvshows/'          
        series = []
        next_page = False
        page = ''
        try:
            headers = {'User-Agent': USER_AGENT}
            headers.update({'Cookie': 'XCRF%3DXCRF'})
            dnsresolver_.change(url)
            r = requests.get(url,headers=headers)
            src = r.text
            soup = self.soup(src)
            box = soup.find("div", {"id": "box_movies"})
            movies = box.findAll("div", {"class": "movie"})
            for i in movies:
                name = i.find('h2').text
                try:
                    name = name.decode('utf-8')
                except:
                    pass
                try:
                    year = i.find('span', {'class': 'year'}).text
                    year = year.replace('–', '')
                except:
                    year = ''
                if year:
                    name = '[B]%s (%s)[/B]'%(name,str(year))
                else:
                    name = '[B]%s[/B]'%name
                img = i.find('div', {'class': 'imagen'})
                iconimage = img.find('img').get('src', '')
                iconimage = iconimage.replace('-120x170', '')
                link = img.find('a').get('href', '')
                series.append((name,iconimage,link))
            try:
                div = soup.find('div', {'id': 'paginador'}).find('div', {'class': 'paginado'})
                current = div.find('span', {'class': 'current'}).text
                a = div.findAll('a')
                for i in a:
                    href = i.get('href', '')
                    nxt = str(int(current) + 1)
                    if nxt in href:
                        next_page = href
                        try:
                            page_ = next_page.split('page/')[1]
                            try:
                                page = page_.split('/')[0]
                            except:
                                page = page_
                        except:
                            pass
                        break

            except:
                pass
        except:
            pass
        return series, next_page, page

    def scraper_temporadas_series(self,url):
        url_original = url       
        list_seasons = []
        serie_name_final = ''
        img = ''
        fanart = ''        
        try:
            headers = {'User-Agent': USER_AGENT}
            headers.update({'Cookie': 'XCRF%3DXCRF'})
            dnsresolver_.change(url)
            r = requests.get(url, headers=headers)
            src = r.text
            soup = self.soup(src)
            # info
            try:
                div_img = soup.find('div', {'id': 'movie'}).find('div', {'class': 'post'}).find('div', {'class': 'headingder'})
                fanart = div_img.find('div', class_=lambda x: x and 'lazyload' in x).get('data-bg', '')
                img = div_img.find('img', {'class': 'lazyload'}).get('data-src', '')
                try:
                    serie_name = div_img.find('div', {'class': 'datos'}).find('div', {'class': 'dataplus'}).find('h1').text
                    try:
                        serie_name = serie_name.decode('utf-8')
                    except:
                        pass
                    serie_name_final = '[B]:::: SÉRIE: %s ::::[/B]'%serie_name
                except:
                    pass
            except:
                pass
            s = soup.find('div', {'id': 'movie'}).find('div', {'class': 'post'}).find('div', {'id': 'cssmenu'}).find('ul').findAll('li', {'class': 'has-sub'})
            for n, i in enumerate(s):
                n += 1
                name = '[B]TEMPORADA %s[/B]'%str(n)
                season = str(n)
                list_seasons.append((season,name,url_original))
        except:
            pass
        return serie_name_final, img, fanart, list_seasons 

    def scraper_episodios_series(self,url,season):
        list_episodes = []
        serie_name_final = ''
        img = ''
        fanart = ''        
        try:
            headers = {'User-Agent': USER_AGENT}
            headers.update({'Cookie': 'XCRF%3DXCRF'})
            dnsresolver_.change(url)
            r = requests.get(url, headers=headers)
            src = r.text
            soup = self.soup(src)
            # info
            try:
                div_img = soup.find('div', {'id': 'movie'}).find('div', {'class': 'post'}).find('div', {'class': 'headingder'})
                fanart = div_img.find('div', class_=lambda x: x and 'lazyload' in x).get('data-bg', '')
                img = div_img.find('img', {'class': 'lazyload'}).get('data-src', '')
                try:
                    serie_name = div_img.find('div', {'class': 'datos'}).find('div', {'class': 'dataplus'}).find('h1').text
                    try:
                        serie_name = serie_name.decode('utf-8')
                    except:
                        pass
                    serie_name_final = '[B]:::: SÉRIE: %s ::::[/B]'%serie_name
                except:
                    pass
            except:
                pass
            s = soup.find('div', {'id': 'movie'}).find('div', {'class': 'post'}).find('div', {'id': 'cssmenu'}).find('ul').findAll('li', {'class': 'has-sub'})
            for n, i in enumerate(s):
                n += 1
                if int(season) == n:
                    e = i.find('ul').findAll('li')
                    for n, i in enumerate(e):
                        n += 1
                        e_info = i.find('a')
                        link = e_info.get('href')
                        ep_name = e_info.find('span', {'class': 'datix'}).text
                        try:
                            ep_name = ep_name.decode('utf-8')
                        except:
                            pass
                        ep_name = ep_name.strip()
                        name_especial = '[B]%s - %s x %s - %s[/B]'%(serie_name,str(season),str(n),ep_name)
                        ep_name2 = '[B]%s - %s[/B]'%(str(n),ep_name)
                        list_episodes.append((ep_name2,name_especial,link))
                    break
        except:
            pass
        return serie_name_final, img, fanart, list_episodes                                  
    


class VOD2:
    def __init__(self, url):
        self.base = self.get_last_base(url)
        self.headers = {
            'User-Agent': USER_AGENT,
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Connection': 'keep-alive'
        }
        self.iframe_headers = {
            **self.headers,
            'sec-fetch-dest': 'iframe'
        }

    def get_last_base(self, url):
        try:
            r = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=5, allow_redirects=True)
            url = r.url
        except:
            pass
        return url.rstrip('/')

    def _strip_subtitle(self, url):
        if '?s=' in url:
            url = url.split('?s=', 1)[0]
        return url.strip()

    def _resolve_video_url(self, session, video_url, referer):
        video_url = self._strip_subtitle(video_url)

        if re.search(r'\.(mp4|m3u8|ts|mpegurl)(\?|#|$)', video_url, re.I):
            try:
                r = requests.head(video_url, headers={'User-Agent': USER_AGENT}, timeout=5, allow_redirects=True)
                if r.status_code >= 400:
                    return ''
            except:
                return ''

            return (
                f"{video_url}"
                f"|User-Agent={quote_plus(USER_AGENT)}"
                f"&Referer={quote_plus(self.base)}"
                f"&Origin={quote_plus(self.base)}"
            )

        try:
            video_hash = video_url.strip('/').split('/')[-1]
            parsed = urlparse(video_url)
            origin = f"{parsed.scheme}://{parsed.netloc}"
            player = f"{origin}/player/index.php?data={video_hash}&do=getVideo"

            r = session.get(video_url, headers={'User-Agent': USER_AGENT}, timeout=15)
            cookies = r.cookies.get_dict()

            r = session.post(
                player,
                headers={
                    'User-Agent': USER_AGENT,
                    'Origin': origin,
                    'Referer': video_url,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                data={'hash': video_hash, 'r': referer},
                cookies=cookies,
                timeout=15
            )

            js = r.json()
            src = js.get('videoSource')
            if not src:
                return ''

            return (
                f"{src}"
                f"|User-Agent={quote_plus(USER_AGENT)}"
                f"&Cookie={quote_plus(urlencode(cookies))}"
                f"&Referer={quote_plus(origin)}"
            )
        except:
            return ''

    def movie(self, imdb):
        try:
            session = cfscraper
            url = f'{self.base}/filme/{imdb}'

            r = session.get(url, headers=self.iframe_headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')

            btns = soup.find_all('div', class_='btn-server')
            ids = [b.get('data-id') for b in btns if b.get('data-id')]
            if not ids:
                return ''

            if len(ids) > 1:
                ids = [ids[1], ids[0]] + ids[2:]

            api = f'{self.base}/api'
            referer = f'{self.base}/'

            for video_id in ids:
                r = session.post(api, data={'action': 'getPlayer', 'video_id': video_id}, headers=self.headers)
                video_url = r.json().get('data', {}).get('video_url', '').strip()
                if not video_url:
                    continue

                resolved = self._resolve_video_url(session, video_url, referer)
                if resolved:
                    return resolved

            return ''
        except:
            return ''

    def tvshows(self, imdb, season, episode):
        try:
            session = cfscraper
            url = f'{self.base}/serie/{imdb}/{season}/{episode}'

            r = session.get(url, headers=self.iframe_headers, timeout=15)
            m = re.search(r'var ALL_EPISODES\s*=\s*({.*?});', r.text, re.DOTALL)
            if not m:
                return ''

            episodes = json.loads(m.group(1))
            contentid = next(
                (ep['ID'] for ep in episodes.get(str(season), [])
                 if str(ep.get('epi_num')) == str(episode)),
                None
            )
            if not contentid:
                return ''

            api = f'{self.base}/api'
            r = session.post(api, data={'action': 'getOptions', 'contentid': contentid}, headers=self.headers)
            options = r.json().get('data', {}).get('options', [])

            ids = [o.get('ID') for o in options if o.get('ID')]
            if len(ids) > 1:
                ids = [ids[1], ids[0]] + ids[2:]

            referer = f'{self.base}/'

            for video_id in ids:
                r = session.post(api, data={'action': 'getPlayer', 'video_id': video_id}, headers=self.headers)
                video_url = r.json().get('data', {}).get('video_url', '').strip()
                if not video_url:
                    continue

                resolved = self._resolve_video_url(session, video_url, referer)
                if resolved:
                    return resolved

            return ''
        except:
            return ''

class VOD3:
    def __init__(self, url):
        self.base = url if url.endswith('/') else url + '/'
        self.headers = {
            'User-Agent': USER_AGENT,
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8',
            'Referer': self.base
        }

    def soup(self, html):
        return BeautifulSoup(html, 'html.parser')

    def _clean_aviso_url(self, url):
        try:
            parsed = urlparse(url)
            if "doramasonline.org/aviso" in url and "url=" in parsed.query:
                qs = parse_qs(parsed.query)
                if "url" in qs:
                    return unquote(qs["url"][0])
        except:
            pass
        return url

    def _decode_holuagency(self, url):
        """
        Ordem correta:
        1. NÃO limpar aviso antes
        2. Decodificar AUTH
        3. Aplicar clean_aviso APÓS o decode
        """

        try:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)

            # Não tem auth → apenas limpa aviso se existir
            if "auth" not in qs:
                return self._clean_aviso_url(url)

            b64data = qs["auth"][0]

            while len(b64data) % 4 != 0:
                b64data += "="

            decoded = base64.b64decode(b64data).decode("utf-8")
            js = json.loads(decoded)

            real = js.get("url")

            if not real:
                return self._clean_aviso_url(url)

            # Aqui sim limpa o aviso corretamente
            real = self._clean_aviso_url(real)

            return real

        except Exception:
            return self._clean_aviso_url(url)

    def scraper_dublados(self, page=1):
        url = f'{self.base}br/generos/dublado/page/{page}/'
        return self._scrape_catalogo(url)

    def scraper_legendados(self, page=1):
        url = f'{self.base}br/generos/legendado/page/{page}/'
        return self._scrape_catalogo(url)

    def scraper_filmes(self, page=1):
        url = f'{self.base}br/filmes/page/{page}/'
        return self._scrape_catalogo(url)

    def search_doramas(self, pesquisa):
        query = quote_plus(pesquisa)
        url = f'{self.base}/?s={query}'
        return self._scrape_busca(url)

    def scraper_episodios(self, url):
        episodios = []

        try:
            r = requests.get(url, headers=self.headers)
            soup = self.soup(r.text)

            serie_name = ''
            try:
                h1 = soup.select_one('div.data h1') or soup.select_one('.data h1')
                if h1 and h1.text:
                    serie_name = h1.text.strip()
            except:
                serie_name = ''

            temporadas = soup.select('div.se-c')

            if temporadas:
                for temporada in temporadas:
                    nome_temp_raw = temporada.select_one('div.se-q span.se-t')
                    temp_txt = nome_temp_raw.text.strip() if nome_temp_raw else ''

                    temp_num = re.findall(r'\d+', temp_txt)
                    season_num = temp_num[0] if temp_num else '1'

                    lista = temporada.select('ul.episodios > li')

                    for idx, li in enumerate(lista, start=1):
                        a = li.select_one('.episodiotitle a')
                        img = li.select_one('.imagen img')

                        if not a:
                            continue

                        num_div = li.select_one('.numerando')
                        ep_num = ''

                        if num_div and num_div.text:
                            nums = re.findall(r'\d+', num_div.text)
                            if len(nums) >= 2:
                                season_num = nums[0]
                                ep_num = nums[1]
                            elif len(nums) == 1:
                                ep_num = nums[0]
                        else:
                            nums = re.findall(r'\d+', a.text)
                            if nums:
                                ep_num = nums[-1]
                            else:
                                ep_num = str(idx)

                        ep_title_text = a.text.strip()

                        if season_num and ep_num:
                            se_part = f"S{season_num}E{ep_num}"
                        else:
                            se_part = f"T{season_num} - Ep{ep_num}".strip()

                        if serie_name:
                            full_title = f"{serie_name} - {se_part}"
                        else:
                            full_title = f"{se_part} - {ep_title_text}"

                        link = a.get('href', '').strip()
                        thumb = img.get('src', '').strip() if img else ''

                        episodios.append((full_title, link, thumb, url))

            else:
                lista = (
                    soup.select('ul.episodios > li')
                    or soup.select('div.episodios li')
                    or soup.find_all('li')
                )

                for li in lista:
                    a = li.select_one('.episodiotitle a') or li.find('a')
                    img = li.select_one('.imagen img')

                    if not a:
                        continue

                    num_div = li.select_one('.numerando')
                    season_num = ''
                    ep_num = ''

                    if num_div and num_div.text:
                        nums = re.findall(r'\d+', num_div.text)
                        if len(nums) >= 2:
                            season_num, ep_num = nums[0], nums[1]
                        elif len(nums) == 1:
                            ep_num = nums[0]

                    if not ep_num:
                        nums = re.findall(r'\d+', a.text)
                        if nums:
                            ep_num = nums[-1]

                    if not season_num:
                        season_num = '1'

                    ep_title_text = a.text.strip()
                    se_part = f"S{season_num}E{ep_num}" if ep_num else f"T{season_num}"

                    if serie_name:
                        full_title = f"{serie_name} - {se_part} - {ep_title_text}"
                    else:
                        full_title = f"{se_part} - {ep_title_text}"

                    link = a.get('href', '').strip()
                    thumb = img.get('src', '').strip() if img else ''

                    episodios.append((full_title, link, thumb, url))

        except Exception as e:
            print('Erro ao extrair episódios:', e)

        return episodios

    def scraper_players(self, url):
        opcoes = []
        try:
            print(f"[scraper_players] Iniciando scrape em: {url}")
            r = requests.get(url, headers=self.headers, timeout=15)
            soup = self.soup(r.text)

            nomes_por_nume = {}
            for li in soup.select('ul#playeroptionsul li.dooplay_player_option'):
                try:
                    nume = (li.get('data-nume') or '').strip()
                    name_el = li.find('span', {'class': 'title'})
                    name = (name_el.text or '').strip() if name_el else f'Opção {nume or "?"}'
                    if nume:
                        nomes_por_nume[nume] = name
                except:
                    continue

            print(f"[scraper_players] Nomes por nume: {nomes_por_nume}")

            for box in soup.select('#dooplay_player_content .source-box'):
                box_id = box.get('id', '')
                m = re.search(r'source-player-(\d+)', box_id or '')
                nume = m.group(1) if m else None

                a = box.find('a', href=True)
                if a and a.get('href'):
                    raw = a['href'].strip()
                    link = self._decode_holuagency(raw)

                    name = nomes_por_nume.get(nume, f'Opção {nume}') if nume else 'Opção'
                    opcoes.append((name, link))
                    print(f"[scraper_players] Fonte {box_id}: Nome='{name}' | Link='{link}'")
                    continue

                iframe = box.find('iframe', src=True)
                if iframe:
                    raw = iframe['src'].strip()
                    link = self._decode_holuagency(raw)

                    name = nomes_por_nume.get(nume, f'Opção {nume}') if nume else 'Opção'
                    opcoes.append((name, link))
                    print(f"[scraper_players] Fonte {box_id} via iframe: Nome='{name}' | Link='{link}'")

            if not opcoes:
                iframes = soup.find_all("iframe", src=True)
                print(f"[scraper_players] Fallback iframes na página: {len(iframes)}")
                for n, iframe in enumerate(iframes, start=1):
                    raw = iframe.get("src", "").strip()
                    link = self._decode_holuagency(raw)

                    name = f"Opção {n}"
                    opcoes.append((name, link))

        except Exception as e:
            print("Erro ao extrair players (novo):", e)

        print(f"[scraper_players] Total de opções extraídas: {len(opcoes)}")
        return opcoes

    def _scrape_catalogo(self, url):
        """
        Scrape para catálogo. Retorna (itens, next_page).
        Detecta paginação por /page/N, .pagination ou .resppages.
        """
        itens = []
        next_page = False
        try:
            r = requests.get(url, headers=self.headers, timeout=15)
            soup = self.soup(r.text)

            container = soup.find("div", class_=lambda x: x and x.startswith("items")) \
                        or soup.find("div", {"id": "box_movies"}) \
                        or soup.find("div", class_="items") \
                        or soup

            artigos = container.find_all("article", id=lambda x: x and x.startswith("post")) \
                      or container.find_all("div", class_="movie-item") \
                      or container.find_all("div", class_="item")

            for art in artigos:
                try:
                    a = art.find("a")
                    href = a.get("href", "") if a else ""
                    title_tag = art.find("h3") or a
                    title = title_tag.text.strip() if title_tag else href
                    img = (art.find("img").get("src", "") if art.find("img") else "")
                    itens.append((title, href, img, title, url))
                except Exception:
                    continue

            paginacao = soup.find("div", class_="pagination") \
                        or soup.find("div", {"id": "paginador"}) \
                        or soup.find("div", class_="resppages")

            if paginacao:
                # tenta achar href com /page/N primeiro
                link = paginacao.find("a", href=re.compile(r'/page/\d+'))
                if link and link.get('href'):
                    m = re.search(r'/page/(\d+)', link.get('href'))
                    if m:
                        try:
                            next_page = int(m.group(1))
                        except:
                            next_page = False
                else:
                    # fallback: procurar <a> com texto numérico maior que o atual
                    current = None
                    cur_span = paginacao.find("span", class_="current")
                    if cur_span:
                        try:
                            current = int(cur_span.text.strip())
                        except:
                            current = None
                    for l in paginacao.find_all("a"):
                        txt = l.text.strip()
                        try:
                            prox = int(txt)
                            if current is None or prox > current:
                                next_page = prox
                                break
                        except:
                            continue

        except Exception as e:
            print("Erro no catálogo VOD3:", e)

        return itens, next_page

    def _scrape_busca(self, url):
        """
        Scrape para busca. RETORNA SOMENTE itens (sem next_page).
        """
        itens = []
        try:
            r = requests.get(url, headers=self.headers, timeout=15)
            soup = self.soup(r.text)

            results = soup.find_all("div", class_="result-item") \
                      or soup.find_all("article", id=lambda x: x and x.startswith("post")) \
                      or soup.find_all("div", class_="items")

            for res in results:
                try:
                    a = res.find("a")
                    href = a.get("href", "") if a else ""
                    title_tag = res.find("div", class_="title") or res.find("h3") or a
                    title = title_tag.text.strip() if title_tag else href
                    img = (res.find("img").get("src", "") if res.find("img") else "")
                    itens.append((title, href, img, title, self.base))
                except Exception:
                    continue

        except Exception as e:
            print("Erro na busca VOD3 (scrape_busca):", e)

        return itens
