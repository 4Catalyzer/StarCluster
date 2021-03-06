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

from starcluster import exception
from starcluster.balancers import sge

from completers import ClusterCompleter

def _int(option, opt_str, value, parser):
    setattr(parser.values, option.dest, value)

class CmdLoadBalance(ClusterCompleter):
    """
    loadbalance <cluster_tag>

    Start the SGE Load Balancer.

    Example:

        $ starcluster loadbalance mycluster

    This command will endlessly attempt to monitor and load balance 'mycluster'
    based on the current SGE load. You can also have the load balancer plot the
    various stats it's monitoring over time using the --plot-stats option:

        $ starcluster loadbalance -p mycluster

    If you just want the stats data and not the plots use the --dump-stats
    option instead:

        $ starcluster loadbalance -d mycluster

    See "starcluster loadbalance --help" for more details on the '-p' and '-d'
    options as well as other options for tuning the SGE load balancer
    algorithm.
    """

    names = ['loadbalance', 'bal']

    def addopts(self, parser):
        parser.add_option("-d", "--dump-stats", dest="dump_stats",
                          action="store_true", default=False,
                          help="Output stats to a csv file at each iteration")
        parser.add_option("-D", "--dump-stats-file", dest="stats_file",
                          action="store", default=None,
                          help="File to dump stats to (default: %s)" %
                          sge.DEFAULT_STATS_FILE % "<cluster_tag>")
        parser.add_option("-p", "--plot-stats", dest="plot_stats",
                          action="store_true", default=False,
                          help="Plot usage stats at each iteration")
        parser.add_option("-P", "--plot-output-dir", dest="plot_output_dir",
                          action="store", default=None,
                          help="Output directory for stats plots "
                          "(default: %s)" % sge.DEFAULT_STATS_DIR %
                          "<cluster_tag>")
        parser.add_option("-i", "--interval", dest="interval",
                          action="callback", type="int", default=None,
                          callback=self._positive_int,
                          help="Load balancer polling interval in seconds "
                          "(max: 300s)")
        parser.add_option("-m", "--max_nodes", dest="max_nodes",
                          action="callback", type="int", default=None,
                          callback=self._positive_int,
                          help="Maximum # of nodes in cluster")
        parser.add_option("-w", "--job_wait_time", dest="wait_time",
                          action="callback", type="int", default=None,
                          callback=self._positive_int,
                          help=("Maximum wait time for a job before "
                                "adding nodes, seconds"))
        parser.add_option("-a", "--add_nodes_per_iter", dest="add_pi",
                          action="callback", type="int", default=None,
                          callback=self._positive_int,
                          help="Number of nodes to add per iteration")
        parser.add_option("-k", "--kill_after", dest="kill_after",
                          action="callback", type="int", default=None,
                          callback=self._positive_int,
                          help="Minutes after which a node can be killed")
        parser.add_option("-s", "--stabilization_time", dest="stab",
                          action="callback", type="int", default=None,
                          callback=self._positive_int,
                          help="Seconds to wait before cluster "
                          "stabilizes (default: 180)")
        parser.add_option("-l", "--lookback_window", dest="lookback_win",
                          action="callback", type="int", default=None,
                          callback=self._positive_int,
                          help="Minutes to look back for past job history")
        parser.add_option("-n", "--min_nodes", dest="min_nodes",
                          action="callback", type="int", default=None,
                          callback=_int,
                          help="Minimum number of nodes in cluster")
        parser.add_option("-K", "--kill-cluster", dest="kill_cluster",
                          action="store_true", default=False,
                          help="Terminate the cluster when the queue is empty")
        parser.add_option(
            "--reboot-interval", dest="reboot_interval", type="int",
            default=10, help="Delay in minutes beyond which a node is "
            "rebooted if it's still being unreachable via SSH. Defaults "
            "to 10.")
        parser.add_option(
            "--num_reboot_restart", dest="n_reboot_restart", type="int",
            default=False, help="Number of reboots after which a node "
            "is restarted (stop/start). Helpfull in case the issue comes from "
            "the hardware. If the node is a spot instance, it "
            "will be terminated instead since it cannot be stopped. Defaults "
            "to false.")
        parser.add_option(
            "--ignore-grp", dest="ignore_grp", action="store_true",
            default=False,
            help="if set, instances will not use the placement group")
        parser.add_option(
            "--image-id", dest="image_id", action="store", type="string",
            default=None, help="image id for new node(s) "
            "(e.g. ami-12345678).")
        parser.add_option(
            "--instance-type", dest="instance_type", default=None,
            help="If set, overrides which instance type newly added nodes "
                 "will use")
        parser.add_option(
            "--spot-bid", dest="spot_bid", default=None,
            help="If set, forces spot instances to be used and overrides "
                 "the maximum price placed.")
        parser.add_option("--slots_per_host", dest="slots_per_host",
                          action="callback", type="int", default=None,
                          callback=self._positive_int,
                          help="slots_per_host in cluster")

    def execute(self, args):
        if not self.cfg.globals.enable_experimental:
            raise exception.ExperimentalFeature("The 'loadbalance' command")
        if len(args) != 1:
            self.parser.error("please specify a <cluster_tag>")

        try:
            cluster_tag = args[0]
            cluster = self.cm.get_cluster(cluster_tag)
            template = self.cm.get_default_cluster_template()
            plugins = self.cm.get_cluster_template(template, cluster_tag).plugins
            cluster.plugins = plugins

            refresh_interval = self.cfg.globals.get("refresh_interval")
            if refresh_interval:
                cluster.refresh_interval = refresh_interval

            # Run this after we rebind plugins
            cluster.recover(self.opts.reboot_interval,
                            self.opts.n_reboot_restart)

            lb = sge.SGELoadBalancer(**self.specified_options_dict)
            lb.run(cluster)
        except KeyboardInterrupt:
            import traceback
            # traceback.format_exc()
            self.log.info(traceback.format_exc())
