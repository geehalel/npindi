from app import Sofi
from sofi.ui import Container, View, Form, FormGroup, Label, Input, Span, UnorderedList, ListItem, Div
from sofi.ui import Paragraph, Heading, Anchor, Image
from sofi.ui import Navbar, Dropdown, DropdownItem
from sofi.ui import Button, ButtonGroup, ButtonToolbar, ButtonDropdown
from sofi.ui.fontawesomeicon import FontAwesomeIcon

from indi.client.indieventqueuemediator import IndiEventAsyncioMediator
from indi.client.indiclient import IndiClient
from indi.client.indievent import IndiEventType
from indi.INDI import INDI

import asyncio

import logging
import html

class PropertyUI:
    def __init__(self, prop, propid, client):
        self.prop = prop
        self.propid = propid
        self.client=client
        self.elems = dict()
    def gethtmlstatus(self):
        pstatus=self.prop.s
        htmlstatus=""
        if pstatus == INDI.IPState.IPS_ALERT:
            htmlstatus='<i class="fa fa-exclamation-triangle" aria-hidden="true" style="color:orange;"></i>'
        elif pstatus == INDI.IPState.IPS_BUSY:
            htmlstatus='<i class="fa fa-spinner fa-spin fa-1x fa-fw" style="color:blue;"></i>'
        elif pstatus == INDI.IPState.IPS_IDLE:
            htmlstatus='<i class="fa fa-pause-circle-o" aria-hidden="true" style="color:darkgrey;"></i>'
        elif pstatus == INDI.IPState.IPS_OK:
            htmlstatus='<i class="fa fa-check-circle-o" aria-hidden="true" style="color:green;"></i>'
        return htmlstatus
    async def settercallback(self, event):
        #logging.info(self.prop.name+' setting element '+str(event["element"]))
        if event["element"].count('-') == 3:
            # set a whole property
            self.client.send_new_property(self.prop)
            return
        pelemidset = event["element"]
        pelemid='-'.join(pelemidset.split('-')[:-1])
        ptype = self.prop.type
        logging.info(self.prop.name+' setting element '+ self.elems[pelemid].name + '('+pelemidset+')')
        if ptype == INDI.INDI_PROPERTY_TYPE.INDI_SWITCH:
            prule=self.prop.rule
            if self.prop.rule == INDI.ISRule.ISR_NOFMANY:
                if self.elems[pelemid].s == INDI.ISState.ISS_ON:
                    self.elems[pelemid].s = INDI.ISState.ISS_OFF
                else:
                    self.elems[pelemid].s = INDI.ISState.ISS_ON
            elif self.prop.rule == INDI.ISRule.ISR_1OFMANY:
                for elemid in self.elems:
                    self.elems[elemid].s = INDI.ISState.ISS_OFF
                self.elems[pelemid].s = INDI.ISState.ISS_ON
            elif self.prop.rule == INDI.ISRule.ISR_ATMOST1:
                if self.elems[pelemid].s == INDI.ISState.ISS_ON:
                    self.elems[pelemid].s = INDI.ISState.ISS_OFF
                else:
                    for elemid in self.elems:
                        self.elems[elemid].s = INDI.ISState.ISS_OFF
                    self.elems[pelemid].s = INDI.ISState.ISS_ON
            self.client.send_new_property(self.prop)
        else:
            self.client.send_new_elem(self.prop, self.elems[pelemid])
    async def changevalueelement(self, event):
        pelemid = event["element"]
        ptype = self.prop.type
        if ptype == INDI.INDI_PROPERTY_TYPE.INDI_NUMBER:
            self.elems[pelemid].value = event['event_object']['target']['value']
        elif ptype == INDI.INDI_PROPERTY_TYPE.INDI_TEXT:
            self.elems[pelemid].text = event['event_object']['target']['value']
    def getfunregister(self):
        return [('click', self.settercallback, '#'+self.propid+' .setter'), ('change', self.changevalueelement, '#'+self.propid+' input')]
    def gethtml(self):
        pname = self.prop.name
        plabel=self.prop.label
        ptype = self.prop.type
        #html='<div class="col-md-2" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"><h4><span id="prop-status-'+self.propid+'">'+htmlstatus+'</span> '+plabel+'</h4>'+'</div>'
        #html+='<div class="col-md-10 well">'
        html='<div class="col-md-10 well" id="'+self.propid+'">'
        if ptype != INDI.INDI_PROPERTY_TYPE.INDI_SWITCH:
            html+='<form class="form-horizontal">'
            html+='<fieldset><legend><span id="prop-status-'+self.propid+'">'+self.gethtmlstatus()+'</span> '+plabel
            if ptype != INDI.INDI_PROPERTY_TYPE.INDI_LIGHT and self.prop.perm != INDI.IPerm.IP_RO:
                html+='<span class="pull-right"><button class="btn btn-default setter" type="button" id="'+self.propid+'-set">Set All</button></span>'
            html+='</legend>'
        else:
            html+='<form class="form-horizontal">'
            html+='<fieldset><legend><span id="prop-status-'+self.propid+'">'+self.gethtmlstatus()+'</span> '+plabel+'</legend>'
            html+='<div class="btn btn-group">'
        index = 0
        for pelemname, pelem in self.prop.vp.items():
            #logging.info('adding '+pelemname)
            pelemid = self.propid+'-'+str(index)
            self.elems[pelemid]=pelem
            if ptype != INDI.INDI_PROPERTY_TYPE.INDI_SWITCH:
                html+='<div class="form-group"><div class="row">'
                html+='<div class="col-md-4"><label for="'+pelemid+'" class="control-label">'+pelem.label+'</label></div>'
            else:
                html+='<div class="btn-group">'
            #html+='<div class="col-md-10">'
            if ptype == INDI.INDI_PROPERTY_TYPE.INDI_NUMBER:
                if self.prop.perm != INDI.IPerm.IP_WO:
                    html+='<div class="col-md-4">'
                    html+='<div class="input-group">'
                    html+='<input id="'+pelemid+'-value" class="input-control" readonly value="'+str(pelem.value)+'">'
                    #html+='<span id="'+pelemid+'-value" class="input-group-addon">'+str(pelem.value)+'</span>'
                    html+='</div>'
                    html+='</div>'
                if self.prop.perm != INDI.IPerm.IP_RO:
                    html+='<div class="col-md-4">'
                    html+='<div class="input-group">'
                    html+='<input type="number" id="'+pelemid+'" class="form-control" placeholder="'+str(pelem.value)+'">'
                    html+='<span class="input-group-btn"><button class="btn btn-default setter" type="button" id="'+pelemid+'-set">Set</button></span>'
                    html+='</div>'
                    html+='</div>'
            elif ptype == INDI.INDI_PROPERTY_TYPE.INDI_SWITCH:
                if self.prop.rule == INDI.ISRule.ISR_NOFMANY:
                    btype = 'checkbox'
                else:
                    btype = 'button'
                if pelem.s == INDI.ISState.ISS_ON:
                    html+='<button type="'+btype+'" id="'+pelemid+'-set" class="btn btn-primary setter">'+pelem.label+'</button>'
                else:
                    html+='<button type="'+btype+'" id="'+pelemid+'-set" class="btn btn-default setter">'+pelem.label+'</button>'
            elif ptype == INDI.INDI_PROPERTY_TYPE.INDI_TEXT:
                #logging.info('text '+str(pelem.text)+' '+html.escape(str(pelem.text)))
                if self.prop.perm != INDI.IPerm.IP_WO:
                    html+='<div class="col-md-4">'
                    html+='<div class="input-group">'
                    html+='<input type="text" id="'+pelemid+'-value" class="input-control" readonly value="'+str(pelem.text)+'">'
                    #html+='<span id="'+pelemid+'-value" class="input-group-addon">'+str(pelem.text)+'</span>'
                    html+='</div>'
                    html+='</div>'
                if self.prop.perm != INDI.IPerm.IP_RO:
                    html+='<div class="col-md-4">'
                    html+='<div class="input-group">'
                    html+='<input type="text" id="'+pelemid+'" class="form-control" placeholder="'+str(pelem.text)+'">'
                    html+='<span class="input-group-btn"><button class="btn btn-default setter" type="button" id="'+pelemid+'-set">Set</button></span>'
                    html+='</div>'
                    html+='</div>'
            else:
                html+='<input type="text" id="'+pelemid+'" class="form-control">'
            #html+='</div>'
            html+='</div>'
            if ptype != INDI.INDI_PROPERTY_TYPE.INDI_SWITCH:
                html+='</div>'
            index +=1
        if ptype != INDI.INDI_PROPERTY_TYPE.INDI_SWITCH:
            #html+='</form>'
            html+='</fieldset></form>'
        else:
            html+='</div></fieldset></form>'
            #html+='</div>'
        html+='</div>'
        return html

    def refresh_ui(self, event):
        index = 0
        htmlreplaces=[]
        htmladdclass=[]
        htmlremoveclass=[]
        for pelemname, pelem in self.prop.vp.items():
            #logging.info('refreshing '+pelemname)
            pelemid = self.propid+'-'+str(index)
            v=''
            if self.prop.type == INDI.INDI_PROPERTY_TYPE.INDI_TEXT :
                v=pelem.text
                htmlreplaces.append(('#'+pelemid+'-value', v))
            elif self.prop.type == INDI.INDI_PROPERTY_TYPE.INDI_NUMBER:
                v=str(pelem.value)
                htmlreplaces.append(('#'+pelemid+'-value', v))
            elif self.prop.type == INDI.INDI_PROPERTY_TYPE.INDI_SWITCH:
                if pelem.s == INDI.ISState.ISS_OFF:
                    htmlremoveclass.append(('#'+pelemid+'-set', 'btn-primary'))
                    htmladdclass.append(('#'+pelemid+'-set', 'btn-default'))
                else:
                    htmlremoveclass.append(('#'+pelemid+'-set', 'btn-default'))
                    htmladdclass.append(('#'+pelemid+'-set', 'btn-primary'))
            index+=1
        return htmlreplaces, htmladdclass, htmlremoveclass

