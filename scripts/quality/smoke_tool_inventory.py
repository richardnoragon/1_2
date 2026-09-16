"""Isolated read-only tool launch probe, invoked by the inventory tests."""
import sys,os,tempfile,json,traceback
from pathlib import Path
from unittest.mock import patch
root=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))
profile=Path(sys.argv[2])
profile.mkdir(parents=True, exist_ok=True)
original_expanduser=os.path.expanduser
os.path.expanduser=lambda path: str(profile)+str(path)[1:] if str(path).startswith('~') else original_expanduser(path)
Path.home=classmethod(lambda cls: profile)
os.environ['XDG_CONFIG_HOME']=str(profile/'config')
os.environ['RFU_USER_ID']='harmonization-window-smoke'
from src.database.database_manager import DatabaseManager
DatabaseManager(profile/'data.db')
from PyQt5.QtCore import QTimer,QSettings
from PyQt5.QtWidgets import QApplication,QMessageBox,QFileDialog,QMainWindow
QSettings.setDefaultFormat(QSettings.IniFormat)
QSettings.setPath(QSettings.IniFormat,QSettings.UserScope,str(profile/'qt'))
app=QApplication([])
for method in ['information','warning','critical','question']:
 setattr(QMessageBox,method,lambda *args,**kw: QMessageBox.No)
from src.gui.tool_catalogue import launch_registered_tool
from src.simple_menu_manager import SimpleMenuManager
hub=QMainWindow();hub.menu_manager=SimpleMenuManager(hub);hub.menu_manager.create_menubar()
try:
 ok=launch_registered_tool(hub,sys.argv[1])
 window=hub._catalogue_windows[sys.argv[1]]
 app.processEvents()
 healthy = window.tool_runtime.check_health()
 assert ok and healthy and window.isVisible()
 body = window.centralWidget()
 runtime = window.tool_runtime
 owner = runtime.owner
 original_check = getattr(owner, 'health_check', None)
 owner.health_check = lambda: False
 assert not runtime.check_health()
 assert window.property('toolDegraded') and not body.isEnabled()
 assert runtime.stack.widget(0) is body
 runtime.retry()
 assert window.property('toolDegraded')
 owner.health_check = lambda: True
 runtime.retry()
 assert not window.property('toolDegraded') and body.isEnabled()
 if original_check is None:
  del owner.health_check
 else:
  owner.health_check = original_check
 assert any(action.shortcut().toString() == 'Ctrl+H' for action in window.findChildren(__import__('PyQt5.QtWidgets', fromlist=['QAction']).QAction))
 print('RFU_SMOKE_RESULT',json.dumps({'id':sys.argv[1],'launch':ok,'healthy':healthy,'visible':window.isVisible(),'fallback_retains_state':True,'retry_validated':True,'return_to_hub':True}),flush=True)
 QTimer.singleShot(150,app.quit)
 app.exec_()
 # Exit subprocess after a bounded read-only launch; no teardown save side effects.
 os._exit(0)
except Exception as exc:
 print('RFU_SMOKE_RESULT',json.dumps({'id':sys.argv[1],'error':type(exc).__name__+': '+str(exc)}),flush=True)
 traceback.print_exc()
 os._exit(1)
