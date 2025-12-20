# -*- coding: utf-8 -*-
from lib.helper import *
from lib import xtream, pluto, imdb 
from lib.vod import VOD1, VOD2, VOD3
from lib.resolver import Resolver
import re
import base64

import os
import requests
from datetime import datetime
import github_update

profile = xbmcvfs.translatePath('special://profile/addon_data/plugin.video.OnePlay.Matrix')
UPDATE_CHECK_FILE = os.path.join(profile, 'last_checked_date.txt')
REMOTE_DATE_URL = 'https://raw.githubusercontent.com/icarok99/plugin.video.OnePlay/main/last_update.txt'

def stop_player():
    try:
        player = xbmc.Player()
        if player.isPlaying():
            player.stop()
            xbmc.sleep(300)
    except:
        pass

def get_local_date():
    try:
        with open(UPDATE_CHECK_FILE, 'r') as f:
            return datetime.strptime(f.read().strip(), '%d-%m-%Y')
    except:
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
channels_api_gratis = '\x68\x74\x74\x70\x73\x3a\x2f\x2f\x64\x6f\x63\x73\x2e\x67\x6f\x6f\x67\x6c\x65\x2e\x63\x6f\x6d\x2f\x75\x63\x3f\x65\x78\x70\x6f\x72\x74\x3d\x64\x6f\x77\x6e\x6c\x6f\x61\x64\x26\x69\x64\x3d\x31\x31\x45\x4e\x5f\x4a\x59\x48\x4b\x36\x73\x38\x30\x55\x58\x72\x6d\x4d\x48\x47\x76\x47\x50\x79\x66\x75\x63\x32\x54\x37\x63\x39\x6a'
vod1_url = '\x68\x74\x74\x70\x73\x3a\x2f\x2f\x6e\x65\x74\x63\x69\x6e\x65\x2e\x6c\x61\x74'
vod2_url = 'https://superflixapi.run'
vod3_url = '\x68\x74\x74\x70\x73\x3a\x2f\x2f\x64\x6f\x72\x61\x6d\x61\x73\x6f\x6e\x6c\x69\x6e\x65\x2e\x6f\x72\x67'

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
    try:
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
    try:
        if is_update_needed_by_date():
            notify('Atualizando ONEPLAY...')
            github_update.update_files()
            notify('ONEPLAY atualizado com sucesso!')
    except Exception as e:
        notify(f'Erro na atualização: {e}')

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
    addMenuItem({'name': '[B]FILMES E SÉRIES[/B]', 'description': 'Assista aos melhores filmes e séries', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','filmeseseries.png'))}, destiny='/filmeseseries')
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
    notify('Carregando listas gratuitas...')
    iptv = xtream.parselist(channels_api_gratis)
    if iptv:
        addMenuItem({'name': '[B]:: ONEPLAY GRATUITO - TV ::[/B]'}, destiny='/ajustes')
        for n, (dns, username, password) in enumerate(iptv, 1):
            item_context = {'name': f'INFO DA LISTA {n}', 'dns': dns, 'username': username, 'password': password}
            addMenuItem({
                'name': f'LISTA {n}',
                'description': 'Canais gratuitos',
                'tipo': 'gratis',
                'dns': dns,
                'username': username,
                'password': password
            }, context=context_iptv_info(item_context), destiny='/cat_channels')
        end()
        setview('WideList')
    else:
        notify('Nenhuma lista gratuita disponível')

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

@route('/filmeseseries')
def filmeseseries(param):
    setcontent('movies')
    addMenuItem({'name': '[B]SERVIDOR 1[/B]', 'description': 'Assista aos melhores filmes e séries', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','filmeseseries.png'))}, destiny='/filmes_op1')
    addMenuItem({'name': '[B]SERVIDOR 2[/B]', 'description': 'Assista aos melhores filmes e séries', 'iconimage': translate(os.path.join(homeDir, 'resources', 'images','filmeseseries.png'))}, destiny='/filmes_op2')
    end()
    setview('List')

@route('/filmes_op2')
def filmes_op2(param):
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
            addMenuItem({'name': name_full, 'description': description, 'iconimage': img, 'fanart': fanart, 'imdbnumber': imdb_id, 'season_num': season, 'episode_num': str(episode_number), 'serie_name': serie_name, 'ep_title': name, 'playable': 'true'}, destiny='/play_resolve_series', folder=False)
        end()
        setview('List')      


@route('/filmes_op1')
def filmes_op1(param):
    addMenuItem({'name': '[B]PESQUISAR[/B]','iconimage': translate(os.path.join(homeDir, 'resources', 'images','pesquisar.png')), 'description': ''}, destiny='/pesquisar_filmes1', folder=True)
    addMenuItem({'name': '[B]FILMES[/B]','iconimage': translate(os.path.join(homeDir, 'resources', 'images','filmes.png')), 'description': ''}, destiny='/filmes1', folder=True)
    addMenuItem({'name': '[B]SÉRIES[/B]','iconimage': translate(os.path.join(homeDir, 'resources', 'images','series.png')), 'description': ''}, destiny='/series1', folder=True)
    end()
    setview('WideList')

@route('/pesquisar_filmes1')
def pesquisar_filmes1(param):
    pesquisa = param.get('pesquisa', '')
    url = param.get('next', '')
    if url:
        try:
            url = base64.b64decode(url[::-1]).decode('utf-8')
        except:
            pass    
    if pesquisa:
        itens_pesquisa, next_page, page = VOD1(vod1_url).pesquisa_filmes(url=url,pesquisa='')
    else:
        pesquisa = input_text('Pesquisa')
        if pesquisa:
            itens_pesquisa, next_page, page = VOD1(vod1_url).pesquisa_filmes(url='',pesquisa=pesquisa)
        else:
            return
    if itens_pesquisa:
        setcontent('movies')
        for name, iconimage, link in itens_pesquisa:
            try:
                new_url = base64.b64encode(link.encode('utf-8')).decode('utf-8')[::-1]
            except:
                new_url = link             
            if '/tvshows/' in link:
                addMenuItem({'name': name.encode('utf-8', 'ignore'),'iconimage': iconimage, 'description': '', 'url': new_url}, destiny='/temporada_serie1', folder=True)
            else:
                addMenuItem({'name': name.encode('utf-8', 'ignore'),'iconimage': iconimage, 'description': '', 'url': new_url}, destiny='/opcoes_filmes1', folder=False)
        if next_page:
            try:
                new_url_next = base64.b64encode(next_page.encode('utf-8')).decode('utf-8')[::-1]
            except:
                new_url_next = next_page            
            addMenuItem({'name': 'Pagina %s'%page,'iconimage': translate(os.path.join(homeDir, 'resources', 'images','proximo.png')), 'description': '', 'pesquisa': pesquisa, 'next': new_url_next}, destiny='/pesquisar_filmes1', folder=True)                
        end()
        setview('Wall')
    else:
        notify('Nenhum item encontrado!')

@route('/filmes1')
def filmes1(param):
    url = param.get('next', '')
    if url:
        try:
            url = base64.b64decode(url[::-1]).decode('utf-8')
        except:
            pass    
    filmes, next_page, page = VOD1(vod1_url).scraper_filmes(url)
    if filmes:
        setcontent('movies')
        for name, iconimage, link in filmes:
            try:
                new_url = base64.b64encode(link.encode('utf-8')).decode('utf-8')[::-1]
            except:
                new_url = link            
            addMenuItem({'name': name.encode('utf-8', 'ignore'),'iconimage': iconimage, 'description': '', 'url': new_url, 'playable': 'true'}, destiny='/opcoes_filmes1', folder=False)
        if next_page:
            try:
                new_url_next = base64.b64encode(next_page.encode('utf-8')).decode('utf-8')[::-1]
            except:
                new_url_next = next_page              
            addMenuItem({'name': 'Pagina %s'%page,'iconimage': translate(os.path.join(homeDir, 'resources', 'images','proximo.png')), 'description': '', 'next': new_url_next}, destiny='/filmes1', folder=True)
        end()
        setview('Wall') 

@route('/series1')
def series1(param):
    url = param.get('next', '')
    if url:
        try:
            url = base64.b64decode(url[::-1]).decode('utf-8')
        except:
            pass      
    series, next_page, page = VOD1(vod1_url).scraper_series(url)
    if series:
        setcontent('tvshows')
        for name, iconimage, link in series:
            try:
                new_url = base64.b64encode(link.encode('utf-8')).decode('utf-8')[::-1]
            except:
                new_url = link             
            addMenuItem({'name': name.encode('utf-8', 'ignore'),'iconimage': iconimage, 'description': '', 'url': new_url}, destiny='/temporada_serie1', folder=True)
        if next_page:
            try:
                new_url_next = base64.b64encode(next_page.encode('utf-8')).decode('utf-8')[::-1]
            except:
                new_url_next = next_page             
            addMenuItem({'name': 'Pagina %s'%page,'iconimage': translate(os.path.join(homeDir, 'resources', 'images','proximo.png')), 'description': '', 'next': new_url_next}, destiny='/series1', folder=True)
        end()
        setview('Wall') 

@route('/temporada_serie1')
def temporada_serie1(param):
    url = param.get('url', '')
    if url:
        try:
            url = base64.b64decode(url[::-1]).decode('utf-8')
        except:
            pass     
    serie_name, iconimage, fanart, s = VOD1(vod1_url).scraper_temporadas_series(url)
    if s:
        setcontent('tvshows')
        addMenuItem({'name': serie_name.encode('utf-8', 'ignore'),'iconimage': iconimage, 'fanart': fanart, 'description': ''}, destiny='', folder=True)
        for season,name,link in s:
            try:
                new_url = base64.b64encode(link.encode('utf-8')).decode('utf-8')[::-1]
            except:
                new_url = link             
            addMenuItem({'name': name.encode('utf-8', 'ignore'),'iconimage': iconimage, 'fanart': fanart, 'description': '', 'url': new_url, 'season': season}, destiny='/episodios_serie1', folder=True)
        end()
        setview('List')

@route('/episodios_serie1')
def episodios_serie1(param):
    url = param.get('url', '')
    if url:
        try:
            url = base64.b64decode(url[::-1]).decode('utf-8')
        except:
            pass      
    season = param.get('season', '')
    serie_name, iconimage, fanart, e = VOD1(vod1_url).scraper_episodios_series(url,season)
    if e:
        setcontent('tvshows')
        addMenuItem({'name': serie_name.encode('utf-8', 'ignore'),'iconimage': iconimage, 'fanart': fanart, 'description': ''}, destiny='', folder=True)
        for ep_name,name_especial,link in e:
            try:
                new_url = base64.b64encode(link.encode('utf-8')).decode('utf-8')[::-1]
            except:
                new_url = link              
            addMenuItem({'name': ep_name.encode('utf-8', 'ignore'),'iconimage': iconimage, 'fanart': fanart, 'description': '', 'url': new_url, 'fullname': name_especial.encode('utf-8', 'ignore'), 'playable': 'true'}, destiny='/opcoes_filmes1', folder=False)
        end()
        setview('List') 

@route('/opcoes_filmes1')
def opcoes_filmes1(param):
    name_movie = param.get('fullname', '')
    if not name_movie:
        name_movie = param.get('name', '')
    iconimage = param.get('iconimage', '')
    playable = param.get('playable', 'false')
    url = param.get('url', '')
    if url:
        try:
            url = base64.b64decode(url[::-1]).decode('utf-8')
        except:
            pass     
    if name_movie and url:
        op_ = VOD1(vod1_url).opcoes_filmes(url)
        items_options = [name2 for name2,link in op_]
        try:
            op = select('SELECIONE UMA OPÇÃO:', items_options)
            if op >= 0:
                link = op_[op][1]
                stream,sub = Resolver().resolverurls(link, '')
                if stream:
                    play_video({'url': stream, 'sub': sub, 'name': name_movie, 'iconimage': iconimage, 'description': '', 'playable': playable})
                else:
                    notify('Stream indisponivel') 
        except:
            notify('Stream indisponivel')

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

    lista = VOD3(vod3_url).search_doramas(query)

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
    lista, next_page = VOD3(vod3_url).scraper_dublados(page=page)

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
    lista, next_page = VOD3(vod3_url).scraper_legendados(page=page)

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

    if '/filmes/' in url:
        addMenuItem(
            {
                'name': param.get('name', ''),
                'iconimage': param.get('iconimage', ''),
                'url': url,
                'prioridade': prioridade
            },
            destiny='/doramas_players',
            folder=False
        )
        end()
        return

    html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text

    if 'dooplay_player_option' in html:
        addMenuItem(
            {
                'name': param.get('name', ''),
                'iconimage': param.get('iconimage', ''),
                'url': url,
                'prioridade': prioridade
            },
            destiny='/doramas_players',
            folder=False
        )
        end()
        return

    lista = VOD3(vod3_url).scraper_episodios(url)
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

    opcoes = VOD3(vod3_url).scraper_players(url)
    if not opcoes:
        notify('Nenhum player encontrado!')
        return

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
            stream, sub = Resolver().resolverurls(link, vod3_url)
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
    notify('Aguarde')
    stop_player()

    name = param.get('name', '')
    iconimage = param.get('iconimage', '')
    description = param.get('description', '')
    imdb_id = param.get('imdbnumber', '')

    url = VOD2(vod2_url).movie(imdb_id)

    if url:
        notify('Escolha o audio portugues nos ajustes')

        stream_url = url.split('|')[0] if '|' in url else url
        is_mp4 = stream_url.lower().endswith('.mp4')

        li = xbmcgui.ListItem(path=stream_url)
        li.setArt({'thumb': iconimage, 'icon': iconimage})
        li.setContentLookup(False)

        if is_mp4:
            li.setProperty('inputstream', 'inputstream.ffmpegdirect')
            li.setProperty('inputstream.ffmpegdirect.manifest_type', 'mp4')
            li.setMimeType('video/mp4')
        else:
            li.setProperty('inputstream', 'inputstream.adaptive')
            li.setProperty('inputstream.adaptive.manifest_type', 'hls')
            li.setMimeType('application/vnd.apple.mpegurl')
            li.setProperty('inputstream.adaptive.original_audio_language', 'pt')

        if '|' in url:
            headers = url.split('|', 1)[1]
            li.setProperty('inputstream.adaptive.stream_headers', headers)
            li.setProperty('inputstream.ffmpegdirect.stream_headers', headers)

        info = li.getVideoInfoTag()
        info.setTitle(name)
        info.setPlot(description)
        info.setIMDBNumber(imdb_id)
        info.setMediaType('movie')

        xbmc.Player().play(item=stream_url, listitem=li)

    else:
        notify('Stream Indisponivel')

@route('/play_resolve_series')
def play_resolve_series(param):
    notify('Aguarde')
    stop_player()

    serie_name = param.get('serie_name', '')
    season = param.get('season_num', '')
    episode = param.get('episode_num', '')
    iconimage = param.get('iconimage', '')
    imdb_id = param.get('imdbnumber', '')
    ep_title = param.get('ep_title', param.get('name', ''))

    url = VOD2(vod2_url).tvshows(imdb_id, season, episode)

    if url:
        notify('Escolha o audio portugues nos ajustes')

        stream_url = url.split('|')[0] if '|' in url else url
        is_mp4 = stream_url.lower().endswith('.mp4')

        li = xbmcgui.ListItem(path=stream_url)
        li.setArt({'thumb': iconimage, 'icon': iconimage})
        li.setContentLookup(False)

        if is_mp4:
            li.setProperty('inputstream', 'inputstream.ffmpegdirect')
            li.setProperty('inputstream.ffmpegdirect.manifest_type', 'mp4')
            li.setMimeType('video/mp4')
        else:
            li.setProperty('inputstream', 'inputstream.adaptive')
            li.setProperty('inputstream.adaptive.manifest_type', 'hls')
            li.setMimeType('application/vnd.apple.mpegurl')
            li.setProperty('inputstream.adaptive.original_audio_language', 'pt')

        if '|' in url:
            headers = url.split('|', 1)[1]
            li.setProperty('inputstream.adaptive.stream_headers', headers)
            li.setProperty('inputstream.ffmpegdirect.stream_headers', headers)

        info = li.getVideoInfoTag()
        info.setTitle(ep_title)
        info.setTvShowTitle(serie_name)
        info.setIMDBNumber(imdb_id)
        info.setMediaType('episode')

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)

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
