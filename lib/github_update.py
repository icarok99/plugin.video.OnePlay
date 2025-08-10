# -*- coding: utf-8 -*-
try:
    from lib.helper import *
except ImportError:
    from helper import *
try:
    from lib.github import *
except ImportError:
    from github import *    

update_ver_file = 'https://raw.githubusercontent.com/icarok99/plugin.video.OnePlay/refs/heads/main/update.txt'
update_list = 'https://raw.githubusercontent.com/icarok99/plugin.video.OnePlay/refs/heads/main/files.json'
path_update_file = 'special://home/addons/plugin.video.OnePlay.Matrix/update.txt'
enable_update = True




def list_files():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0'}
    try:
        update_list_ = last_raw(update_list)
        r = requests.get(update_list_,headers=headers)
        if r.status_code == 200:
            files = r.json()
        else:
            files = []
            log('UPDATE: erro ao acessar %s'%update_list)
    except:
       files = []
    return files

def find_path(url):
    return url.split('main/')[1]

def update():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0'}
    ver_file = translate(path_update_file)
    if os.path.exists(ver_file):
        with open(ver_file, 'r') as f:
            ver_base = f.read()
            ver_base = ver_base.replace(' ', '').replace('\n', '')
            if enable_update:
                try:
                    url_update_file = last_raw(update_ver_file)
                    r = requests.get(url_update_file,headers=headers)
                    if r.status_code == 200:
                        ver_site = r.text
                        ver_site = ver_site.replace(' ', '').replace('\n', '')
                        if ver_site:
                            if ver_site != ver_base:
                                notify('Atualizando...')
                                files = list_files()
                                for i in files:
                                    path_kodi = 'special://home/addons/' + find_path(i)
                                    url_file = last_raw(i)
                                    d = translate(path_kodi)
                                    with open(d, 'wb') as f:
                                        log('UPDATE: acessando %s'%url_file)
                                        res = requests.get(url_file,headers=headers,stream=True)
                                        if res.status_code == 200:
                                            for chunk in res.iter_content(chunk_size=1024):
                                                f.write(chunk)
                                        else:
                                            log('UPDATE: falha ao acessar %s'%url_file)
                                # salvar update.txt
                                try:
                                    d = translate(path_update_file)
                                    with open(d, 'wb') as f:
                                        log('UPDATE: acessando %s'%url_update_file)
                                        res = requests.get(url_update_file,headers=headers,stream=True)
                                        if res.status_code == 200:
                                            for chunk in res.iter_content(chunk_size=1024):
                                                f.write(chunk)
                                        else:
                                            log('UPDATE: falha ao acessar %s'%url_update_file)
                                except:
                                    log('UPDATE: Erro ao baixar update.txt')
                                notify('Atualizado com sucesso')
                    else:
                        log('UPDATE: url %s nao existe'%url_update_file)
                except:
                    pass

