# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import re
import simplejson as json
import urllib
import sqlite3
from ga import ga

__addon__ = xbmcaddon.Addon()
__author__ = __addon__.getAddonInfo('author')
__scriptid__ = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__icon__ = __addon__.getAddonInfo('icon').decode('utf-8')
__language__ = __addon__.getLocalizedString
__cwd__ = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode('utf-8')
__profile__ = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode('utf-8')
__resource__ = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode('utf-8')
__icon_msg__ = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'bulsat.png' ) ).decode('utf-8')
clean_tvdb = __addon__.getSetting('clean_tvdb') == 'true'
clean_epgdb = __addon__.getSetting('clean_epgdb') == 'true'
db_dir = os.path.join(__profile__, "../../Database/").decode('utf-8')
epg_type = __addon__.getSetting('epg_type')
if epg_type == '1':
  __map__ = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'map.json' ) ).decode('utf-8')
else:
  __map__ = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'megamap.json' ) ).decode('utf-8')

__data__ = xbmc.translatePath(os.path.join( __profile__, '', 'dat') ).decode('utf-8')
__r_path__ = xbmc.translatePath(__addon__.getSetting('w_path')).decode('utf-8')
sys.path.insert(0, __resource__)



def progress_cb (a):
  _str = __scriptname__
  if a.has_key('idx') and a.has_key('max'):
    _str += ' %s of %d' % (a['idx'], a['max'])
  dp.update(a['pr'], _str  , a['str'])

def Notify (msg1, msg2):
  xbmc.executebuiltin((u'Notification(%s,%s,%s,%s)' % (msg1, msg2, '5000', __icon_msg__)).encode('utf-8'))

def check_plg():
  js_resp = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.GetAddons", "id":1}')
  if int(xbmc.getInfoLabel("System.BuildVersion" )[0:2]) > 14: ln = 1
  else: ln = 2

  if len(re.findall(r'blstfusion', js_resp)) > ln:
    Notify ('%s %s' % (__scriptname__, __version__) , '[COLOR FFFF0000]confilct ![/COLOR]')
    return False
  else:
    return True

def update(name, dat, crash=None):
  payload = {}
  payload['an'] = __scriptname__
  payload['av'] = __version__
  payload['ec'] = name
  payload['ea'] = 'tv_service'
  payload['ev'] = '1'
  payload['dl'] = urllib.quote_plus(dat.encode('utf-8'))
  ga('UA-79422131-11').update(payload, crash)


def dbg_msg(msg):
  if dbg:
    print'### %s: %s' % (__scriptid__, msg)

def is_player_active():
  try:
    res = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Player.GetActivePlayers", "id":1}')
    player_id = json.loads(res)["result"][0]["playerid"]
    res = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Player.GetItem","params":{"properties":["channeltype","channelnumber"],"playerid":%s},"id":"id1"}' % player_id)
    item_type = json.loads(res)["result"]["item"]["type"]
    if item_type == "channel":
      xbmc.log("PVR is playing!")
      return True
  except:
    pass
  xbmc.log("PVR is not playing!")
  return False    

def delete_tvdb():
  db_file = os.path.join(db_dir, "TV29.db")
  if os.path.isfile(db_file):
    xbmc.log("Trying to manually reset TV DB before restart %s" % db_file)
    conn = sqlite3.connect(db_file)
    with conn:
      cursor = conn.cursor()
      conn.execute('''DELETE FROM channels;''')
      xbmc.log('''Executing query: "DELETE FROM channels;"''')
      conn.execute('''DELETE FROM map_channelgroups_channels;''')
      xbmc.log('''Executing query: "DELETE FROM map_channelgroups_channels;"''')
      conn.execute('''DELETE FROM channelgroups;''')
      xbmc.log('''Executing query: "DELETE FROM channelgroups;"''')
      conn.execute('''VACUUM;''')
      xbmc.log('''Executing query: "VACUUM;"''')
      conn.commit()
  else:
    xbmc.log("DB file does nto exist! %s" % db_file)

def delete_epgdb():
  db_file = os.path.join(db_dir, "Epg11.db")
  if os.path.isfile(db_file):
    xbmc.log("Trying to reset EPG DB before restart %s" % db_file)
    conn = sqlite3.connect(db_file)
    with conn:
      cursor = conn.cursor()
      conn.execute('''DELETE FROM epg;''')
      xbmc.log('''Executing query: "DELETE FROM epg;"''')
      conn.execute('''DELETE FROM epgtags;''')
      xbmc.log('''Executing query: "DELETE FROM epgtags;"''')
      conn.execute('''DELETE FROM lastepgscan;''')
      xbmc.log('''Executing query: "DELETE FROM lastepgscan;"''')
      conn.execute('''VACUUM;''')
      xbmc.log('''Executing query: "VACUUM;"''')
      conn.commit()
  else:
    xbmc.log("DB file not found! %s" % db_file)
    
__ua_os = {
  '0' : {'ua' : 'pcweb', 'osid' : 'pcweb'},
  #'1' : {'ua' : 'samsunghas-agent/1.1', 'osid' : 'samsungtv'},
  '1' : {'ua' : 'Mozilla/5.0 (SMART-TV; Linux; Tizen 2.3) AppleWebkit/538.1 (KHTML, like Gecko) SamsungBrowser/1.0 TV Safari/538.1', 'osid' : 'samsungtv'},
  '2' : {'ua' : 'HLS Client/2.0 (compatible; LG NetCast.TV-2012)', 'osid' : 'lgtv'},
  '3' : {'ua' : 'Mozilla/5.0 (FreeBSD; Viera; rv:34.0) Gecko/20100101 Firefox/34.0', 'osid' : 'panasonictv'},
  '4' : {'ua' : 'Bulsatcom for android', 'osid' : 'androidtv'},
}


