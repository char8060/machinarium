import utilities.GogoUtilities

SHELL_STEPS = sprintf('''#!/bin/bash -x
mkdir -p runway/FS_ROOT/etc/gogo
mkdir -p runway/FS_ROOT/application/bin
docker run --rm -v $(pwd):/mnt/ python:2 pip install --upgrade -t /mnt/src/ -r /mnt/requirements.txt
mkdir -p src/library
cp utilities/log_and_control/library/* src/library/
cd src
''')

def myJob = job("$SRC_JOB") {
    parameters {
        stringParam('GIT_BUILD_BRANCH', 'master', 'Git branch used to build.')
    }

    logRotator {
        numToKeep(5)
        artifactNumToKeep(5)
    }

    scm {
        git {
            remote {
                url("$REPO")
                credentials('gitlab-jenkinsci')
            }
            branch('*/master')
        }
    }

    steps {
        shell(SHELL_STEPS)
    }

}

g = new GogoUtilities(job: myJob).addBaseOptions('lambda').addGitLabPush()
