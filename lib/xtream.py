# -*- coding: utf-8 -*-
import xml.dom.minidom
import base64
import re
import socket
import requests
from urllib.parse import urlparse, parse_qs

try:
    from lib.helper import *
except:
    from helper import *

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'

class DNSResolver:
    def __init__(self, dns_server='1.1.1.1'):
        self.etc_hosts = {}
        self.cache_resolve_dns = {}
        self.DNS_SERVER = dns_server
    def resolver(self, builtin_resolver):
        def wrapper(*args, **kwargs):
            try: return self.etc_hosts[args[:2]]
            except KeyError: return builtin_resolver(*args, **kwargs)
        return wrapper
    def dns_query_custom(self, hostname):
        query = b'\xaa\xbb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' + b''.join(bytes([len(p)]) + p.encode() for p in hostname.split('.')) + b'\x00\x00\x01\x00\x01'
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.sendto(query, (self.DNS_SERVER, 53))
        resp, _ = sock.recvfrom(512)
        sock.close()
        ip = '.'.join(map(str, resp[resp.find(b'\xc0')+12:resp.find(b'\xc0')+16]))
        return ip
    def _change_dns(self, domain, port, ip):
        self.etc_hosts[(domain, port)] = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, port))]
    def change(self, url):
        socket.getaddrinfo = self.resolver(socket.getaddrinfo)
        p = urlparse(url)
        port = p.port or (443 if p.scheme=='https' else 80)
        host = p.hostname
        try: ip = self.cache_resolve_dns[host]
        except:
            try: ip = self.dns_query_custom(host)
            except: ip = '127.0.0.1'
            self.cache_resolve_dns[host] = ip
        self._change_dns(host, port, ip)

dnsresolver_ = DNSResolver()

def cliente(url):
    dnsresolver_.change(url)
    return requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=15)

def parselist(input_data):
    iptv = []
    content = ""
    url = ""

    if isinstance(input_data, str) and input_data.strip().startswith('http'):
        url = input_data.strip()
        if 'gist.github' in url:
            if '/raw' not in url:
                if url.endswith('/'): url = url[:-1]
                parts = url.split('github.com/')[1].split('/')
                url = f"https://gist.githubusercontent.com/{parts[0]}/{parts[1]}/raw"
        try:
            r = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=15)
            r.raise_for_status()
            content = r.text
        except:
            return iptv
    else:
        content = input_data

    lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
    for line in lines:
        if 'username=' not in line or 'password=' not in line or 'http' not in line:
            continue
        try:
            dns, user, pwd = extract_info(line)
            if dns and user and pwd:
                dns = dns.rstrip('/')
                key = f"{dns}|{user}"
                if not any(key == f"{d}|{u}" for d, u, p in iptv):
                    iptv.append((dns, user, pwd))
        except:
            continue
    return iptv

def extract_info(url):
    p = urlparse(url)
    protocol = p.scheme
    host = p.hostname
    port = p.port or (443 if protocol=='https' else 80)
    dns = f'{protocol}://{host}:{port}'
    q = parse_qs(p.query)
    username = q.get('username', [None])[0]
    password = q.get('password', [None])[0]
    return dns, username, password

def replace_desc(d): return re.sub(r'[\[\(]', lambda m: '[COLOR aquamarine][' if m.group(0)=='[' else '[/COLOR](', d)
def replace_name(n): return n.replace('-', '-[COLOR aquamarine]') + '[/COLOR]' if '-' in n else n
def ordenar_resolucao(i):
    n = i[0]
    if 'FHD' in n: return 1
    if 'HD' in n: return 2
    if '4K' in n: return 3
    if 'SD' in n: return 4
    return 5
def remove_emojis(t):
    try: return re.sub(r'[\U00010000-\U0010ffff\u2600-\u26FF\u2700-\u27BF\u2B50-\u2B59]', '', t).replace('  ', ' ').strip()
    except: return t

