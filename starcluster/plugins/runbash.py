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
"""
from starcluster.clustersetup import DefaultClusterSetup
from starcluster.logger import log
from starcluster.utils import print_timing


class BashRunner(DefaultClusterSetup):
    """Bash Runner"""

    def __init__(self, bash_file=None, forward_ssh_agent=False, master_only=False):
        super(BashRunner, self).__init__()
        self.bash_file = bash_file
        if isinstance(forward_ssh_agent, basestring):
            self.forward_ssh_agent = forward_ssh_agent.lower().strip() == 'true'
        else:
            self.forward_ssh_agent = forward_ssh_agent

        if isinstance(master_only, basestring):
            self.master_only = master_only.lower().strip() == 'true'
        else:
            self.master_only = master_only

    @print_timing("BashRunner")
    def run_bash(self, nodes):
        if not self.bash_file:
            log.info("No bash file specified!")
            return

        msg = "Running bash file: %s" % self.bash_file
        if self.forward_ssh_agent:
            msg += " with forward_ssh_agent"
        log.info(msg)
        with open(self.bash_file, 'r') as fp:
            commands = fp.readlines()

        for command in commands:
            log.info("$ %s" % command.strip())
        cmd = "\n".join(commands)
        for node in nodes:
            self.pool.simple_job(node.ssh.execute,
                args=(cmd,),
                kwargs={'forward_ssh_agent': self.forward_ssh_agent},
                jobid=node.alias)
        self.pool.wait(len(nodes))

    def run(self, nodes, master, user, user_shell, volumes):
        if self.master_only:
            self.run_bash([master])
        else:
            self.run_bash(nodes)

    def on_add_node(self, node, nodes, master, user, user_shell, volumes):
        if not self.master_only:
            self.run_bash([node])

    def on_remove_node(self, node, nodes, master, user, user_shell, volumes):
        raise NotImplementedError("on_remove_node method not implemented")
