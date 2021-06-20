import logging
import time
from typing import Union, Optional, List, Any

from zigpy import types as t
from zigpy.profiles import zha
from zigpy.quirks import CustomDevice, CustomCluster
from zigpy.zcl import foundation as foundation
from zigpy.zcl.clusters.general import Basic, OnOff, Scenes

from zhaquirks import ENDPOINTS, PROFILE_ID, DEVICE_TYPE, INPUT_CLUSTERS, OUTPUT_CLUSTERS
from zhaquirks.const import SKIP_CONFIGURATION, SHORT_PRESS, BUTTON_1, BUTTON_2, ARGS, COMMAND, BUTTON_3, BUTTON_4, \
    BUTTON, PRESS_TYPE, COMMAND_ID, ZHA_SEND_EVENT, SHORT_RELEASE, LONG_RELEASE
from zhaquirks.philips import ButtonPressQueue

PRESS = "press"

_LOGGER = logging.getLogger(__name__)

class SunricherGpCluster(CustomCluster, Scenes):

    #KEYMAP = {3: 0, 6: 0, 2: 1, 7: 1, 0: 2, 4: 2, 1: 3, 5: 3}
    KEYMAP = {
        # Single button presses
        0x10: (2, "press"),
        0x11: (3, "press"),
        0x12: (1, "press"),
        0x13: (0, "press"),
        0x14: (2, "release"),
        0x15: (3, "release"),
        0x16: (1, "release"),
        0x17: (0, "release"),

        # Simultaneous press of 0 and 2
        0x62: (4, "press"),
        0x63: (4, "release"),
        # Simultaneous press of 1 and 3
        0x64: (5, "press"),
        0x65: (5, "release"),

        # Simultaneous press of 0 and 3
        0x68: (6, "press"),
    }

    cluster_id = 0x05

    button_press_queue = ButtonPressQueue()

    press_time = [0] * 7

    def handle_cluster_request(self, hdr: foundation.ZCLHeader, args: List[Any], *, dst_addressing: Optional[
        Union[t.Addressing.Group, t.Addressing.IEEE, t.Addressing.NWK]
    ] = None):
        _LOGGER.debug(
            "SunricherGpCluster - handle_cluster_request tsn: [%s] command id: %s - args: [%s]",
            hdr.tsn,
            hex(hdr.command_id),
            args,
        )

        button, press_type = self.KEYMAP.get(hdr.command_id, (None, None))
        _LOGGER.debug("%s", button)

        if button is None:
            return

        now = time.time()

        if press_type == PRESS:
            self.press_time[button] = now
        else:
            if now - self.press_time[button] < 0.3:
                press_type = "short_release"
            else:
                press_type = "long_release"

        event_args = {
            BUTTON: button,
            PRESS_TYPE: press_type,
            COMMAND_ID: hdr.command_id,
            ARGS: args,
        }

        action = f"button{button}_{press_type}"
        self.listener_event(ZHA_SEND_EVENT, action, event_args)
        _LOGGER.debug("Post!")




class ZGPSwitch(CustomDevice):
    """lumi.plug.maus01 plug."""

    signature = {
        SKIP_CONFIGURATION: True,
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: 0xa1e0,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    Scenes.cluster_id,
                    OnOff.cluster_id,
                ],
            },

            242: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: 0x0002,
                INPUT_CLUSTERS: [
                    0x0021,
                ],
                OUTPUT_CLUSTERS: [

                ],
            }
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: 0xa1e0,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    SunricherGpCluster
                ],
            },

            242: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: 0x0002,
                INPUT_CLUSTERS: [
                    0x0021,
                ],
                OUTPUT_CLUSTERS: [

                ],
            }
        },
    }

    device_automation_triggers = {
        (SHORT_PRESS,   BUTTON_1): {COMMAND: "button0_press"},
        (SHORT_PRESS,   BUTTON_2): {COMMAND: "button1_press"},
        (SHORT_PRESS,   BUTTON_3): {COMMAND: "button2_press"},
        (SHORT_PRESS,   BUTTON_4): {COMMAND: "button3_press"},
        (SHORT_RELEASE, BUTTON_1): {COMMAND: "button0_short_release"},
        (SHORT_RELEASE, BUTTON_2): {COMMAND: "button1_short_release"},
        (SHORT_RELEASE, BUTTON_3): {COMMAND: "button2_short_release"},
        (SHORT_RELEASE, BUTTON_4): {COMMAND: "button3_short_release"},
        (LONG_RELEASE,  BUTTON_1): {COMMAND: "button0_long_release"},
        (LONG_RELEASE,  BUTTON_2): {COMMAND: "button1_long_release"},
        (LONG_RELEASE,  BUTTON_3): {COMMAND: "button2_long_release"},
        (LONG_RELEASE,  BUTTON_4): {COMMAND: "button3_long_release"},
    }