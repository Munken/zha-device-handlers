from zigpy.profiles import zha
from zigpy.zcl.clusters.general import Basic, PowerConfiguration, DeviceTemperature, Groups, Identify, OnOff, Scenes, \
    BinaryOutput, Time, Ota, AnalogInput, BinaryInput
from zigpy.zcl.clusters.homeautomation import ElectricalMeasurement

from zhaquirks import Bus, MODELS_INFO, ENDPOINTS, PROFILE_ID, DEVICE_TYPE, INPUT_CLUSTERS, OUTPUT_CLUSTERS
from zhaquirks.const import SKIP_CONFIGURATION, SHORT_PRESS, BUTTON_1, BUTTON_2, ARGS, COMMAND, BUTTON_3, BUTTON_4
from zhaquirks.xiaomi import XiaomiCustomDevice, LUMI, BasicCluster, ElectricalMeasurementCluster, AnalogInputCluster


class Plug(XiaomiCustomDevice):
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

    device_automation_triggers = {
        (SHORT_PRESS, BUTTON_1): {COMMAND: 'view', ARGS: [0, 0]},
        (SHORT_PRESS, BUTTON_2): {COMMAND: 'view', ARGS: [0, 1]},
        (SHORT_PRESS, BUTTON_3): {COMMAND: 'view', ARGS: [0, 2]},
        (SHORT_PRESS, BUTTON_4): {COMMAND: 'view', ARGS: [0, 3]},
    }