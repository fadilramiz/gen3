from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_rsp_launch


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("GEN3-7DOF-VISION_ARM_URDF_V12", package_name="gen3").to_moveit_configs()
    return generate_rsp_launch(moveit_config)