#########################################################################
### Run addon only if PVR is not active
#########################################################################
if is_player_active():
  xbmc.log("PVR is in use. Delaying playlist regeneration with 5 minutes")
  xbmc.executebuiltin('AlarmClock(%s, RunScript(%s, False), %s, silent)' % (__scriptid__, __scriptid__, 5))
else:
  dp = xbmcgui.DialogProgressBG()
  dp.create(heading = __scriptname__)

  if os.path.exists(os.path.join(__data__, '', 'data.dat')):
    with open(os.path.join(__data__, '', 'data.dat'), 'r') as f:
      js = json.load(f)
    if not (js.has_key('app_version') and js['app_version'] == __version__):
      u = __addon__.getSetting('username')
      p = __addon__.getSetting('password')

      for root, dirs, files in os.walk(__data__, topdown=False):
        for name in files:
          os.remove(os.path.join(root, name))
        for name in dirs:
          os.rmdir(os.path.join(root, name))
      __addon__.setSetting('firstrun', 'true')

  if __addon__.getSetting('firstrun') == 'true':
    Notify('Settings', 'empty')
    __addon__.openSettings()
    __addon__.setSetting('firstrun', 'false')

  if __addon__.getSetting('dbg') == 'true':
    dbg = True
  else:
    dbg = False

  if __addon__.getSetting('xxx') == 'true':
    xxx = True
  else:
    xxx = False

  if __addon__.getSetting('en_group_ch') == 'true':
    _group_name = False
  else:
    _group_name = __scriptid__

  if __addon__.getSetting('ext_epg') == 'true':
    etx_epg = True
  else:
    etx_epg = False

  if not __addon__.getSetting('username'):
    Notify('User', 'empty')
  if not __addon__.getSetting('password'):
    Notify('Password', 'empty')


  import traceback
  try:
    import bsc
    b = bsc.dodat(login = {'usr': __addon__.getSetting('username'), 'pass': __addon__.getSetting('password')},
                  path = __data__,
                  cachetime = float(__addon__.getSetting('refresh')),
                  dbg = dbg,
                  timeout=float(__addon__.getSetting('timeout')),
                  ver = __version__,
                  xxx = xxx,
                  os_id = __ua_os[__addon__.getSetting('dev_id')]['osid'],
                  agent_id = __ua_os[__addon__.getSetting('dev_id')]['ua'],
                  force_group_name = _group_name,
                  gen_m3u = True,
                  epg_type = epg_type,
                  compress = True,
                  proc_cb = progress_cb,
                  map_file = __map__)

    if check_plg():
      force = True
      if len(sys.argv) > 1 and sys.argv[1] == 'False':
        force = False
        dbg_msg('Reload timer')
        update('reload_timer',  __addon__.getSetting('check_interval'))
        xbmc.executebuiltin('AlarmClock (%s, RunScript(%s, False), %s, silent)' % (__scriptid__,__scriptid__, __addon__.getSetting('check_interval')))

      if b.gen_all(force):
        if __addon__.getSetting('en_cp') == 'true' and __addon__.getSetting('w_path') != '' and xbmcvfs.exists(__r_path__):
          if os.path.isfile(os.path.join(__data__, '', 'bulsat.xml.gz')):
            xbmcvfs.copy(os.path.join(__data__, '', 'bulsat.xml.gz'), os.path.join(__r_path__, '', 'bulsat.xml.gz'))
          if os.path.isfile(os.path.join(__data__, '', 'bulsat.m3u')):
            xbmcvfs.copy(os.path.join(__data__, '', 'bulsat.m3u'), os.path.join(__r_path__, '', 'bulsat.m3u'))
          dbg_msg('Copy Files')

        if __addon__.getSetting('en_custom_cmd') == 'true':
          __builtin = __addon__.getSetting('builtin_cmd')
          __script = __addon__.getSetting('script_cmd')

          if __builtin != '':
            dbg_msg ('builtin exec %s' % __builtin)
            update('builtin_exec %s' % __builtin, __ua_os[__addon__.getSetting('dev_id')]['osid'])
            xbmc.executebuiltin('%s' % __builtin)

          if __script != '':
            dbg_msg ('script exec %s' % __script)
            update('script_exec %s' % __script, __ua_os[__addon__.getSetting('dev_id')]['osid'])
            os.system(__script)

        dbg_msg('Reload PVR')
        update('reload_pvr', __ua_os[__addon__.getSetting('dev_id')]['osid'])
        ####################################################
        ###Restart PVR Service to reload channels' streams
        ####################################################
        if not is_player_active():
          xbmc.executebuiltin('XBMC.StopPVRManager')
          xbmc.sleep(1000)
          if clean_tvdb:
            delete_tvdb()
            xbmc.sleep(1000)
          if clean_epgdb:
            delete_epgdb()
            xbmc.sleep(1000)
          xbmc.executebuiltin('XBMC.StartPVRManager')

  except Exception, e:
    Notify('Error!', str(e))
    traceback.print_exc()
    update('exception', str(e.args[0]), sys.exc_info())
    pass

  dp.close()
