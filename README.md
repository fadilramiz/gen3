# GEN3 7DOF ROS2 MoveIt Package

Robot Kinova GEN3 7DOF avec pince Panda, simulé dans Gazebo Harmonic avec MoveIt2.

## Dépendances
- ROS2 Jazzy
- MoveIt2
- Gazebo Harmonic (gz-sim 8)
- ros_gz_bridge
- ollama (Pour le cas de "llama3.2b:1b")

## Prerequis
Assurez vous le nom du package soit "gen3"
Sourcez l'environnemet ROS2 et celui du package 

## Creation du package
```bash
colcon build --packages-select gen3
source install/setup.bash
```

## Lancement

### Cas_1:
```bash
ros2 launch gen3 moveit_planning.launch.py
```
Le robot effectura une simulation de pick and place avec des valeurs predefinies

###Cas_2:
```bash
ros2 launch gen3 moveit_planning.launch.py example_file:=ai_motion_planning.py
```
Le robot fonctionnera sous une IA locale "llama3.2b:1b" (venant de ollama), le but de celui-ci etant de recevoir un ordre et de l'executer.
Le prompt est predefini et contient 1 seule action pour l'instant.