class API:
    def __init__(self, dns, username, password):
        self.live_url  = f'{dns}/enigma2.php?username={username}&password={password}&type=get_live_categories'
        self.live_url2 = f'{dns}/player_api.php?username={username}&password={password}&action=get_live_categories'
        self.vod_url   = f'{dns}/enigma2.php?username={username}&password={password}&type=get_vod_categories'
        self.vod_url2  = f'{dns}/player_api.php?username={username}&password={password}&action=get_vod_categories'
        self.series_url = f'{dns}/enigma2.php?username={username}&password={password}&type=get_series_categories'
        self.player_api = f'{dns}/player_api.php?username={username}&password={password}'
        self.play_url   = f'{dns}/live/{username}/{password}/'
        self.play_movies = f'{dns}/movie/{username}/{password}/'
        self.play_series = f'{dns}/series/{username}/{password}/'
        self.adult_tags = ['xxx','XXX','adult','Adult','ADULT','porn','Porn','PORN']
        try:
            self.hide_adult = getsetting('hidexxx')
        except:
            self.hide_adult = 'true'

    def http(self, url='', mode=None):
        try: return cliente(url).content
        except: return b''

    def check_login(self):
        try: return cliente(self.player_api).json()['user_info']['auth'] == 1
        except: return False

    def MonthNumToName(self, num):
        m = {'01':'Janeiro','02':'Fevereiro','03':'Março','04':'Abril','05':'Maio','06':'Junho',
             '07':'Julho','08':'Agosto','09':'Setembro','10':'Outubro','11':'Novembro','12':'Dezembro'}
        return m.get(num, '')

    def account_info(self):
        itens = []
        try:
            p = cliente(self.player_api).json()['user_info']
            exp = p.get('exp_date')
            if exp and exp != "null":
                exp = datetime.fromtimestamp(int(exp)).strftime('%d/%m/%Y')
                d, m, a = exp.split('/')
                exp = f"{d} de {self.MonthNumToName(m)} de {a.split('-')[0]}"
            else:
                exp = 'Ilimitado'
            itens.append(f"[B][COLOR white]Expira em:[/COLOR][/B] {exp}")
            itens.append(f"[B][COLOR white]Status:[/COLOR][/B] {'Ativo' if p['status']=='Active' else p['status']}")
            itens.append(f"[B][COLOR white]Conexões atuais:[/COLOR][/B] {p.get('active_cons','0')}")
            itens.append(f"[B][COLOR white]Conexões permitidas:[/COLOR][/B] {'Ilimitado' if p['max_connections'] in ('null','0') else p['max_connections']}")
        except: pass
        return itens

    def b64(self, obj):
        try: return base64.b64decode(obj).decode('utf-8')
        except: return ''

    def check_protocol(self, url):
        return url.replace('http://', 'https://') if 'https' in self.player_api else url

    def channels_category(self):
        itens = []
        try:
            data = cliente(self.live_url2).json()
            for c in data:
                name = remove_emojis(c['category_name'])
                if 'All' not in name and (self.hide_adult == 'true' or not any(t in name for t in self.adult_tags)):
                    url = f"{self.player_api}&action=get_live_streams&category_id={c['category_id']}"
                    itens.append((name, url))
        except:
            try:
                xml = cliente(self.live_url).content.decode(errors='ignore')
                doc = xml.dom.minidom.parseString(xml)
                for i, _ in enumerate(doc.getElementsByTagName('channel')):
                    name = remove_emojis(self.b64(doc.getElementsByTagName('title')[i].firstChild.nodeValue))
                    url = self.check_protocol(doc.getElementsByTagName('playlist_url')[i].firstChild.nodeValue.replace('<![CDATA[','').replace(']]>',''))
                    if 'All' not in name and (self.hide_adult == 'true' or not any(t in name for t in self.adult_tags)):
                        itens.append((name, url))
            except: pass
        return itens

    def channels_open(self, url):
        itens = []
        try:
            data = cliente(url).json()
            for c in data:
                name = remove_emojis(c.get('name', ''))
                stream_id = c['stream_id']
                thumb = c.get('stream_icon', '')
                link = f"{self.play_url}{stream_id}.m3u8"
                itens.append((name, link, thumb, ''))
        except: pass
        return sorted(itens, key=ordenar_resolucao) if itens else itens

    def vod2(self):
        itens = []
        try:
            data = cliente(self.vod_url2).json()
            for c in data:
                name = remove_emojis(c['category_name'])
                if self.hide_adult == 'true' or not any(t in name for t in self.adult_tags):
                    link = f"{self.player_api}&action=get_vod_streams&category_id={c['category_id']}"
                    itens.append((name, link))
        except: pass
        return itens

    def Vodlist(self, url):
        itens = []
        try:
            data = cliente(url).json()
            for c in data:
                name = c['name']
                link = f"{self.play_movies}{c['stream_id']}.{c['container_extension']}"
                thumb = c.get('stream_icon', '')
                if self.hide_adult == 'true' or not any(t in name for t in self.adult_tags):
                    itens.append((name, link, thumb))
        except: pass
        return itens

    def series_cat(self):
        itens = []
        try:
            data = cliente(f"{self.player_api}&action=get_series_categories").json()
            for c in data:
                name = remove_emojis(c['category_name'])
                if self.hide_adult == 'true' or not any(t in name for t in self.adult_tags):
                    url = f"{self.player_api}&action=get_series&category_id={c['category_id']}"
                    itens.append((name, url))
        except: pass
        return itens

    def series_list(self, url):
        itens = []
        try:
            data = cliente(url).json()
            for s in data:
                itens.append((
                    s['name'],
                    f"{self.player_api}&action=get_series_info&series_id={s['series_id']}",
                    s.get('cover', ''),
                    s.get('backdrop_path', [''])[0] if s.get('backdrop_path') else '',
                    s.get('plot', ''),
                    s.get('releaseDate', '') or s.get('year', ''),
                    [], '', '', s.get('genre', '')
                ))
        except: pass
        return itens

    def series_seasons(self, url):
        itens = []
        try:
            data = cliente(url).json()
            info = data.get('info', {})
            for s in data['episodes'].keys():
                itens.append((f"Temporada {s}", f"{url}&season_number={s}",
                             info.get('cover',''), info.get('backdrop_path','')[0] if info.get('backdrop_path') else ''))
        except: pass
        return itens

    def season_list(self, url):
        itens = []
        try:
            data = cliente(url).json()
            season = parse_qs(urlparse(url).query)['season_number'][0]
            for e in data['episodes'][season]:
                link = f"{self.play_series}{e['id']}.{e['container_extension']}"
                info = e.get('info', {})
                itens.append((
                    e['title'], link,
                    info.get('movie_image', ''),
                    info.get('movie_image', ''),
                    info.get('plot', ''),
                    info.get('releasedate', ''),
                    [], '', info.get('duration', ''), data['info'].get('genre', '')
                ))
        except: pass
        return itens