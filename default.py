# -*- coding: utf-8 -*-
from lib.helper import *
from lib import xtream, pluto, imdb 
from lib.vod import VOD1, VOD2
from lib.resolver import Resolver
import re
import base64

# === IMPORTS PARA ATUALIZAÇÃO ===
import os
import requests
from datetime import datetime
import github_update

# PROFILE E CONFIG DE UPDATE
profile = xbmcvfs.translatePath('special://profile/addon_data/plugin.video.OnePlay.Matrix')
UPDATE_CHECK_FILE = os.path.join(profile, 'last_checked_date.txt')
REMOTE_DATE_URL = 'https://raw.githubusercontent.com/icarok99/plugin.video.OnePlay/main/last_update.txt'

def get_local_date():
    try:
        with open(UPDATE_CHECK_FILE, 'r') as f:
            return datetime.strptime(f.read().strip(), '%d-%m-%Y')
    except:
        # data inicial padrão
        return datetime.strptime('18-08-2025', '%d-%m-%Y')

def save_local_date(date_str):
    with open(UPDATE_CHECK_FILE, 'w') as f:
        f.write(date_str)

def is_update_needed_by_date():
    try:
        response = requests.get(REMOTE_DATE_URL, timeout=5)
        if response.status_code == 200:
            remote_date_str = response.text.strip()
            remote_date = datetime.strptime(remote_date_str, '%d-%m-%Y')
            local_date = get_local_date()
            if remote_date > local_date:
                save_local_date(remote_date_str)
                return True
    except Exception as e:
        print(f'Erro ao verificar data remota: {e}')
    return False


vip_url_desc = '\x68\x74\x74\x70\x73\x3a\x2f\x2f\x6f\x6e\x65\x70\x6c\x61\x79\x68\x64\x2e\x63\x6f\x6d\x2f\x64\x6f\x77\x6e\x6c\x6f\x61\x64\x2f\x76\x69\x70\x2f\x69\x6e\x66\x6f\x5f\x6f\x6e\x65\x70\x6c\x61\x79\x2e\x74\x78\x74'
vip_url_dns = '\x68\x74\x74\x70\x73\x3a\x2f\x2f\x61\x64\x64\x6f\x6e\x2e\x6f\x6e\x65\x70\x6c\x61\x79\x68\x64\x2e\x6e\x65\x74\x2f\x64\x6e\x73\x5f\x76\x69\x70\x5f\x6f\x6e\x65\x70\x6c\x61\x79\x2e\x6a\x73\x6f\x6e'
channels_api_gratis = '\x68\x74\x74\x70\x73\x3a\x2f\x2f\x67\x69\x73\x74\x2e\x67\x69\x74\x68\x75\x62\x2e\x63\x6f\x6d\x2f\x7a\x6f\x72\x65\x75\x2f\x37\x31\x61\x30\x39\x63\x33\x34\x30\x66\x62\x37\x31\x33\x61\x62\x34\x30\x38\x38\x35\x34\x61\x64\x62\x36\x35\x31\x39\x61\x34\x36'
vod1_url = '\x68\x74\x74\x70\x73\x3a\x2f\x2f\x73\x75\x70\x65\x72\x66\x6c\x69\x78\x61\x70\x69\x2e\x73\x68\x6f\x70'
vod2_url = '\x68\x74\x74\x70\x73\x3a\x2f\x2f\x64\x6f\x72\x61\x6d\x61\x73\x6f\x6e\x6c\x69\x6e\x65\x2e\x6f\x72\x67'

try:
    class Donate_(xbmcgui.WindowDialog):
        def __init__(self):
            try:
                self.image = xbmcgui.ControlImage(440, 128, 400, 400, translate(os.path.join(homeDir, 'resources', 'images','qrcode.png')))
                self.text = xbmcgui.ControlLabel(x=150,y=570,width=1100,height=25,label='[B][COLOR yellow]SE ESSE ADD-ON LHE AGRADA, FAÇA UMA DOAÇÃO VIA PIX ACIMA E MANTENHA ESSE SERVIÇO ATIVO[/COLOR][/B]',textColor='yellow')
                self.text2 = xbmcgui.ControlLabel(x=495,y=600,width=1000,height=25,label='[B][COLOR yellow]PRESSIONE VOLTAR PARA SAIR[/COLOR][/B]',textColor='yellow')
                self.addControl(self.image)
                self.addControl(self.text)
                self.addControl(self.text2)
            except:
                pass
except:
    pass

def donate_question():
    q = yesno('', 'Deseja fazer uma doação do desenvolvedor?', nolabel='NÃO', yeslabel='SIM')
    if q:
        dialog2('AVISO', 'A DOAÇÃO É UMA AJUDA AO DESENVOLVEDOR E NÃO DA DIREITO AO VIP!')
        dialog_donate = Donate_()
        dialog_donate.doModal()

if not exists(profile):
    try:
        os.mkdir(profile)
    except:
        pass

