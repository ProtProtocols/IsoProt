# Instruction how to make a release

1.) Define files that are shipped to the user (as a zip file). So far, these are run.sh and run.bat
2.) Adapt all files that contain version numbers - ie. that need to be updated
* Adapt the README.md file to point to that version as the latest stable version (ie. update the shown docker pull command).
* Adapt the run.sh / run.cmd file to install the version by default
* Adapt the methods_generator module to print the correct version.