class DeviceUI:
    def __init__(self, device, deviceid, client):
        self.device = device
        self.deviceid = deviceid
        self.client=client
        self.tabs=dict()
        self.props=dict()
    def gethtml(self):
        htmldevice='<ul class="nav nav-pills nav-stacked col-md-2" id="pills'+str(self.deviceid)+'" data-spy="affix" data-offset-top="53"></ul>'
        html='<div class="tab-pane" role="tabpane" id="device'+str(self.deviceid)+'" >'+htmldevice+'<div id="device'+str(self.deviceid)+'-tab" class="tab-content col-md-10" role="tabpane"></div></div>'
        return html
    def addproperty(self, event):
        res=[]
        p=event.value
        pname=p.name
        ptab=p.group
        logging.info('adding property '+pname+' in '+ptab)
        if not ptab in self.tabs:
            ptabid='group-'+str(self.deviceid)+'-'+str(len(self.tabs))
            res.append(('#pills'+str(self.deviceid),\
                        '<li role="presentation"><a href="#'+ptabid+'" role="tab" data-toggle="tab">'+ ptab+'</a></li>'))
            self.tabs[ptab]=ptabid
            res.append(('#device'+str(self.deviceid)+'-tab', '<div id="'+ptabid+'" class="tab-pane fade" role="tab-content"></div>'))
        else:
            ptabid=self.tabs[ptab]
        propid='prop-'+str(self.deviceid)+'-'+str(len(self.props))
        self.props[pname] = PropertyUI(p, propid, self.client)
        res.append(('#'+ptabid, self.props[pname].gethtml()))
        return res, self.props[pname].getfunregister()