def platform():
    from kodi_six import xbmc

    if xbmc.getCondVisibility('system.platform.android'):
        return 'android'
    elif xbmc.getCondVisibility('system.platform.linux') or xbmc.getCondVisibility('system.platform.linux.Raspberrypi'):
        return 'linux'
    elif xbmc.getCondVisibility('system.platform.windows'):
        return 'windows'
    elif xbmc.getCondVisibility('system.platform.osx'):
        return 'osx'
    elif xbmc.getCondVisibility('system.platform.atv2'):
        return 'atv2'
    elif xbmc.getCondVisibility('system.platform.ios') or xbmc.getCondVisibility('system.platform.darwin'):
        return 'ios'

def contador():
    #page: https://whos.amung.us/stats/addononeplay/
    name = '{0}-{1}'.format(addonID,addonVersion)
    page = 'https://oneplayhd.com'
    keycontador = 'addononeplay'
    s = platform()
    kodi_name = 'Kodi {0}'.format(kversion)
    user_agent = {'android': 'Mozilla/5.0 (Linux; Android 13; Mobile; rv:109.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36',
                  'windows': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
                  'linux': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
                  'osx': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
                  'atv2': 'Apple TV',
                  'ios': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
                  }.get(s, kodi_name)
    try:
        url_contador = 'https://whos.amung.us/pingjs/?k={0}&t={1}&c=s&x={2}&y=&a=0&d=0.74&v=27&r=1230'.format(keycontador,name,quote(page))
        r = requests.get(url_contador,headers={'User-Agent': user_agent})
    except:
        pass

contador()

def desc_vip():
    text = ''
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0'
    try:
        r = requests.get(vip_url_desc, headers={'User-Agent': user_agent})
        text += r.content.decode('utf-8')
    except:
        pass
    return text 


def vip_dns():
    text = []
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0'
    # try:
    #     r = requests.get('https://gist.github.com/zoreu/0e42aff50182190329a6c6a3a7e2a793/raw/vip_oneplay_dns.txt', headers={'User-Agent': user_agent})
    #     text += r.content.decode('utf-8')
    # except:
    #     pass
    try:
        #vip_url_dns_ = github.last_gist(vip_url_dns)
        #r = requests.get(vip_url_dns_, headers={'User-Agent': user_agent})
        r = requests.get(vip_url_dns, headers={'User-Agent': user_agent})
        text = r.json()
    except:
        pass
    return text 


def context_iptv_info(item):
    plugin = 'plugin://' + addonID + '/iptv_info/' + quote_plus(urlencode(item))
    context = [(item['name'], 'RunPlugin(%s)'%plugin)]
    return context

@route('/iptv_info')
def iptv_info(param):
    name = param['name']
    dns = param['dns']
    username = param['username']
    password = param['password']
    itens = xtream.API(dns,username,password).account_info()
    if itens:
        name_ = '{0}:'.format(name)
        i = []
        i.append(name_)
        i.extend(itens)
        msg = '\n'.join(i)
        dialog_text(msg)
    else:
        dialog('Lista offline')



def first_acess():
    first = getsetting('first')
    if first == 'true':
        q = yesno('', 'Deseja ativar os conteudos Adultos?')
        if q:
            setsetting('hidexxx', 'true')
            adult_password = input_text('Defina a senha Parental:')
            if not adult_password:
                adult_password = ''
            setsetting('parental_password', str(adult_password))
        else:
            setsetting('hidexxx', 'false')
        setsetting('first', 'false')    

