Waziup platform Tests
=====================

This repository defines tests for the full Waziup platform.


Development
===========

The Jenkins scripts can be run locally with {Jenkinsfile-runner](https://github.com/jenkinsci/jenkinsfile-runner)
This allows to run the scripts without Jenkins.
For example:
```
jenkinsfile-runner -w ~/.jenkinsfile-runner/war/2.303.3 -p /var/lib/jenkins/plugins/ -f wazigate_images.jenkinsfile --runWorkspace workspace
```
