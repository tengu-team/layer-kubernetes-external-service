#!/usr/bin/env python3
# Copyright (C) 2017  Ghent University
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
from charmhelpers.core import hookenv, unitdata
from charmhelpers.core.hookenv import status_set, log
from charms.reactive import when, when_not, set_state, remove_state


@when_not('kubernetes-deployer.available')
def no_deployer_connected():
    status_set('blocked', 'Please connect the application to a kubernetes-deployer.')
    set_state('services.paused')


@when('kubernetes-deployer.available', 'externalname.service.start')
def deployer_connected_externalname(deployer):
    conf = hookenv.config()
    if not conf.get('service-name'):
        status_set('blocked', 'Please provide the service name.')
        return
    external_service_request = {
        'unit': os.environ['JUJU_UNIT_NAME'],
        'externalName': conf.get('service-name'),
        'ip': unitdata.kv().get('external-service-ip'),
        'ports': unitdata.kv().get('external-service-ports')
    }
    deployer.send_external_service_requests(external_service_request)
    status_set('waiting', 'Service request sent, waiting for deployment.')
    remove_state('externalname.service.start')


@when('kubernetes-deployer.available', 'headless.service.start')
def deployer_connected_headless(deployer):
    headless_service_request = {
        'unit': os.environ['JUJU_UNIT_NAME'],
        'ips': unitdata.kv().get('headless-service-ips'),
        'port': unitdata.kv().get('headless-service-port')
    }
    deployer.send_headless_service_request(headless_service_request)
    status_set('waiting', 'Service request sent, waiting for deployment.')
    remove_state('headless.service.start')


@when('kubernetes-deployer.available')
def service_running(deployer):
    conf = hookenv.config()
    external_service = deployer.get_services()
    if external_service:
        status_set('active', 'Ready external service')
        unitdata.kv().set('service_name', external_service['service_name'])
    else:
        unitdata.kv().set('service_name', '')


@when('kubernetes-deployer.joined')
def new_deployer(deployer):
    set_state('services.paused')


@when('services.paused', 'kubernetes-deployer.available')
def active_services(deployer):
    states = unitdata.kv().get('active-services', [])
    for state in states:
        set_state(state)
    remove_state('services.paused')
