import logging
import time
from typing import Union, Optional, Coroutine, List, Any

from zigpy import types as t
from zigpy.profiles import zha
from zigpy.quirks import CustomDevice, CustomCluster
from zigpy.zcl import foundation as foundation
from zigpy.zcl.clusters.general import Basic, PowerConfiguration, DeviceTemperature, Groups, Identify, OnOff, Scenes, \
    BinaryOutput, Time, Ota, AnalogInput, BinaryInput
from zigpy.zcl.clusters.homeautomation import ElectricalMeasurement

from zhaquirks import Bus, MODELS_INFO, ENDPOINTS, PROFILE_ID, DEVICE_TYPE, INPUT_CLUSTERS, OUTPUT_CLUSTERS
from zhaquirks.const import SKIP_CONFIGURATION, SHORT_PRESS, BUTTON_1, BUTTON_2, ARGS, COMMAND, BUTTON_3, BUTTON_4, \
    ENDPOINT_ID, LONG_PRESS, BUTTON, PRESS_TYPE, COMMAND_ID, ZHA_SEND_EVENT, SHORT_RELEASE, LONG_RELEASE

from zhaquirks.philips import ButtonPressQueue

_LOGGER = logging.getLogger(__name__)


class SunricherGpCluster(CustomCluster, Scenes):

    cluster_id = Scenes.cluster_id

    button_press_queue = ButtonPressQueue()

    press_time = [0] * 4

    def handle_cluster_request(self, hdr: foundation.ZCLHeader, args: List[Any], *, dst_addressing: Optional[
        Union[t.Addressing.Group, t.Addressing.IEEE, t.Addressing.NWK]
    ] = None):
        _LOGGER.debug(
            "SunricherGpCluster - handle_cluster_request tsn: [%s] command id: %s - args: [%s]",
            hdr.tsn,
            hdr.command_id,
            args,
        )

        button = args[1]
        phys_button = button % 4
        now = time.time()

        if button < 4:
            press_type = "press"
            self.press_time[phys_button] = now
        else:
            if now - self.press_time[phys_button] > 300:
                press_type = "short_release"
            else:
                press_type = "long_release"

        event_args = {
            BUTTON: button,
            PRESS_TYPE: press_type,
            COMMAND_ID: hdr.command_id,
            ARGS: args,
        }

        action = f"button{phys_button}_{press_type}"
        self.listener_event(ZHA_SEND_EVENT, action, event_args)




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
                    Scenes.cluster_id
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