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

from starcluster import clustersetup
from starcluster.logger import log


class SGEInstaller(clustersetup.DefaultClusterSetup):
    """
    This plugin installs SGE to the master node in the cluster. The
    path is specified in the plugin's config:

    [plugin sgeinstaller]
    setup_class = starcluster.plugins.sgeinstaller.SGEInstaller
    path = http://
    """
    def __init__(self, path=None):
        super(SGEInstaller, self).__init__()
        self.path = path
        self.dest = '/opt/sge6-fresh'

    def run(self, nodes, master, user, user_shell, volumes):
        if not self.path:
            log.info("No path specified!")
            return
        log.info('Installing SGE to master')

 #       master.ssh.execute('wget "%s" -O /tmp/sge.zip' % self.path)
        master.ssh.execute('curl "%s" -o /tmp/sge.zip' % self.path)
        master.ssh.execute('unzip -o -q /tmp/sge.zip -d /tmp/sge -x /')
        master.ssh.execute('mv /tmp/sge "%s"' % self.dest)
        master.ssh.execute('chmod -R  a+r "%s"' % self.dest)

