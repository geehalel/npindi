import logging
import signal
import sys
import time

from indi.client.indiclient import IndiClient
from indi.INDI import INDI
from indi.client.indievent import IndiEvent, IndiEventType

class ServiceExit(Exception):
    pass
def shutdown(signum, frame):
    print('Caught signal %d' % signum)
    raise ServiceExit

# Register the signal handlers
signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)
# logging default (stderr)
logging.basicConfig(format='%(asctime)s: %(name)-8s %(levelname)-8s %(message)s', level=logging.INFO)
logger = logging.getLogger('indiclient')
#mediator=IndiEventQueueMediator(logger=logger)
#client=BaseClient(mediator=mediator, logger=logger)
client=IndiClient(logger=logger)
if not client.connect():
    logger.warning('INDI server not reachable')
    sys.exit(1)
try:
    #DEVICE_NAME='EQMod Mount'
    DEVICE_NAME='CCD Simulator'
    client.wait_device(DEVICE_NAME, connect=False)
    device=client.devices[DEVICE_NAME]
    print(DEVICE_NAME,'is here', [p for p in client.devices[DEVICE_NAME].properties.keys()])
    rc=client.wait_properties(DEVICE_NAME, ['SIMULATION'])
    if rc:
        print('got SIMULATION property')
        simulation=device.properties['SIMULATION']
        simulation.vp['ENABLE'].s=INDI.ISState.ISS_ON
        simulation.vp['DISABLE'].s=INDI.ISState.ISS_OFF
        client.send_new_property(simulation)
    print('connecting')
    client.connect_device(device.name)
    print(DEVICE_NAME, 'is connected now.')
    print('Monitoring only', DEVICE_NAME, 'events')
    client.set_blob_mode(INDI.BLOBHandling.B_ALSO, device, None)
    indi_event=IndiEvent(None, device=device, value=None)
    while True:
        event=client.wait_indi_event(indi_event)
        print('got event', str(event))
        if event and event.type == IndiEventType.SERVER_DISCONNECTED:
            print('server disconnected')
            break;
        #time.sleep(0.1)
except ServiceExit:
    client.disconnect()
print('Exiting')
