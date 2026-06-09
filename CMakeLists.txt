cmake_minimum_required(VERSION 3.22)
project(gen3)

find_package(ament_cmake REQUIRED)

ament_package()

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/launch")
  install(
    DIRECTORY launch
    DESTINATION share/${PROJECT_NAME}
    PATTERN "setup_assistant.launch" EXCLUDE)
endif()

install(DIRECTORY config DESTINATION share/${PROJECT_NAME})
install(FILES .setup_assistant DESTINATION share/${PROJECT_NAME})
install(PROGRAMS
  scripts/motion_planning_python_api_tutorial.py
  DESTINATION lib/${PROJECT_NAME}
)
install(PROGRAMS
  scripts/ai_motion_planning.py
  DESTINATION lib/${PROJECT_NAME}
)
