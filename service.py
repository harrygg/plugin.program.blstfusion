import xbmc
xbmc.executebuiltin('RunScript(plugin.program.blstfusion, False)')

monitor = xbmc.Monitor()
while not monitor.abortRequested():
  xbmc.sleep(250)

xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"pvr.iptvsimple","enabled":"false"},"id":1}')
xbmc.log("plugin.program.blstfusion | PVR Manager disabled on exit.", xbmc.LOGNOTICE)
