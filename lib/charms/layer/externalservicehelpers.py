from charmhelpers.core import unitdata
from charms.reactive import set_state


def configure_externalname_service(ip, ports):
    """Sets the ip adress information for the external service
    in the unitdata key-value store.
    
    Args:
        ip (str): Ip adress or hostname
        ports (list): list of ports
    """
    unitdata.kv().set('external-service-ip', ip)
    unitdata.kv().set('external-service-ports', ports)
    needed_states = unitdata.kv().get('active-services', set())
    needed_states.add('externalname.service.start')
    unitdata.kv().set('active-services', list(needed_states))
    set_state('externalname.service.start')


def configure_headless_service(ips, port):
    """Configure headless service info.
    
    Args:
        ips (list): list with ip addresses
        port (int): port to access service
    """
    unitdata.kv().set('headless-service-ips', ips)
    unitdata.kv().set('headless-service-port', port)
    needed_states = unitdata.kv().get('active-services', set())
    needed_states.add('headless.service.start')
    unitdata.kv().set('active-services', list(needed_states))
    set_state('headless.service.start')
