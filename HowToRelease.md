# Instruction how to make a release

## Preparations

  * Update README.md file to point to that version as the latest stable version (ie. update the shown docker pull command)
  * Adapt the methods_generator module to print the correct version
  * Add a repository tag with `git tag -a X.X -m "Version X.X"`

## Release

  * Build image and release to DockerHub using the the format: `release-X.X`
  * Release an updated version of `docker-launcher` to support the new version
    * Note: docker-launcher will automatically detect the new version based on the GitHub tag but as a fallback uses an interal list as well.

## Move to next development version

  * Adapt methods_generator module to print development version - this will be displayed in the ":latest" image.
    * Format: X.X.X-latest

## Update GitHub repository

```
git push
git push --tags
```

**Note**: `docker-launcher` will automatically detect new image versions based on the
available tags in the repository. Therefore, the new tag must only be pushed to the repository once
the docker image with that version is available (using the `release-X.X` format).