class ControlPanelUI:
    def __init__(self, sofi, navbar):
        self.sofi = sofi
        self.navbar = navbar
        self.devices=dict()
    def dispatch_indievent(self, event, client):
        logging.info(str(event)+' from '+client.host+':'+str(client.port))
        if event.type == IndiEventType.NEW_DEVICE:
            deviceid=len(self.devices)
            self.devices[event.device] = DeviceUI(event.device, deviceid, client)
            html='<li><a data-toggle="tab" href="#device'+str(deviceid)+'">'+event.device.name+'</a></li>'
            #self.sofi.append('#'+self.navbar+' > ul', html)
            self.sofi.append('#'+self.navbar, html)
            self.sofi.append("#device-tabs", self.devices[event.device].gethtml())
        if event.type == IndiEventType.NEW_PROPERTY:
            htmls, funs = self.devices[event.device].addproperty(event)
            for selector, html in htmls:
                self.sofi.append(selector, html)
            for ev, fun, selector in funs:
                self.sofi.register(ev, fun, selector)
        if (event.type == IndiEventType.NEW_TEXT) or (event.type == IndiEventType.NEW_NUMBER) or (event.type == IndiEventType.NEW_SWITCH):
            pname=event.value.name
            htmlreplaces=[]
            htmlreplaces, htmladdclass, htmlremoveclass=self.devices[event.device].props[pname].refresh_ui(event)
            for selector, html in htmlreplaces:
                self.sofi.attr(selector, 'value', html)
            for selector, cl in htmladdclass:
                self.sofi.addclass(selector, cl)
            for selector, cl in htmlremoveclass:
                self.sofi.removeclass(selector, cl)

