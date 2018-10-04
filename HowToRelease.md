# Instruction how to make a release

## Preparations

  * Update README.md file to point to that version as the latest stable version (ie. update the shown docker pull command)
  * Adapt the methods_generator module to print the correct version
  * Add a repository tag with `git tag -a X.X.X -m "Version X.X.X"`

## Release process

  * Release to DockerHub using the above version
  * Release an updated version of `docker-launcher` to support the new version
