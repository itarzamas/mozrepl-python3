#!/usr/bin/env python
#-*- coding: utf-8 -*-

# TODO remove base 64 on script , optimize script  , clean raw functions
# hacer q el saveimage sea una funcion de objeto (solo si esta en el tag img)
# llamada al self.execute repetida?
# dataURL.replace("data:image/png;base64,","");para todos
# def _rawExecute(self, command , log): borrar el log
# function_null??? dejar?, pero agregar exceptions

import base64
import json
import os
import random
import re
import sys
import telnetlib
import time
import urllib.error
import urllib.parse
import urllib.parse
import urllib.request
import uuid
from datetime import datetime
#from ufp.terminal.debug import print_ as debug

if sys.version_info < (3, ):
    from .exception import Exception as MozException

from .my_type.my_function import Function
from .my_type.my_object import Object
from .my_type.my_array import Array, Snapshot
from .my_type.my_raw import Raw
from .my_type.my_util import convertToJs
from .my_type.my_exception import Exception as MozException


class Mozrepl(object):
    """
    The class that provides an interface for Firefox MozREPL Add-on.
    
    It supports the with statement.
    
     ..
        https://github.com/bard/mozrepl/wiki/Pyrepl bard / mozrepl Wiki
    
     : param port: mozrepl Firefox Add-on port of.
     : type port: int
     : param host: mozrepl Firefox Add-on hosts in.
     : type host: unicode
    """

    _RE_PROMPT = re.compile(br'^repl\d*>', re.MULTILINE)
    DEFAULT_HOST = '127.0.0.1'
    # DEFAULT_HOST = '192.168.1.30'
    DEFAULT_PORT = 4242

    def __init__(self, port=DEFAULT_PORT, host=DEFAULT_HOST, log_enable=False):
        """
        mozrepl Firefox Add-on And connect.
        """
        self._isConnected = False
        self.connect(port, host)
        self.log = log_enable
        self.document = 'window.content.top.document'
        self.timeout_waitload = 60  # esperar 60 segundos

        self._baseVarname = '__pymozrepl_{uuid}'.format(uuid=uuid.uuid4().hex)

        buffer = """(function(){{ {baseVar} = {{ 'ref': {{}}, 'context': {{}}, 'modules': {{}} }}; }}()); (function(){{ let {{ Loader }} = Components.utils.import("resource://gre/modules/commonjs/toolkit/loader.js", {{}}); let loader = Loader.Loader({{ paths: {{ "sdk/": "resource://gre/modules/commonjs/sdk/", "": "resource://gre/modules/commonjs/" }}, modules: {{ "toolkit/loader": Loader, "@test/options": {{}} }}, resolve: function(id, base) {{ if ( id == "chrome" || id.startsWith("@") ) {{ return id; }}; return Loader.resolve(id, base); }} }}); let requirer = Loader.Module("main", "chrome://URItoRequire"); let require = Loader.Require(loader, requirer); {baseVar}.modules.require = require; }}()); (function(){{ {baseVar}.modules.base64 = {baseVar}.modules.require('sdk/base64'); {baseVar}.modules.uuid = {baseVar}.modules.require('sdk/util/uuid'); }}()); (function(){{ {baseVar}.modules.loader = Components.classes['@mozilla.org/moz/jssubscript-loader;1'].getService(Components.interfaces.mozIJSSubScriptLoader); }}()); (function(){{ {baseVar}.modules.represent = function(thing){{ var represent = arguments.callee; var s; switch(typeof(thing)) {{ case 'string': s = '"' + thing + '"'; break; case 'number': s = thing.toString(); break; case 'object': var names = []; for(var name in thing) {{ names.push(name); }}; s = thing.toString(); if(names.length > 0) {{ s += ' - {{'; s += names.slice(0, 7).map(function(n) {{ var repr = n + ': '; try {{ if(thing[n] === null) {{ repr += 'null'; }} else if(typeof(thing[n]) == 'object') {{ repr += '{{...}}'; }} else {{  repr += represent(thing[n]); }}; }} catch(e) {{ repr += '[Exception!]'; }}; return repr; }}).join(', '); if(names.length > 7) {{ s += ', ...'; }}; s += '}}'; }} break; case 'function': s = 'function() {{...}}'; break; default: s = thing.toString(); }}; return s; }}; }}()); null;""".format(
            baseVar=self._baseVarname)
        self._rawExecute(buffer)

    def connect(self, port=None, host=None):
        """
        Connect with mozrepl Firefox Add-on.
        
         The connection associated with the destination must be the same as the first target.
        
         : param port: mozrepl Firefox Add-on port of. If omitted, it uses the existing value.
         : param port: mozrepl Firefox Add-on hosts in. If omitted, it uses the existing value.
        """
        if port is not None:
            self.port = port

        if host is not None:
            self.host = host

        self._telnet = telnetlib.Telnet(self.host, self.port)
        self.prompt = self._telnet.expect([self._RE_PROMPT], 2)[1].group(0)
        self._isConnected = True

    def __repr__(self):
        return 'Mozrepl(port={port}, host={host})'.format(
            port=self.port, host=repr(self.host))

    def __enter__(self):
        return self

    def disconnect(self):
        """
        and Disconnects mozrepl Firefox Add-on temporarily.
        
         To clear up the status stored on the server, you must delete this object.
        """
        # If not connected, and not go through the disconnection process.
        if not self._isConnected:
            return

        self.prompt = None
        self._telnet.close()
        self._isConnected = False
        del self._telnet

    def __exit__(self, type, value, traceback):
        del self

    def _rawExecute(self, command, timeout=60):
        """
        Execute the command.
        
         without analyzing the command Unlike the execute method returns a string literally been returning from a Firefox MozREPL Add-on.
        
         : param command: command.
         : type command: unicode
         : return: Firefox MozREPL received a string summarizing the string returned by the Add-on.
         : return: return None if there is no response from the Firefox MozREPL Add-on.
         : rtype: unicode
    :timeout in seconds
        """
        # Forwarding
        command = command[:-1] if command[-1] == ';' else command
        buffer = """try {{ {command}; }} catch (e) {{ (function() {{ let robj = {{ 'exception': {{}} }}; Object.getOwnPropertyNames(e).forEach(function (key) {{ robj.exception[key] = e[key]; }}, e); let buffer = JSON.stringify(robj); buffer = window.btoa(unescape(encodeURIComponent(buffer))); return buffer; }}()) }};""".format(
            command=command, baseVar=self._baseVarname)

        if self.log:
            print(str(buffer), '\n')  # , 'lo que envio;'

        buffer = buffer.encode('UTF-8')
        try:
            self._telnet.write(buffer)
            respon = self._telnet.read_until(self.prompt, timeout)  # recive
        except:
            respon = b''
            print(buffer, 'error telnet null')

        # Remove unnecessary strings from the response string if a response exists.
        if respon:
            # If the response is present to remove unwanted strings in received response string.
            respon = re.sub(b'^ (\.+> )*', b'', respon)  # remover los " ...>""
            respon = re.sub(b'(\n)?' + self.prompt, b'', respon,
                            re.UNICODE)  # remove "\nrepl{x}>"
        else:
            respon = b''  # if the Object is Null
            print('object null')

        # Returns None if there is no response
        if not respon:
            return None

        # Parsing the received information.
        respon = respon[1:-1]  # Remove the double quotation marks
        try:
            respon = base64.decodestring(respon).decode()
            respon = json.loads(respon, strict=False)
        except:
            # print('en teoria solo daria este error si ya es base64') #esto pasa siempre ahora
            respon = respon.decode()
            respon = json.loads(respon, strict=False)

        # If the error throws an exception.
        if 'exception' in respon:
            try:
                print(respon['exception']['message'], ' <-- mensaje error')
            except:
                print(respon, '<-- sin mensaje')

            return None

        else:
            # print('//',respon , 'ok ;')
            # respon= respon.replace('[object Object] - ','')
            pass
        return respon

    def __del__(self):
        # If not connected, and not go through the disconnection process.
        if not self._isConnected:
            return

        buffer = """delete {baseVar}; null;""".format(
            baseVar=self._baseVarname)
        self._rawExecute(buffer)
        self.disconnect()

    def execute(self, command):
        """
        Execute the command.
        
        .. Attention :: When using the method of the object, 'repl.execute ("repl.home") ()' can not be used immediately after being returned as a function of the method. To use in this manner, give the object passes the call explicitly, as shown in 'repl.execute ("repl.home.call") (Raw ("repl"))', 'repl.execute ("repl"). Use the automatic binding function of pymozrepl as home () '.
        .. Attention :: pymozrepl one object has a separate single context. Please note that this context is different from the current context is provided in Firefox mozrepl.
        .. Do not use the attention :: javascript repl object.
        .. Have some information during todo :: command prompt mixed response it may not fully accepted. In addition, the value of the long -inf or something is not a problem for processing. To solve this problem, creates a response with the receive json returned by the file input and output.
        
        : Param command: command.
        : Type command: unicode
        : Raise mozrepl.Exception: mozrepl Firefox if you throw an error in the Add-on.
        : Returns:: py: class: `~ mozrepl.type.Object`: If the value received in return mozrepl Firefox Add-on this object.
        : Returns:: py: class: `~ mozrepl.type.Array`: value received in return mozrepl Firefox Add-on in this case the array.
        : Returns:: py: class: `~ mozrepl.type.Function`: value received in return mozrepl Firefox Add-on in this case the function.
        : Returns: default, such as string, number, bool Returns else is converted to an appropriate basic type in the corresponding python (int, bool, unicode, etc.).
        """

        # porque se pasaba antes en base64??
        # buffer = """(function(){{ let robj = {{}}; let lastCmdValue = {content} ; robj.type = typeof lastCmdValue; if ( robj.type == 'object' || robj.type == 'function' ) {{ if ( robj.type == 'object' && Array.isArray(lastCmdValue) ) {{ robj.type = 'array'; }}; {baseVar}.ref['{refUuid}'] = lastCmdValue; robj.refUuid = '{refUuid}'; }} else {{ robj.value = lastCmdValue; }}; var buffer = JSON.stringify(robj); buffer = {baseVar}.modules.base64.encode(buffer, 'utf-8'); return buffer; }}());""".format(
        buffer = """(function(){{ let robj = {{}}; let lastCmdValue = {content} ; robj.type = typeof lastCmdValue; if (lastCmdValue == null) {{return null;}}; if ( robj.type == 'object' || robj.type == 'function' ) {{ if ( robj.type == 'object' && Array.isArray(lastCmdValue) ) {{ robj.type = 'array'; }}; {baseVar}.ref['{refUuid}'] = lastCmdValue; robj.refUuid = '{refUuid}'; }} else {{ robj.value = lastCmdValue; }}; var buffer = JSON.stringify(robj); return buffer; }}());""".format(
            baseVar=self._baseVarname, refUuid=uuid.uuid4(), content=command)

        respon = self._rawExecute(buffer)

        # Si no hay respuesta que recibió como resultado Return
        if respon is None:
            # return FunctionNull(self, 'no existe item')
            return FunctionNull()
            return None

        if self.log:
            print('//', respon, 'ok ;')

        # function
        if respon['type'] == 'function':
            buffer = respon['refUuid']
            return Function(self, buffer)

        # array
        if respon['type'] == 'array':
            buffer = respon['refUuid']
            return Array(self, buffer)

        # object
        if respon['type'] == 'object':
            buffer = respon['refUuid']
            return Object(self, buffer)

        # Basic Type
        if 'value' in respon:
            return respon['value']

        return FunctionNull()
        # return FunctionNull(self, 'no existe funcion')
        return None

    def xpath(self, path, index=0, origin=None):
        if not origin:
            origin = self.document
        path = path.replace('"', '\\"')
        if index == 0:
            # print(f'{self.document}.evaluate("{path}", {origin}, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue')
            return (self.execute(
                f'{self.document}.evaluate("{path}", {origin}, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue'))

        res = self.execute(
            f'{self.document}.evaluate("{path}", {origin}, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)')

        if index == -1:
            res_snapshot = Snapshot(res._repl, res._uuid)
            res_snapshot = [i for i in res_snapshot]
            return res_snapshot
        else:
            return res_snapshot[index]


    def openUrl(self, url, wait=True):
        res = self.execute('{document}.location.href="{url}" '.format(
            document=self.document, url=url))
        if wait:
            self.waitLoad()
        return (res)

    def currentURL(self):
        res = self.execute('{document}.location.href'.format(
            document=self.document))
        return (res)

    def readHTML(self, mode='html'):
        if mode == 'body':
            mode = "body"
        if mode == 'html':
            mode = "documentElement"
        res = self.execute('{document}.{mode}.innerHTML'.format(
            document=self.document, mode=mode))
        return (res)

    def waitLoad(self):
        # espera maximo 2 min a que cargue
        for i in range(10 * self.timeout_waitload):
            if not self.execute("window.getBrowser().webProgress.isLoadingDocument"):
                break
            print('.', end='')
            time.sleep(0.1)

    def saveImage(self, capcha, filename='some_image.jpg'):
        varis = '''1;img = {capcha};var canvas = {document}.createElement("canvas");canvas.width = img.width;canvas.height = img.height;var ctx = canvas.getContext("2d");ctx.drawImage(img, 0, 0);var dataURL = canvas.toDataURL("image/png"); lastCmdValue = dataURL.replace("data:image/png;base64,",""); '''.format(
            document=self.document, capcha=capcha)
        img = self.execute(varis)
        if img:
            # print('\n' +img+'\n' )
            img = base64.b64decode(img.encode())

            f = open(filename, 'wb')
            f.write(img)
            f.close()
            # .tagName.toLowerCase();

    def tabSetSelected(self, vTab=0):
        return (self.execute("gBrowser.tabContainer.selectedIndex = {};".format(vTab)))
        # .advanceSelectedTab( -1, true ) = prev

    def tabCount(self, vTab=0):
        return (self.execute("gBrowser.mTabs.length;".format(vTab)))

    def tabAdd(self, url, select=False):
        if select:
            self.execute("gBrowser.selectedTab = gBrowser.addTab('{}')".format(url))
        else:
            self.execute("gBrowser.loadOneTab('{}',null,null,null,true)".format(url))

    # def tabGetSelected(self, vTab=0):
    #     return (self.execute("gBrowser.tabContainer.selectedIndex = {};".format(vTab)))
    #     # .advanceSelectedTab( -1, true ) = prev

    def getElement(self, sElement, sMode='id', index=0, wait=False):

        startTime = datetime.now()
        sMode = sMode.lower()
        res = None
        while 1:
            if sMode == "xpath":
                res = self.xpath(sElement, index)
            else:
                if sMode == "elements":
                    if sElement[:-7] == "OBJECT|":
                        sElement = sElement[8]
                elif sMode == "id":
                    sElement = "{document}.getElementById('{sElement}')".format(
                        document=self.document, sElement=sElement, index=index)
                elif sMode == "name":
                    sElement = "{document}.getElementsByName('{sElement}')[{index}]".format(
                        document=self.document, sElement=sElement, index=index)
                elif sMode == "class":
                    # esto retorna una tupula formaro (1,val1),(2,val2)
                    sElement = "{document}.getElementsByClassName('{sElement}')".format(
                        document=self.document, sElement=sElement)
                elif sMode == "tag":
                    sElement = "{document}.getElementsByTagName('{sElement}')[{index}]".format(
                        document=self.document, sElement=sElement, index=index)
                # if sMode == Else
                #   ???
                res = self.execute(sElement)
            if res or not wait or (wait and
                                   (datetime.now() - startTime).total_seconds() >= self.timeout_waitload):
                break

            time.sleep(0.02)
        return (res)

    def back(self, wait=True):
        if wait:
            self.waitLoad()
        return (self.execute("gBrowser.goBack()"))

    def waitGetForElement(self, element, wait=True):
        for i in range(10 * self.timeout_waitload):
            if element:
                return 1
            time.sleep(0.1)


class FunctionNull():
    # def __init__(self, repl, uuid):
    # super(FunctionNull, self).__init__(repl, uuid)

    def __repr__(self):
        return None
        # return 'function() {...}'

    def __str__(self):
        # print('str--')
        return ''

    def __call__(self, *args):
        # print('FunctionNull.__call__', args)
        return None

    def __getattribute__(self, key):
        # print('FunctionNull.__getattribute__', key)
        return None

    def __eq__(self, other):
        return None == other

    def __bool__(self):
        return False

    # def __del__(self):
    #   buffer = 'delete {reference}; null;'.format(reference=self)
    #   self._repl._rawExecute(buffer)
