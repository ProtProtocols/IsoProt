@echo off
setlocal enabledelayedexpansion
:: enabledelayedexpansion is used to exapnd variables like !var_name! (inside group statments)

set img_name=veitveit/isolabeledprotocol
set docker_cmd=docker.exe

:: TODO have an option to override with named parameter
set data=%cd%

:: Make sure docker is installed
where /Q %docker_cmd% || (
	echo Error: Canot find '%docker_cmd%' command.
	echo To install Docker on your system please visit: https://www.docker.com
	goto END_ERROR
)

:: Check if img_name exists
docker images | find "%img_name%" > NUL || (
	echo Docker image '%img_name%' is not installed.
	set /p install_img=Do you want to install it [y/n]?: 
	if "!install_img!" NEQ "y" goto END_ERROR

	:: installing image
	%docker_cmd% pull %img_name% || (
		echo Error: Failed to install docker image.
		goto END_ERROR
	)
)

:: Find open port starting from 8888
set  /A port=8888
:TEST_PORT
netstat -na | find ":%port%" | find "ESTABLISHED" > NUL || goto END_LOOP
set /A port=%port%+1
goto TEST_PORT
:END_LOOP


set ADRESS=http://localhost:%port%
echo Adress: %ADRESS%

start openBrowser "%ADRESS%"

:: This will not be used as it's not asynchronus
REM :TEST_SERVER
REM start /wait http.vbs http://localhost:%port%
REM if "%ERRORLEVEL%" NEQ "0" goto :TEST_SERVER
REM :: server is runing, open the browser
REM start "" %URL%

if not exist "OUT" mkdir OUT || (
		echo Error: Can't create folder OUT
		goto END_ERROR
	)

%docker_cmd% run -it -p %port%:%port% -v %data%:/data/ -v %data%/OUT:/home/biodocker/OUT %img_name% jupyter notebook --ip=0.0.0.0 --port=%port% --no-browser



:: Finished
exit /B 0

:END_ERROR
echo Run error
pause
exit /B 1