@route('/')
def index():
    # === VERIFICAÇÃO DE UPDATE AUTOMÁTICA ===
    try:
        if is_update_needed_by_date():
            notify('Atualizando ONEPLAY...')
            github_update.update_files()
            notify('ONEPLAY atualizado com sucesso!')
    except Exception as e:
        notify(f'Erro na atualização: {e}')
    # === FIM DA VERIFICAÇÃO ===

    first_acess()
    desc_oneplay = '''
Para trabalhar em equipe precisamos ter empatia, transparência, solidariedade e muita lealdade, esses ingredientes são necessários para o sucesso em grupo.

[B][COLOR aquamarine]Repositório Oficial ONEPLAY[/COLOR][/B]
[COLOR blue]https://oneplayhd.com/oneplay[/COLOR]

[B][COLOR aquamarine]Grupo Oficial FACEBOOK[/COLOR][/B]
[COLOR blue]https://tinyurl.com/oneplay2019[/COLOR]

[B][COLOR aquamarine]Grupo Oficial TELEGRAM[/COLOR][/B]
[COLOR blue]http://t.me/oneplay2019[/COLOR]
    '''    
    setcontent('movies')
    addMenuItem({'name': '[B][COLOR aquamarine]:::[/COLOR]BEM-VINDOS AO ONEPLAY - GRATUITO[COLOR aquamarine]:::[/COLOR][/B]', 'description': desc_oneplay}, destiny='')
    addMenuItem({'name': '[B]TV AO VIVO[/B]', 'description': 'Assista aos melhores canais gratuitamente', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','tv.png'))}, destiny='/tvs')
    addMenuItem({'name': '[B]FILMES E SÉRIES[/B]', 'description': 'Assista aos melhores filmes e séries', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','filmeseseries.png'))}, destiny='/filmes_op1')
    addMenuItem({'name': '[B]DORAMAS[/B]', 'description': 'Assista aos melhores doramas', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','doramas.png'))}, destiny='/doramas')
    addMenuItem({'name': '[B]DOAÇÃO[/B]', 'description': 'Area de doação', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','doacao.png'))}, destiny='/donate')
    end()
    setview('List')

@route('/donate')
def donate(param):
    donate_question()

@route('/tvs')
def tvs(param):
    setcontent('movies')
    addMenuItem({'name': '[B]LISTAS IPTV[/B]', 'description': 'Listas IPTV','iconimage': translate(os.path.join(homeDir, 'resources', 'images','tv.png'))}, destiny='/tvgratis')    
    addMenuItem({'name': '[B]PLUTO TV[/B]', 'description': 'Canais Pluto TV', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','pluto.png'))}, destiny='/pluto_tv')  
    end()
    setview('List')

@route('/tvgratis')
def tvgratis(param):
    chan = github.last_gist(channels_api_gratis)
    iptv = xtream.parselist(chan)
    if iptv:
        addMenuItem({'name': '[B]:: ONEPLAY GRATUITO - TV ::[/B]', 'description': ''}, destiny='/ajustes')
        for n, (dns, username, password) in enumerate(iptv):
            n = n + 1
            item_context = {'name': 'INFO DA LISTA {0}'.format(str(n)), 'dns': dns, 'username': str(username), 'password': str(password)}
            addMenuItem({'name': 'LISTA {0}'.format(str(n)), 'description': 'Assista os melhores canais', 'tipo': 'gratis', 'dns': dns, 'username': str(username), 'password': str(password)}, context=context_iptv_info(item_context), destiny='/cat_channels')
        end()
        setview('WideList')
    else:
        notify('Falha ao exibir listas')

@route('/pluto_tv')
def pluto_tv(param):
    channels = pluto.playlist_pluto()
    if channels:
        setcontent('movies')
        for channel in channels:
            channel_name,desc,thumbnail,stream = channel
            addMenuItem({'name': channel_name, 'description': desc, 'iconimage': thumbnail, 'url': stream}, destiny='/play_pluto', folder=False)
        end()
        setview('List') 


@route('/play_pluto')
def play_pluto(param):
    if not exists(translate('special://home/addons/script.module.inputstreamhelper')):
        try:                            
            xbmc.executebuiltin('InstallAddon(script.module.inputstreamhelper)', wait=True)
        except:
            pass
    #https://github.com/flubshi/pvr.plutotv/blob/Matrix/src/PlutotvData.cpp
    import inputstreamhelper
    is_helper = inputstreamhelper.Helper("hls")
    if is_helper.check_inputstream():
        url = param.get('url', '')
        if '|' in url:
            header = unquote_plus(url.split('|')[1])
        play_item = xbmcgui.ListItem(path=url)
        play_item.setContentLookup(False)
        play_item.setArt({"icon": "DefaultVideo.png", "thumb": param.get('iconimage', '')})
        play_item.setMimeType("application/vnd.apple.mpegurl")
        if kversion >= 19:
            play_item.setProperty('inputstream', is_helper.inputstream_addon)
        else:
            play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)
        play_item.setProperty("inputstream.adaptive.manifest_type", "hls")
        if '|' in url:
            play_item.setProperty("inputstream.adaptive.manifest_headers", header)
        play_item.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
        play_item.setProperty('inputstream.adaptive.is_realtime_stream', 'true')
        if kversion > 19:
            info = play_item.getVideoInfoTag()
            info.setTitle(param.get('name', 'Pluto TV'))
            info.setPlot(param.get('description', ''))
        else:
            play_item.setInfo(type="Video", infoLabels={"Title": param.get('name', ''), "Plot": param.get('description', '')})    
        xbmc.Player().play(item=param.get('url', ''), listitem=play_item)

@route('/filmes_op1')
def filmes_op1(param):
    setcontent('movies')
    addMenuItem({'name': 'IMDB Filmes', 'description': '', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','filmes.png'))}, destiny='/imdb_movies')
    addMenuItem({'name': 'IMDB Series', 'description': '', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','series.png'))}, destiny='/imdb_series')
    end()
    setview('List')

@route('/imdb_movies')
def imdb_movies(param):
    addMenuItem({'name': 'Pesquisar Filmes', 'description': '', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','pesquisar.png'))}, destiny='/find_movies')
    addMenuItem({'name': 'Filmes - TOP 250', 'description': '', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','filmes.png'))}, destiny='/imdb_movies_250')
    addMenuItem({'name': 'Filmes - Popular', 'description': '', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','filmes.png'))}, destiny='/imdb_movies_popular')
    end()
    setview('WideList')

@route('/imdb_series')
def imdb_series(param):
    addMenuItem({'name': 'Pesquisar Series', 'description': '', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','pesquisar.png'))}, destiny='/find_series')
    addMenuItem({'name': 'Series - TOP 250', 'description': '', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','series.png'))}, destiny='/imdb_series_250')
    addMenuItem({'name': 'Series - Popular', 'description': '', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','series.png'))}, destiny='/imdb_series_popular')
    end()
    setview('WideList')

@route('/find_movies')
def find_movies(param):
    search = input_text(heading='Pesquisar')
    if search:
        itens = imdb.IMDBScraper().search_movies(search)
        if itens:
            setcontent('movies')
            for i in itens:
                name,img,page,year,imdb_id = i
                addMenuItem({'name': name, 'description': '', 'iconimage': img, 'url': '', 'imdbnumber': imdb_id}, destiny='/play_resolve_movies', folder=False)
            end()
            setview('Wall') 

@route('/find_series')
def find_series(param):
    search = input_text(heading='Pesquisar')
    if search:
        itens = imdb.IMDBScraper().search_series(search)
        if itens:
            setcontent('tvshows')
            for i in itens:
                name,img,page,year,imdb_id = i
                addMenuItem({'name': name, 'description': '', 'iconimage': img, 'url': page, 'imdbnumber': imdb_id}, destiny='/open_imdb_seasons')
            end()
            setview('Wall')                 


@route('/imdb_movies_250')
def movies_250(param=None):
    page = int(param.get('page', 1)) if param else 1
    per_page = 50
    start = (page - 1) * per_page
    end_ = start + per_page

    all_items = imdb.IMDBScraper().movies_250()
    itens = all_items[start:end_]

    if itens:
        setcontent('movies')
        for i in itens:
            name,image,url,description, imdb_id = i
            addMenuItem({'name': name, 'description': description, 'iconimage': image, 'url': '', 'imdbnumber': imdb_id}, destiny='/play_resolve_movies', folder=False)

        if end_ < len(all_items):
            addMenuItem({'name': 'Próxima Página', 'page': page + 1, 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','proximo.png'))}, destiny='/imdb_movies_250')

        end()
        setview('Wall')

@route('/imdb_series_250')
def series_250(param=None):
    page = int(param.get('page', 1)) if param else 1
    per_page = 50
    start = (page - 1) * per_page
    end_ = start + per_page

    all_items = imdb.IMDBScraper().series_250()
    itens = all_items[start:end_]

    if itens:
        setcontent('tvshows')
        for i in itens:
            name,image,url,description, imdb_id = i
            addMenuItem({'name': name, 'description': description, 'iconimage': image, 'url': url, 'imdbnumber': imdb_id}, destiny='/open_imdb_seasons')

        if end_ < len(all_items):
            addMenuItem({'name': 'Próxima Página', 'page': page + 1, 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','proximo.png'))}, destiny='/imdb_series_250')

        end()
        setview('Wall')

@route('/imdb_movies_popular')
def movies_popular(param=None):
    page = int(param.get('page', 1)) if param else 1
    per_page = 50
    start = (page - 1) * per_page
    end_ = start + per_page

    all_items = imdb.IMDBScraper().movies_popular()
    itens = all_items[start:end_]

    if itens:
        setcontent('movies')
        for i in itens:
            name,image,url,description, imdb_id = i
            addMenuItem({'name': name, 'description': description, 'iconimage': image, 'url': '', 'imdbnumber': imdb_id}, destiny='/play_resolve_movies', folder=False)

        if end_ < len(all_items):
            addMenuItem({'name': 'Próxima Página', 'page': page + 1, 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','proximo.png'))}, destiny='/imdb_movies_popular')

        end()
        setview('Wall')

@route('/imdb_series_popular')
def series_popular(param=None):
    page = int(param.get('page', 1)) if param else 1
    per_page = 50
    start = (page - 1) * per_page
    end_ = start + per_page

    all_items = imdb.IMDBScraper().series_popular()
    itens = all_items[start:end_]

    if itens:
        setcontent('tvshows')
        for i in itens:
            name,image,url,description, imdb_id = i
            addMenuItem({'name': name, 'description': description, 'iconimage': image, 'url': url, 'imdbnumber': imdb_id}, destiny='/open_imdb_seasons')

        if end_ < len(all_items):
            addMenuItem({'name': 'Próxima Página', 'page': page + 1, 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','proximo.png'))}, destiny='/imdb_series_popular')

        end()
        setview('Wall')


@route('/open_imdb_seasons')
def open_imdb_seasons(param):
    serie_icon = param.get('iconimage', '')
    serie_name = param.get('name', '')
    url = param.get('url', '')
    imdb_id = param.get('imdbnumber', '')
    itens = imdb.IMDBScraper().imdb_seasons(url)
    if itens:
        setcontent('tvshows')
        try:
            addMenuItem({'name': '::: ' + serie_name + ':::', 'description': '', 'iconimage': serie_icon}, destiny='')
        except:
            pass
        for i in itens:
            season_number, name, url_season = i
            addMenuItem({'name': name, 'description': '', 'iconimage': serie_icon, 'url': url_season, 'imdbnumber': imdb_id, 'season': season_number, 'serie_name': serie_name}, destiny='/open_imdb_episodes')
        end()
        setview('List')


@route('/open_imdb_episodes')
def open_imdb_episodes(param):
    serie_icon = param.get('iconimage', '')
    serie_name = param.get('serie_name', '')
    url = param.get('url', '')
    imdb_id = param.get('imdbnumber', '')
    season = param.get('season', '')
    itens = imdb.IMDBScraper().imdb_episodes(url)
    if itens:
        setcontent('tvshows')
        try:
            addMenuItem({'name': '::: ' + serie_name + ' - S' + str(season) + ':::', 'description': '', 'iconimage': serie_icon}, destiny='')
        except:
            pass 
        for i in itens:
            episode_number,name,img,fanart,description = i
            name_full = str(episode_number) + ' - ' + name
            #if not '#' in name_full and not '.' in name_full:
            addMenuItem({'name': name_full, 'description': description, 'iconimage': img, 'fanart': fanart, 'imdbnumber': imdb_id, 'season': season, 'episode': str(episode_number), 'serie_name': serie_name, 'playable': 'true'}, destiny='/play_resolve_series', folder=False)
        end()
        setview('List')

#doramasonline
@route('/doramas')
def doramas(param):
    setcontent('tvshows')
    addMenuItem({'name': '[B]PESQUISAR POR NOME[/B]', 'description': '', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','pesquisar.png'))}, destiny='/doramas_search', folder=True)
    addMenuItem({'name': '[B]DORAMAS DUBLADOS[/B]', 'description': '', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','doramas2.png'))}, destiny='/doramas_dublados', folder=True)
    addMenuItem({'name': '[B]DORAMAS LEGENDADOS[/B]', 'description': '', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','doramas3.png'))}, destiny='/doramas_legendados', folder=True)
    end()
    setview('List')

@route('/doramas_search')
def search_doramas(param):
    query = input_text('Pesquisar dorama')
    if not query:
        return

    lista = VOD2(vod2_url).search_doramas(query)

    if lista:
        setcontent('tvshows')
        for title, href, img, info, referer in lista:
            addMenuItem(
                {'name': title, 'description': info, 'iconimage': img, 'url': href, 'referer': referer},
                destiny='/doramas_episodios',
                folder=True
            )
        end()
        setview('List')

@route('/doramas_dublados')
def doramas_dublados(param):
    page = int(param.get('page', '1'))
    lista, next_page = VOD2(vod2_url).scraper_dublados(page=page)

    if lista:
        setcontent('tvshows')
        for title, href, img, info, referer in lista:
            addMenuItem(
                {
                    'name': title,
                    'description': info,
                    'iconimage': img,
                    'url': href,
                    'referer': referer,
                    'prioridade': 'DUBLADO'
                },
                destiny='/doramas_episodios',
                folder=True
            )
        if next_page:
            addMenuItem(
                {
                    'name': f'Página {next_page}',
                    'description': '',
                    'iconimage': translate(os.path.join(homeDir, 'resources', 'images', 'proximo.png')),
                    'page': str(next_page)
                },
                destiny='/doramas_dublados',
                folder=True
            )
        end()
        setview('List')


@route('/doramas_legendados')
def doramas_legendados(param):
    page = int(param.get('page', '1'))
    lista, next_page = VOD2(vod2_url).scraper_legendados(page=page)

    if lista:
        setcontent('tvshows')
        for title, href, img, info, referer in lista:
            addMenuItem(
                {
                    'name': title,
                    'description': info,
                    'iconimage': img,
                    'url': href,
                    'referer': referer,
                    'prioridade': 'LEGENDADO'
                },
                destiny='/doramas_episodios',
                folder=True
            )
        if next_page:
            addMenuItem(
                {
                    'name': f'Página {next_page}',
                    'description': '',
                    'iconimage': translate(os.path.join(homeDir, 'resources', 'images', 'proximo.png')),
                    'page': str(next_page)
                },
                destiny='/doramas_legendados',
                folder=True
            )
        end()
        setview('List')


@route('/doramas_episodios')
def scraper_episodios(param):
    url = param.get('url')
    prioridade = param.get('prioridade', '')

    if not url:
        return

    if re.search(r'/filmes?/|/generos/', url):
        addMenuItem(
            {
                'name': param.get('name', ''),
                'iconimage': param.get('iconimage', ''),
                'url': url,
            },
            destiny='/doramas_players',
            folder=False
        )
        end()
        setview()
        return

    lista = VOD2(vod2_url).scraper_episodios(url)
    if lista:
        setcontent('tvshows')
        for title, link, img, href in lista:
            addMenuItem(
                {
                    'name': title,
                    'iconimage': img,
                    'url': link,
                    'prioridade': prioridade
                },
                destiny='/doramas_players',
                folder=False
            )
        end()
        setview('List')


@route('/doramas_players')
def doramas_players(param):
    prioridade = param.get('prioridade', '').upper()
    name_movie = param.get('fullname', '') or param.get('name', '')
    iconimage = param.get('iconimage', '')
    playable = param.get('playable', 'false')
    url = param.get('url', '')

    if not url:
        notify('Link inválido para player!')
        return

    opcoes = VOD2(vod2_url).scraper_players(url)
    if not opcoes:
        notify('Nenhum player encontrado!')
        return

    # Filtra pelos que têm a prioridade no nome
    if prioridade:
        opcoes = [(nome, link) for nome, link in opcoes if prioridade in nome.upper()]

    if not opcoes:
        notify(f'Nenhum player {prioridade} encontrado!')
        return

    items_options = [nome for nome, link in opcoes]

    try:
        op = select('SELECIONE UMA OPÇÃO:', items_options)
        if op >= 0:
            link = opcoes[op][1]
            stream, sub = Resolver().resolverurls(link, vod2_url)
            if stream:
                play_video({
                    'url': stream,
                    'sub': sub,
                    'name': name_movie,
                    'iconimage': iconimage,
                    'description': '',
                    'playable': playable
                })
            else:
                notify('Stream indisponível')
    except Exception:
        notify('Stream indisponível')
 

@route('/vip')
def vip(param):
    username = getsetting('username')
    password = getsetting('password')
    if not username or not password:
        opensettings()
    else:
        #dns = vip_dns()
        #dns = dns.replace(' ', '').replace('\n', '')
        portal = int(getsetting('portal'))
        try:
            dns = vip_dns()[portal]['portal']
        except:
            notify('Falha ao conectar ao servidor')
            return
        ok = xtream.API(dns,username,password).check_login()
        if ok:
            setcontent('movies')
            addMenuItem({'name': '[B]::: VIP :::[/B]', 'description': ''}, destiny='')
            addMenuItem({'name': '[B]INFO[/B]', 'description': '', 'dns': dns, 'username': str(username), 'password': str(password)}, destiny='/info_vip')
            addMenuItem({'name': '[B]TV AO VIVO[/B]', 'description': 'Assista os melhores canais', 'tipo': 'vip', 'dns': dns, 'username': str(username), 'password': str(password)}, destiny='/cat_channels')
            addMenuItem({'name': '[B]FILMES[/B]', 'description': 'Assista os melhores filmes', 'dns': dns, 'username': str(username), 'password': str(password)}, destiny='/vod')
            addMenuItem({'name': '[B]SERIES[/B]', 'description': 'Assista as melhores series', 'dns': dns, 'username': str(username), 'password': str(password)}, destiny='/series_iptv')
            end()
            setview('List')
        else:
            notify('Login incorreto')
            opensettings()

@route('/info_vip')
def info_vip(param):
    dns = param['dns']
    username = param['username']
    password = param['password']
    itens = xtream.API(dns,username,password).account_info()
    if itens:
        addMenuItem({'name': '[B]::: VIP :::[/B]', 'description': ''}, destiny='')
        for info in itens:
            addMenuItem({'name': info, 'description': ''}, destiny='')
        end()
        setview('WideList')


@route('/cat_channels')
def cat_channels(param):
    dns = param['dns']
    username = param['username']
    password = param['password']
    tipo = param['tipo']
    if tipo == 'vip':
        boas_vindas = '[B]::: VIP :::[/B]'
    else:
        boas_vindas = '[B]::: GRATIS :::[/B]'
    cat = xtream.API(dns,username,password).channels_category()
    if cat:
        addMenuItem({'name': boas_vindas, 'description': ''}, destiny='')
        for i in cat:
            name, url = i
            addMenuItem({'name': name, 'description': '', 'tipo': tipo, 'dns': dns, 'username': str(username), 'password': str(password), 'url': url}, destiny='/open_channels')
        end()
        setview('WideList')
    else:
        notify('Servidor offline')

@route('/open_channels')
def open_channels(param):
    grupo = param['name']
    dns = param['dns']
    username = param['username']
    password = param['password']
    tipo = param['tipo']
    url = param['url']
    if re.search("Adult",grupo,re.IGNORECASE) or re.search("A Casa das Brasileirinhas",grupo,re.IGNORECASE) or re.search("XXX",grupo,re.IGNORECASE):
        password1 = getsetting('parental_password')
        password2 = input_text('Senha Parental:')
        if str(password1) == str(password2):
            pass
        else:
            dialog('Senha errada')
            return        
    open_ = xtream.API(dns,username,password).channels_open(url)
    if open_:
        setcontent('movies')
        addMenuItem({'name': '[B]::: {0} :::[/B]'.format(grupo), 'description': ''}, destiny='')
        for i in open_:
            name,link,thumb,desc = i
            if tipo == 'vip':
                addMenuItem({'name': name, 'description': desc, 'iconimage': thumb, 'url': link}, destiny='/play_direct', folder=False)
            elif tipo == 'gratis':
                addMenuItem({'name': name, 'description': desc, 'iconimage': thumb, 'url': link}, destiny='/play_f4m', folder=False)
        end()
        setview('List')
    else:
        notify('Opção indisponivel')
            

@route('/vod')
def vod(param):
    dns = param['dns']
    username = param['username']
    password = param['password']
    itens = xtream.API(dns,username,password).vod2()
    if itens:
        setcontent('movies')
        addMenuItem({'name': '[B]::: VIP :::[/B]', 'description': ''}, destiny='')
        for i in itens:
            name, link = i
            addMenuItem({'name': name, 'description': '', 'dns': dns, 'username': str(username), 'password': str(password), 'url': link}, destiny='/open_vod')
        end()
        setview('List')

@route('/open_vod')
def open_vod(param):
    grupo = param['name']
    dns = param['dns']
    username = param['username']
    password = param['password']
    url = param['url']
    if re.search("Adult",grupo,re.IGNORECASE) or re.search("A Casa das Brasileirinhas",grupo,re.IGNORECASE) or re.search("XXX",grupo,re.IGNORECASE):
        password1 = getsetting('parental_password')
        password2 = input_text('Senha Parental:')
        if str(password1) == str(password2):
            pass
        else:
            dialog('Senha errada')
            return
    itens = xtream.API(dns,username,password).Vodlist(url)
    if itens:
        setcontent('movies')
        for i in itens:
            name, link, thumb = i
            addMenuItem({'name': name, 'description': '', 'iconimage': thumb, 'url': link}, destiny='/play_direct', folder=False)
        end()
        setview('Wall')




@route('/series_iptv')
def series_iptv(param):
    dns = param['dns']
    username = param['username']
    password = param['password']
    itens = xtream.API(dns,username,password).series_cat()
    if itens:
        setcontent('movies')
        addMenuItem({'name': '[B]::: VIP :::[/B]', 'description': ''}, destiny='')
        for i in itens:
            name, link = i
            addMenuItem({'name': name, 'description': '', 'dns': dns, 'username': str(username), 'password': str(password), 'url': link}, destiny='/open_series')
        end()
        setview('List')

@route('/open_series')
def open_series(param):
    dns = param['dns']
    username = param['username']
    password = param['password']
    url = param['url']
    itens = xtream.API(dns,username,password).series_list(url)
    if itens:
        setcontent('movies')
        addMenuItem({'name': '[B]::: VIP :::[/B]', 'description': ''}, destiny='')
        for i in itens:
            name,link,thumb,background,plot,releaseDate,cast,rating_5based,episode_run_time,genre = i
            addMenuItem({'name': name, 'description': plot, 'iconimage': thumb, 'fanart': background, 'aired': releaseDate, 'duration': episode_run_time, 'genre': genre, 'dns': dns, 'username': str(username), 'password': str(password), 'url': link}, destiny='/seasons_iptv')
        end()
        setview('List')


@route('/seasons_iptv')
def seasons_iptv(param):
    name_serie = param['name']
    description = param['description']
    iconimage = param['iconimage']
    fanart = param['fanart']
    genre = param['genre']
    dns = param['dns']
    username = param['username']
    password = param['password']    
    url = param['url']
    itens = xtream.API(dns,username,password).series_seasons(url)
    if itens:
        setcontent('movies')
        addMenuItem({'name': '[B]::: VIP :::[/B]', 'description': ''}, destiny='')
        addMenuItem({'name': '[B]::: {0} :::[/B]'.format(name_serie), 'description': description, 'iconimage': iconimage, 'fanart': fanart}, destiny='')
        for n, i in enumerate(itens):
            season = str(n + 1)
            name,link,thumb,background = i
            addMenuItem({'name': name, 'description': description, 'iconimage': thumb, 'fanart': background, 'genre': genre, 'dns': dns, 'username': str(username), 'password': str(password), 'url': link, 'name_serie': name_serie, 'season_': season}, destiny='/episodes_iptv')
        end()
        setview('List')


@route('/episodes_iptv')
def episodes_iptv(param):
    name_serie = param['name_serie']
    season = param['season_']
    description = param['description']
    iconimage = param['iconimage']
    fanart = param['fanart']
    genre = param['genre']
    dns = param['dns']
    username = param['username']
    password = param['password']    
    url = param['url']
    itens = xtream.API(dns,username,password).season_list(url)
    if itens:
        setcontent('movies')
        addMenuItem({'name': '[B]::: VIP :::[/B]', 'description': ''}, destiny='')
        addMenuItem({'name': '[B]::: {0} - T{1} :::[/B]'.format(name_serie,str(season)), 'description': description, 'iconimage': iconimage, 'fanart': fanart}, destiny='')
        for n, i in enumerate(itens):
            episode = str(n + 1)
            name_player = '{0} - T{1}E{2}'.format(name_serie,season,episode)
            name,link,thumb,background,plot,releasedate,cast,rating_5based,duration,genre = i
            addMenuItem({'name': name, 'description': plot, 'iconimage': thumb, 'fanart': background, 'aired': releasedate, 'genre': genre, 'dns': dns, 'username': str(username), 'password': str(password), 'url': link, 'play_name': name_player, 'playable': 'true'}, destiny='/play_serie_iptv', folder=False)
        end()
        setview('List')


@route('/play_resolve_movies')
def play_resolve_movies(param):
    if not exists(translate('special://home/addons/script.module.inputstreamhelper')):
        try:                            
            xbmc.executebuiltin('InstallAddon(script.module.inputstreamhelper)', wait=True)
        except:
            pass    
    notify('Aguarde')
    # json_rpc_command = '''
    # {
    #     "jsonrpc": "2.0",
    #     "method": "Settings.SetSetting",
    #     "params": {
    #         "setting": "locale.languageaudio",
    #         "value": "por"
    #     },
    #     "id": 1
    # }
    # '''
    # xbmc.executeJSONRPC(json_rpc_command)
    import inputstreamhelper
    #serie_name = param.get('serie_name')
    #season = param.get('season', '')
    #episode = param.get('episode', '')
    iconimage = param.get('iconimage', '')
    imdb = param.get('imdbnumber', '')
    description = param.get('description', '')
    #name = serie_name + ' S' + str(season) + 'E' + str(episode)
    name = param.get('name', '')
    url = VOD1(vod1_url).movie(imdb)
    #url = api_vod.VOD().movie(imdb)
    if url:
        notify('Escolha o audio portugues nos ajustes')

        is_helper = inputstreamhelper.Helper("hls")
        if is_helper.check_inputstream():
            if '|' in url:
                header = unquote_plus(url.split('|')[1])
            play_item = xbmcgui.ListItem(path=url)
            play_item.setContentLookup(False)
            play_item.setArt({"icon": "DefaultVideo.png", "thumb": iconimage})
            play_item.setMimeType("application/vnd.apple.mpegurl")
            if kversion >= 19:
                play_item.setProperty('inputstream', is_helper.inputstream_addon)
            else:
                play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)
            play_item.setProperty("inputstream.adaptive.manifest_type", "hls")
            if '|' in url:
                play_item.setProperty("inputstream.adaptive.manifest_headers", header)
            play_item.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
            play_item.setProperty('inputstream.adaptive.is_realtime_stream', 'true')
            play_item.setProperty('inputstream.adaptive.original_audio_language', 'pt') 
            if kversion > 19:
                info = play_item.getVideoInfoTag()
                info.setTitle(name)
                info.setPlot(description)
                info.setIMDBNumber(str(imdb))
                #info.setSeason(int(season))
                #info.setEpisode(int(episode))
            else:
                play_item.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
                play_item.setInfo('video', {'imdbnumber': str(imdb)})
                #play_item.setInfo('video', {'season': int(season)})
                #play_item.setInfo('video', {'episode': int(episode)})

            #xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, play_item)
            xbmc.Player().play(item=url, listitem=play_item)
    else:
        notify('Stream Indisponivel')

@route('/play_resolve_series')
def play_resolve_series(param):
    if not exists(translate('special://home/addons/script.module.inputstreamhelper')):
        try:                            
            xbmc.executebuiltin('InstallAddon(script.module.inputstreamhelper)', wait=True)
        except:
            pass    
    # json_rpc_command = '''
    # {
    #     "jsonrpc": "2.0",
    #     "method": "Settings.SetSetting",
    #     "params": {
    #         "setting": "locale.languageaudio",
    #         "value": "por"
    #     },
    #     "id": 1
    # }
    # '''
    # xbmc.executeJSONRPC(json_rpc_command)
    import inputstreamhelper
    serie_name = param.get('serie_name')
    season = param.get('season', '')
    episode = param.get('episode', '')
    iconimage = param.get('iconimage', '')
    imdb = param.get('imdbnumber', '')
    description = param.get('description', '')
    name = serie_name + ' S' + str(season) + 'E' + str(episode)
    url = VOD1(vod1_url).tvshows(imdb,season,episode)
    if url:
        notify('Escolha o audio portugues nos ajustes')

        is_helper = inputstreamhelper.Helper("hls")
        if is_helper.check_inputstream():
            if '|' in url:
                header = unquote_plus(url.split('|')[1])
            play_item = xbmcgui.ListItem(path=url)
            play_item.setContentLookup(False)
            play_item.setArt({"icon": "DefaultVideo.png", "thumb": iconimage})
            play_item.setMimeType("application/vnd.apple.mpegurl")
            if kversion >= 19:
                play_item.setProperty('inputstream', is_helper.inputstream_addon)
            else:
                play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)
            play_item.setProperty("inputstream.adaptive.manifest_type", "hls")
            if '|' in url:
                play_item.setProperty("inputstream.adaptive.manifest_headers", header)
            play_item.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
            play_item.setProperty('inputstream.adaptive.is_realtime_stream', 'true')
            play_item.setProperty('inputstream.adaptive.original_audio_language', 'pt') 
            if kversion > 19:
                info = play_item.getVideoInfoTag()
                info.setTitle(name)
                info.setPlot(description)
                info.setIMDBNumber(str(imdb))
                info.setSeason(int(season))
                info.setEpisode(int(episode))
            else:
                play_item.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
                play_item.setInfo('video', {'imdbnumber': str(imdb)})
                play_item.setInfo('video', {'season': int(season)})
                play_item.setInfo('video', {'episode': int(episode)})

            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, play_item)
    else:
        notify('Stream Indisponivel')  


@route('/play_direct')
def play_direct(param):
    play_video(param)

@route('/play_serie_iptv')
def play_serie_iptv(param):
    name = param['play_name']
    param.update({'name': name})
    param.pop('play_name')
    play_video(param)

@route('/play_f4m')
def play_f4m(param):
    name = param['name']
    description = param['description']
    iconimage = param['iconimage']
    url = param['url']
    if url:
        plugin = 'plugin://plugin.video.f4mTester/?streamtype=HLSRETRY&name=' + quote_plus(str(name)) + '&iconImage=' + quote_plus(str(iconimage)) + '&thumbnailImage=' + quote_plus(str(iconimage)) + '&description=' + quote_plus(description) + '&url=' + quote_plus(url)
        xbmc.executebuiltin('RunPlugin(%s)' % plugin)
    else:
        notify('Stream indisponivel')

@route('/ajustes')
def ajustes(param):
    opensettings()
