# GEN3 7DOF ROS2 MoveIt Package

Robot Kinova GEN3 7DOF avec pince Panda, simulé dans Gazebo Harmonic avec MoveIt2.

## Dépendances
- ROS2 Jazzy
- MoveIt2
- Gazebo Harmonic (gz-sim 8)
- ros_gz_bridge
- ollama (Pour le cas de "qwen3:8b")

## Prerequis
Assurez vous le nom du package soit "gen3"
Sourcez l'environnemet ROS2 et celui du package 

## Creation du package
```bash
colcon build --packages-select gen3
source install/setup.bash
```

## Lancement

Dependement de l'option que vous voulez il y a 3 cas possibles

### Cas_1:
Dans un terminal, executer :
```bash
ros2 launch gen3 moveit_planning.launch.py
```

Puis dans un second terminal, executer : 
```bash
ros2 run gen3 ros_server_client.py
```
Ensuite tapez votre requete, exemple : ```Move the arm of the robot to 0.4 0.2 0.4```
Le robot effectura en simulation le deplacement vers l'endroit defini

### Cas_2:
```bash
ros2 launch gen3 moveit_planning.launch.py example_file:=ai_motion_planning.py
```
Le robot fonctionnera sous une IA locale "qwen3:8b" (venant de ollama), le but de celui-ci etant de recevoir un ordre et de l'executer.
Le prompt est predefini et contient 1 seule action pour l'instant, pareil au cas 1 avec des limitations.

### Cas_3
```bash
ros2 launch gen3 moveit_planning.launch.py example_file:=motion_planning_python_api_tutorial.py
```
Le robot effectuera une simulation de pick and place en continu