class ControlPanel:
    def __init__(self, sofi):
        self.sofi = sofi
        self.servers = dict()
        self.inputs = dict()
        self.modals=[]
        self.navbar='navbar-devices'
        self.ui=ControlPanelUI(self.sofi, self.navbar)

    async def oninit(self, event):
        logging.info("MAIN")
        v = View("npindi control panel with sofi", bscss='assets/bootstrap.min-3.3.6.css', bsjs='assets/bootstrap.min-3.3.6.js', jquery='assets/jquery-2.2.4.js')

        n = Navbar(brand='npindi', fixed='top')

        p=Dropdown("Connections", cl='scrollable-menu', ident='connections', navbaritem=True)
        n.adddropdown(p)

        addindi=Button(None, cl="navbar-nav navbar-btn", attrs={"aria-label": "Add Indi server", "data-toggle": "modal", "data-target": "#add-connection-modal"})
        #glyphicons=Span(text=None, cl="glyphicon glyphicon-plus", attrs={"aria-hidden": "true"})
        glyphicons=FontAwesomeIcon(name="plus-square")
        addindi.addelement(glyphicons)
        addconnectionmodal="""
 <div id="add-connection-modal" class="modal fade">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                <h4 class="modal-title">New Conection</h4>
            </div>
            <div class="modal-body">
                <p>Enter INDI server host and port</p>
                <form>
                  <div class="form-group">
                    <label for="serverhost">Host</label>
                    <input type="text" class="form-control" id="serverhost" placeholder="localhost">
                  </div>
                  <div class="form-group">
                    <label for="serverport">Port</label>
                    <input type="number" class="form-control" id="serverport" placeholder="7624">
                  </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                <button type="button" id="connectserver" class="btn btn-primary" data-dismiss="modal">Connect</button>
            </div>
        </div>
    </div>
</div>
"""
        self.modals.append(addconnectionmodal)
        n.addelement(addindi)

        device_ul=UnorderedList(cl="nav navbar-nav nav-tabs", ident="navbar-devices")
        n.addelement(device_ul)

        v.addelement(n)

        c = Container(fluid=True, ident='container-main')

        devicetabs=Div(cl="tab-content", ident="device-tabs")
        c.newrow(devicetabs)

        v.addelement(c)

        self.sofi.load(str(v), event['client'])

    async def onload(self, event):
        for m in self.modals:
            self.sofi.append('body', m)
        self.sofi.append('head', """
<style>
.scrollable-menu .dropdown-menu {
    height: auto;
    max-height: 200px;
    overflow-x: hidden;
}
.affix {
    top: 50px;
    z-index: 9999 !important;
}
</style>
""");
        self.sofi.register('click', self.connectserver, selector='#connectserver', client=event['client'])
        self.sofi.register('input', self.inputchanged, selector='input', client=event['client'])
        logging.info("LOADED")

    async def connectserver(self, event):
        host = self.inputs['serverhost'] if 'serverhost' in self.inputs else 'localhost'
        port = self.inputs['serverport'] if 'serverport' in self.inputs else '7624'
        serverid = len(self.servers)
        logging.info("connecting to "+host+":"+port+' serverid '+str(serverid))
        #logger = logging.getLogger(host+":"+port)
        mediator=IndiEventAsyncioMediator(logger=None)
        client = IndiClient(logger=None, host=host, port=int(port), mediator=mediator)
        if not client.connect():
            logging.warning('INDI server '+str(serverid)+' not reachable')
            #del(self.servers[serverid])
            return
        dbutton=Button(text=None, ident='disconnect-server-'+str(serverid), size='xsmall', cl="pull-right", attrs={"aria-label": "Disconnect Indi server"})
        glyphicons=FontAwesomeIcon(name="minus-square")
        dbutton.addelement(glyphicons)
        serverui=Span(text=host+':'+port, ident='connection-ui-'+str(serverid))
        self.sofi.append('#connections-dropdown > ul', '<li id="connection-li-'+str(id)+'">'+str(serverui)+str(dbutton)+'</li>')
        self.sofi.register('click', (lambda event: self.disconnectserver(serverid)), selector='#disconnect-server-'+str(serverid), client=event['client'])
        consumer = asyncio.ensure_future(self.consume(client))
        self.servers[serverid] = {'client': client, 'consumer': consumer}

    async def disconnectserver(self, serverid):
        logging.info("disconnecting from "+str(serverid))
        #self.servers[serverid]['client'].disconnect()
        self.servers[serverid]['consumer'].cancel()
        del(self.servers[serverid])
        self.sofi.remove(selector='#connection-ui-'+str(serverid))
        self.sofi.remove(selector='#disconnect-server-'+str(serverid))
        self.sofi.remove(selector='#connection-li-'+str(serverid))

    async def consume(self, client):
        try:
            while True:
                item = await client.mediator.queue.get()
                logging.info(str(item))
                #self.sofi.append('#container-main', '<span>'+html.escape(str(item))+'</span><br/>')
                self.ui.dispatch_indievent(item, client)
                client.mediator.queue.task_done()
        except asyncio.CancelledError:
            logging.info('cancelling consumer')
            client.disconnect()
            while True:
                item = await client.mediator.queue.get()
                logging.info(str(item))
                self.sofi.append('#container-main', '<span>'+html.escape(str(item))+'</span><br/>')
                client.mediator.queue.task_done()
                if item.type==IndiEventType.SERVER_DISCONNECTED:
                    break

    async def inputchanged(self, event):
        logging.info("Input "+event['element']+" changed")
        self.inputs[event['element']] = event['event_object']['target']['value']

logging.basicConfig(format="%(asctime)s [%(levelname)s] - %(funcName)s: %(message)s", level=logging.INFO)

app = Sofi(singleclient=True)
control_panel = ControlPanel(app)
app.register('init', control_panel.oninit)
app.register('load', control_panel.onload)

app.start()
