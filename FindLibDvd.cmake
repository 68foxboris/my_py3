
# Check for existing LIBDVDREAD.
# Suppress mismatch warning, see https://cmake.org/cmake/help/latest/module/FindPackageHandleStandardArgs.html
+  set(_dvdlibs dvdread dvdnav)
+  set(_handlevars LIBDVD_INCLUDE_DIRS DVDREAD_LIBRARY DVDNAV_LIBRARY)
+  if(ENABLE_DVDCSS)
+    list(APPEND _dvdlibs libdvdcss)
+    list(APPEND _handlevars DVDCSS_LIBRARY)
+  endif()

  if(PKG_CONFIG_FOUND)
    pkg_check_modules(PC_DVD ${_dvdlibs} QUIET)
  endif()

  find_path(LIBDVD_INCLUDE_DIRS dvdnav/dvdnav.h PATHS ${PC_DVD_INCLUDE_DIRS})
  find_library(DVDREAD_LIBRARY NAMES dvdread libdvdread PATHS ${PC_DVD_dvdread_LIBDIR})
  find_library(DVDNAV_LIBRARY NAMES dvdnav libdvdnav PATHS ${PC_DVD_dvdnav_LIBDIR})
  if(ENABLE_DVDCSS)
    find_library(DVDCSS_LIBRARY NAMES dvdcss libdvdcss PATHS ${PC_DVD_libdvdcss_LIBDIR})
   endif()
  include(FindPackageHandleStandardArgs)
  find_package_handle_standard_args(LibDvd REQUIRED_VARS ${_handlevars})
  if(LIBDVD_FOUND)
    add_library(dvdnav UNKNOWN IMPORTED)
    set_target_properties(dvdnav PROPERTIES
                                  FOLDER "External Projects"
                                  IMPORTED_LOCATION "${DVDNAV_LIBRARY}")

    add_library(dvdread UNKNOWN IMPORTED)
    set_target_properties(dvdread PROPERTIES
                                  FOLDER "External Projects"
                                  IMPORTED_LOCATION "${DVDREAD_LIBRARY}")
    add_library(dvdcss UNKNOWN IMPORTED)
    set_target_properties(dvdcss PROPERTIES
                                  FOLDER "External Projects"
                                  IMPORTED_LOCATION "${DVDCSS_LIBRARY}")

    set(_linklibs ${DVDREAD_LIBRARY})
    if(ENABLE_DVDCSS)
      list(APPEND _linklibs ${DVDCSS_LIBRARY})
    endif()
    set(_linklibs ${DVDNAV_LIBRARY})
    set(LIBDVD_LIBRARIES ${DVDNAV_LIBRARY})
    mark_as_advanced(LIBDVD_INCLUDE_DIRS LIBDVD_LIBRARIES)
  endif()

mark_as_advanced(LIBDVD_INCLUDE_DIRS LIBDVD_LIBRARIES)
