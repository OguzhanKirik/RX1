#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "rx1_motor::rx1_motor" for configuration ""
set_property(TARGET rx1_motor::rx1_motor APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(rx1_motor::rx1_motor PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_NOCONFIG "CXX"
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/librx1_motor.a"
  )

list(APPEND _cmake_import_check_targets rx1_motor::rx1_motor )
list(APPEND _cmake_import_check_files_for_rx1_motor::rx1_motor "${_IMPORT_PREFIX}/lib/librx1_motor.a" )

# Import target "rx1_motor::rx1_motor_node" for configuration ""
set_property(TARGET rx1_motor::rx1_motor_node APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(rx1_motor::rx1_motor_node PROPERTIES
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/rx1_motor/rx1_motor_node"
  )

list(APPEND _cmake_import_check_targets rx1_motor::rx1_motor_node )
list(APPEND _cmake_import_check_files_for_rx1_motor::rx1_motor_node "${_IMPORT_PREFIX}/lib/rx1_motor/rx1_motor_node" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
