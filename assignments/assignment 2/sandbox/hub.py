from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr

log = core.getLogger()

def _handle_ConnectionUp (event):

    msg = of.ofp_flow_mod()
    msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
    event.connection.send(msg)
    log.info("Hubifying %s", dpidToStr(event.dpid))

def launch ():

    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    log.info("Hub running.")

def send_packet (self, buffer_id, raw_data, out_port, in_port):

    """
    Sends a packet out of the specified switch port.
    If buffer_id is a valid buffer on the switch, use that.  Otherwise,
    send the raw data in raw_data.
    The "in_port" is the port number that packet arrived on.  Use
    OFPP_NONE if you're generating this packet.
    """

    msg = of.ofp_packet_out()
    msg.in_port = in_port

    if buffer_id != -1 and buffer_id is not None:
        # We got a buffer ID from the switch; use that
        msg.buffer_id = buffer_id
    else:
        # No buffer ID from switch -- we got the raw data
        if raw_data is None:
            # No raw_data specified -- nothing to send!
            return
        msg.data = raw_data

    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)

