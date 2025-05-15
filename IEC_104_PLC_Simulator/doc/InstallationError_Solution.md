# **Problem and Solution**

**In this document we will share the valuable problems and the solution we meet during the project development as a reference menu for the new programmer who may take over this project for further development. Later we will sort the problem based on the problem <type>.**

[TOC]

------

### Problem[0] Pip Installation compile Error

##### Error Message: 

```
C:\Users\liu_y>pip install c104
Collecting c104
  Using cached c104-2.2.1.tar.gz (2.0 MB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Building wheels for collected packages: c104
  Building wheel for c104 (pyproject.toml) ... error
  error: subprocess-exited-with-error

  × Building wheel for c104 (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [166 lines of output]
      running bdist_wheel
      running build
      running build_py
      creating build
      creating build\lib.win32-cpython-37
      creating build\lib.win32-cpython-37\c104
      copying c104\__init__.py -> build\lib.win32-cpython-37\c104
      running egg_info
      writing c104.egg-info\PKG-INFO
      writing dependency_links to c104.egg-info\dependency_links.txt
      writing top-level names to c104.egg-info\top_level.txt
      reading manifest file 'c104.egg-info\SOURCES.txt'
      reading manifest template 'MANIFEST.in'
      C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\config\pyprojecttoml.py:66: _BetaConfiguration: Support for `[tool.setuptools]` in `pyproject.toml` is still *beta*.
        config = read_configuration(filepath, True, ignore_option_errors, dist)
      warning: no previously-included files found matching 'src\main_client.cpp'
      warning: no previously-included files found matching 'src\main_server.cpp'
      warning: no previously-included files found matching 'c104\__pycache__'
      warning: no previously-included files matching '**\.*' found anywhere in distribution
      no previously-included directories found matching '**\tests'
      adding license file 'LICENSE'
      writing manifest file 'c104.egg-info\SOURCES.txt'
      copying c104\__init__.pyi -> build\lib.win32-cpython-37\c104
      copying c104\py.typed -> build\lib.win32-cpython-37\c104
      running build_ext
      -- Building for: Visual Studio 17 2022
      -- Selecting Windows SDK version 10.0.22621.0 to target Windows 10.0.22631.
      -- The CXX compiler identification is MSVC 19.43.34810.0
      -- Detecting CXX compiler ABI info
      -- Detecting CXX compiler ABI info - failed
      -- Check for working CXX compiler: D:/Tools/vs2022buildTool/VC/Tools/MSVC/14.43.34808/bin/Hostx64/x86/cl.exe
      -- Check for working CXX compiler: D:/Tools/vs2022buildTool/VC/Tools/MSVC/14.43.34808/bin/Hostx64/x86/cl.exe - broken
      CMake Error at C:/Users/liu_y/AppData/Local/Temp/pip-build-env-rlrgd4gg/overlay/Lib/site-packages/cmake/data/share/cmake-3.27/Modules/CMakeTestCXXCompiler.cmake:60 (message):
        The C++ compiler

          "D:/Tools/vs2022buildTool/VC/Tools/MSVC/14.43.34808/bin/Hostx64/x86/cl.exe"

        is not able to compile a simple test program.

        It fails with the following output:

          Change Dir: 'C:/Users/liu_y/AppData/Local/Temp/pip-install-6jactpyi/c104_c93a202a653747c2828bd37318b629b0/build/temp.win32-cpython-37/Release/c104._c104/CMakeFiles/CMakeScratch/TryCompile-x974d0'

          Run Build Command(s): D:/Tools/vs2022buildTool/MSBuild/Current/Bin/amd64/MSBuild.exe cmTC_e4c2b.vcxproj /p:Configuration=Debug /p:Platform=Win32 /p:VisualStudioVersion=17.0 /v:n
          MSBuild version 17.13.19+0d9f5a35a for .NET Framework
          Build started 29/4/2025 9:22:01 am.

          Project "C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj" on node 1 (default targets).
          PrepareForBuild:
            Creating directory "cmTC_e4c2b.dir\Debug\".
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppBuild.targets(544,5): warning MSB8029: The Intermediate directory or Output directory cannot reside under the Temporary directory as it could lead to issues with incremental build. [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
            Structured output is enabled. The formatting of compiler diagnostics will reflect the error hierarchy. See https://aka.ms/cpp/structured-output for more details.
            Creating directory "C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\Debug\".
            Creating directory "cmTC_e4c2b.dir\Debug\cmTC_e4c2b.tlog\".
          InitializeBuildStatus:
            Creating "cmTC_e4c2b.dir\Debug\cmTC_e4c2b.tlog\unsuccessfulbuild" because "AlwaysCreate" was specified.
            Touching "cmTC_e4c2b.dir\Debug\cmTC_e4c2b.tlog\unsuccessfulbuild".
          ClCompile:
            D:\Tools\vs2022buildTool\VC\Tools\MSVC\14.43.34808\bin\HostX64\x86\CL.exe /c /Zi /W1 /WX- /diagnostics:column /Od /Ob0 /Oy- /D _MBCS /D WIN32 /D _WINDOWS /D "CMAKE_INTDIR=\"Debug\"" /Gm- /EHsc /RTC1 /MDd /GS /fp:precise /Zc:wchar_t /Zc:forScope /Zc:inline /GR /Fo"cmTC_e4c2b.dir\Debug\\" /Fd"cmTC_e4c2b.dir\Debug\vc143.pdb" /external:W1 /Gd /TP /analyze- /errorReport:queue "C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\testCXXCompiler.cxx"
            Microsoft (R) C/C++ Optimizing Compiler Version 19.43.34810 for x86
            Copyright (C) Microsoft Corporation.  All rights reserved.
            cl /c /Zi /W1 /WX- /diagnostics:column /Od /Ob0 /Oy- /D _MBCS /D WIN32 /D _WINDOWS /D "CMAKE_INTDIR=\"Debug\"" /Gm- /EHsc /RTC1 /MDd /GS /fp:precise /Zc:wchar_t /Zc:forScope /Zc:inline /GR /Fo"cmTC_e4c2b.dir\Debug\\" /Fd"cmTC_e4c2b.dir\Debug\vc143.pdb" /external:W1 /Gd /TP /analyze- /errorReport:queue "C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\testCXXCompiler.cxx"
            testCXXCompiler.cxx
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003: The specified task executable "CL.exe" could not be run. System.IO.DirectoryNotFoundException: Could not find a part of the path 'C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.dir\Debug\cmTC_e4c2b.tlog'. [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at System.IO.__Error.WinIOError(Int32 errorCode, String maybeFullPath) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at System.IO.FileSystemEnumerableIterator`1.CommonInit() [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at System.IO.FileSystemEnumerableIterator`1..ctor(String path, String originalUserPath, String searchPattern, SearchOption searchOption, SearchResultHandler`1 resultHandler, Boolean checkHost) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at System.IO.Directory.GetFiles(String path, String searchPattern) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at Microsoft.Build.Utilities.TrackedDependencies.ExpandWildcards(ITaskItem[] expand) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at Microsoft.Build.CPPTasks.TrackedVCToolTask.DeleteFiles(ITaskItem[] filesToDelete) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at Microsoft.Build.CPPTasks.CL.PostExecuteTool(Int32 exitCode) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at Microsoft.Build.CPPTasks.TrackedVCToolTask.ExecuteTool(String pathToTool, String responseFileCommands, String commandLineCommands) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at Microsoft.Build.CPPTasks.CL.ExecuteTool(String pathToTool, String responseFileCommands, String commandLineCommands) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at Microsoft.Build.Utilities.ToolTask.Execute() [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          Done Building Project "C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj" (default targets) -- FAILED.

          Build FAILED.

          "C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj" (default target) (1) ->
          (PrepareForBuild target) ->
            D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppBuild.targets(544,5): warning MSB8029: The Intermediate directory or Output directory cannot reside under the Temporary directory as it could lead to issues with incremental build. [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]


          "C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj" (default target) (1) ->
          (ClCompile target) ->
            D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003: The specified task executable "CL.exe" could not be run. System.IO.DirectoryNotFoundException: Could not find a part of the path 'C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.dir\Debug\cmTC_e4c2b.tlog'. [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at System.IO.__Error.WinIOError(Int32 errorCode, String maybeFullPath) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at System.IO.FileSystemEnumerableIterator`1.CommonInit() [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at System.IO.FileSystemEnumerableIterator`1..ctor(String path, String originalUserPath, String searchPattern, SearchOption searchOption, SearchResultHandler`1 resultHandler, Boolean checkHost) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at System.IO.Directory.GetFiles(String path, String searchPattern) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at Microsoft.Build.Utilities.TrackedDependencies.ExpandWildcards(ITaskItem[] expand) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at Microsoft.Build.CPPTasks.TrackedVCToolTask.DeleteFiles(ITaskItem[] filesToDelete) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at Microsoft.Build.CPPTasks.CL.PostExecuteTool(Int32 exitCode) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at Microsoft.Build.CPPTasks.TrackedVCToolTask.ExecuteTool(String pathToTool, String responseFileCommands, String commandLineCommands) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at Microsoft.Build.CPPTasks.CL.ExecuteTool(String pathToTool, String responseFileCommands, String commandLineCommands) [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]
          D:\Tools\vs2022buildTool\MSBuild\Microsoft\VC\v170\Microsoft.CppCommon.targets(781,5): error MSB6003:    at Microsoft.Build.Utilities.ToolTask.Execute() [C:\Users\liu_y\AppData\Local\Temp\pip-install-6jactpyi\c104_c93a202a653747c2828bd37318b629b0\build\temp.win32-cpython-37\Release\c104._c104\CMakeFiles\CMakeScratch\TryCompile-x974d0\cmTC_e4c2b.vcxproj]

              1 Warning(s)
              1 Error(s)

          Time Elapsed 00:00:00.37





        CMake will not be able to correctly generate this project.
      Call Stack (most recent call first):
        CMakeLists.txt:2 (project)


      -- Configuring incomplete, errors occurred!
      Traceback (most recent call last):
        File "C:\Users\liu_y\AppData\Local\Programs\Python\Python37-32\lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 353, in <module>
          main()
        File "C:\Users\liu_y\AppData\Local\Programs\Python\Python37-32\lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 335, in main
          json_out['return_val'] = hook(**hook_input['kwargs'])
        File "C:\Users\liu_y\AppData\Local\Programs\Python\Python37-32\lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 252, in build_wheel
          metadata_directory)
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\build_meta.py", line 417, in build_wheel
          wheel_directory, config_settings)
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\build_meta.py", line 401, in _build_with_temp_dir
          self.run_setup()
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\build_meta.py", line 338, in run_setup
          exec(code, locals())
        File "<string>", line 128, in <module>
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\__init__.py", line 107, in setup
          return distutils.core.setup(**attrs)
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\_distutils\core.py", line 185, in setup
          return run_commands(dist)
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\_distutils\core.py", line 201, in run_commands
          dist.run_commands()
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\_distutils\dist.py", line 969, in run_commands
          self.run_command(cmd)
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\dist.py", line 1234, in run_command
          super().run_command(command)
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\_distutils\dist.py", line 988, in run_command
          cmd_obj.run()
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\wheel\bdist_wheel.py", line 368, in run
          self.run_command("build")
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\_distutils\cmd.py", line 318, in run_command
          self.distribution.run_command(command)
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\dist.py", line 1234, in run_command
          super().run_command(command)
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\_distutils\dist.py", line 988, in run_command
          cmd_obj.run()
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\_distutils\command\build.py", line 131, in run
          self.run_command(cmd_name)
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\_distutils\cmd.py", line 318, in run_command
          self.distribution.run_command(command)
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\dist.py", line 1234, in run_command
          super().run_command(command)
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\_distutils\dist.py", line 988, in run_command
          cmd_obj.run()
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\command\build_ext.py", line 84, in run
          _build_ext.run(self)
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\_distutils\command\build_ext.py", line 345, in run
          self.build_extensions()
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\_distutils\command\build_ext.py", line 467, in build_extensions
          self._build_extensions_serial()
        File "C:\Users\liu_y\AppData\Local\Temp\pip-build-env-rlrgd4gg\overlay\Lib\site-packages\setuptools\_distutils\command\build_ext.py", line 493, in _build_extensions_serial
          self.build_extension(ext)
        File "<string>", line 120, in build_extension
        File "C:\Users\liu_y\AppData\Local\Programs\Python\Python37-32\lib\subprocess.py", line 512, in run
          output=stdout, stderr=stderr)
      subprocess.CalledProcessError: Command '['cmake', 'C:\\Users\\liu_y\\AppData\\Local\\Temp\\pip-install-6jactpyi\\c104_c93a202a653747c2828bd37318b629b0', '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=C:\\Users\\liu_y\\AppData\\Local\\Temp\\pip-install-6jactpyi\\c104_c93a202a653747c2828bd37318b629b0\\build\\lib.win32-cpython-37\\c104\\', '-DPython_EXECUTABLE=C:\\Users\\liu_y\\AppData\\Local\\Programs\\Python\\Python37-32\\python.exe', '-DCMAKE_BUILD_TYPE=Release', '-DC104_VERSION_INFO=2.2.1', '-A', 'Win32', '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE=C:\\Users\\liu_y\\AppData\\Local\\Temp\\pip-install-6jactpyi\\c104_c93a202a653747c2828bd37318b629b0\\build\\lib.win32-cpython-37\\c104']' returned non-zero exit status 1.
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for c104
Failed to build c104
ERROR: Could not build wheels for c104, which is required to install pyproject.toml-based projects

[notice] A new release of pip is available: 23.2.1 -> 24.0
[notice] To update, run: python.exe -m pip install --upgrade pip

```

### Problem Summary

Your `pip install c104` **failed during the build step** because **MSVC (Visual Studio Compiler) failed to compile a test C++ program**.
 The **critical error** was:

```
luaCopyEditerror MSB6003: The specified task executable "CL.exe" could not be run. 
System.IO.DirectoryNotFoundException: Could not find a part of the path ...
```

Specifically, **the temporary build directory structure is broken or missing** during the build, causing `CL.exe` (the compiler) to fail.

------

### Why did this happen?

1. **Building in a Temporary Folder**
    CMake and MSBuild are trying to compile *inside a Windows Temp directory* (`C:\Users\liu_y\AppData\Local\Temp\pip-install-fawa38fe\...`).
    But **MSBuild warns that building inside Temp is risky** (`MSB8029` warning), because temporary directories may get cleaned up automatically or blocked.
2. **Incorrect/Partial Visual Studio Build Tools Setup**
   - You are using **Visual Studio 2022 Build Tools** (`VS 17 2022`), but maybe only minimal C++ components are installed.
   - Missing important **C++ build workload** or **Windows 10 SDK components** needed for pip/CMake builds.
3. **Architecture Mismatch**
    Your Python is **32-bit (win32-cpython-37)** but your Visual Studio toolchain is trying to run 64-bit (`HostX64`) tools targeting `x86` (32-bit).
    Still theoretically okay — but **if some libraries are missing 32-bit support**, problems happen.

------

### How to fix it?

Here are the steps:

✅ **1. Install Full C++ Build Environment**

You must **repair or add components** to your Build Tools installation:

- Open **Visual Studio Installer** → Modify **Build Tools for Visual Studio 2022**.
- Make sure these are selected:
  - ✅ Desktop development with C++
  - ✅ MSVC v143 - VS 2022 C++ x86/x64 build tools
  - ✅ Windows 10 SDK (10.0.22621.0)
  - ✅ C++ CMake tools for Windows
  - ✅ C++ ATL for x86 and x64

✅ **2. Avoid building in TEMP folders**

Force `pip` to use a *local* build directory rather than Temp by setting:

```bash
pip install c104 --no-cache-dir --no-build-isolation
```

Or manually clone it:

```
bashCopyEditgit clone https://github.com/<repo>/c104
cd c104
pip install .
```

(Replace `<repo>` if known.)

✅ **3. Confirm Python matches Visual Studio Architecture**

- If your Python is 32-bit (shows `win32`), you might prefer to install 64-bit Python (`amd64`) if your VS Build Tools is 64-bit focused.

Check your Python version with:

```bash
python -c "import platform; print(platform.architecture())"
```

If it shows **32-bit**, consider installing 64-bit Python 3.7/3.8.

✅ **4. Setup proper environment (vcvarsall.bat)**

Before installing:

```bash
"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars32.bat"
```

or

```bash
"C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x86
```

to load environment variables for compiler correctly.