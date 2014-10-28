# Copyright 2009-2014 Justin Riley
#
# This file is part of StarCluster.
#
# StarCluster is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# StarCluster is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with StarCluster. If not, see <http://www.gnu.org/licenses/>.

"""
A starcluster plugin for running Spearmint
"""
import json
import os
import time
import posixpath

from starcluster import utils
from starcluster import static
from starcluster import spinner
from starcluster import exception
from starcluster.utils import print_timing
from starcluster.clustersetup import DefaultClusterSetup

from starcluster.logger import log


class SMCluster(DefaultClusterSetup):
    """
    """
    def __init__(self, ports=[]):
        super(SMCluster, self).__init__()
        if isinstance(ports, basestring):
            self.ports = [int(port.strip()) for port in ports.strip().split(",")]
        else:
            self.ports = ports

    def _authorize_port(self, node, port, service_name, protocol='tcp'):
        group = node.cluster_groups[0]
        world_cidr = '0.0.0.0/0'
        if isinstance(port, tuple):
            port_min, port_max = port
        else:
            port_min, port_max = port, port
        port_open = node.ec2.has_permission(group, protocol, port_min,
                                            port_max, world_cidr)
        if not port_open:
            log.info("Authorizing tcp ports [%s-%s] on %s for: %s" %
                     (port_min, port_max, world_cidr, service_name))
            node.ec2.conn.authorize_security_group(
                group_id=group.id, ip_protocol='tcp', from_port=port_min,
                to_port=port_max, cidr_ip=world_cidr)

    @print_timing("SMCluster")
    def run(self, nodes, master, user, user_shell, volumes):
        for port in self.ports:
            self._authorize_port(master, port, 'spearmint')

    def on_add_node(self, node, nodes, master, user, user_shell, volumes):
        pass

    def on_remove_node(self, node, nodes, master, user, user_shell, volumes):
        pass


