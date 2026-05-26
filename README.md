# GEN3 7DOF ROS2 MoveIt Package

Robot Kinova GEN3 7DOF avec pince Panda, simulé dans Gazebo Harmonic avec MoveIt2.

## Dépendances
- ROS2 Jazzy
- MoveIt2
- Gazebo Harmonic (gz-sim 8)
- ros_gz_bridge

## Prerequis
Assurez vous le nom du package soit "gen3" 

## Lancement
```bash
colcon build --packages-select gen3
source install/setup.bash
ros2 launch gen3 moveit_gazebo.launch.py
```
