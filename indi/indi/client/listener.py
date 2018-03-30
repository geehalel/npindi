# Copyright 2017 geehalel@gmail.com
#
# This file is part of npindi.
#
#    npindi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    npindi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with npindi.  If not, see <http://www.gnu.org/licenses/>.

import socket
import threading
import xml.parsers.expat
import xml.etree.ElementTree

from indi.INDI import INDI

class IndiExpatParser:
    def __init__(self, indiclient):
        self.indiclient=indiclient
        self.parser=xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler=self.start_element
        self.parser.EndElementHandler=self.end_element
        self.parser.Parse('<fakeindiroot>', 0)
        self.current_depth=0
    def start_element(self,name, attrs):
        #print('Start element:', name, attrs)
        self.current_depth+=1
    def end_element(self, name):
        #print('End element:', name)
        self.current_depth-=1
        print('Parsed a', name, 'element')
    def parse_chunk(self, buf):
        self.parser.Parse(buf, 0)

class IndiEtreeParser:
    def __init__(self, indiclient):
        self.indiclient=indiclient
        self.parser=xml.etree.ElementTree.XMLPullParser(['start', 'end'])
        self.parser.feed('<fakeindiroot>')
        for event, elem in self.parser.read_events():
            pass
        self.current_chunk=[]
        self.current_depth=0
    def parse_chunk(self, buf):
        self.parser.feed(buf)
        for event, elem in self.parser.read_events():
            #print(event, elem.tag, elem.keys())
            if event=='start':
                self.current_depth+=1
            elif event=='end':
                self.current_depth-=1
            else:
                logger.error('Parser: unknown event')
            if self.current_depth==0:
                #print('Parsed a', elem.tag,'element')
                if not self.indiclient.dispatch_command(elem):
                    logger.error('Parser: dispatch_command failed for element '+ elem.tag)


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._shutdown_flag = threading.Event()

    def stop(self):
        self._shutdown_flag.set()

    def stopped(self):
        return self._shutdown_flag.isSet()

class Listener(StoppableThread):
    def __init__(self, indiclient):
        super(Listener, self).__init__()
        self.indiclient=indiclient
        self.socket=self.indiclient.client_socket
        #self.parser=IndiExpatParser(self.indiclient)
        self.parser=IndiEtreeParser(self.indiclient)
        #self.record=True
        self.record=False
        self.recordfile=None
    def run(self):
        if self.record:
            self.recordfile=open('indilog.xml', 'wb')
        self.socket.settimeout(0.5)
        self.socket.sendall(b'<getProperties version="'+INDI.INDIV+b'"/>')
        while not self.stopped():
            try:
                buf=self.socket.recv(INDI.MAXINDIBUF)
                if self.record:
                    self.recordfile.write(buf)
                #logger.info('Listener: '+buf)
                self.parser.parse_chunk(buf)
            except socket.timeout:
                pass
