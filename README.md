# pyworkmaster
Work setup manager

Example config:
```yaml
# Located at ~/.config/workmaster/config.yaml
variables:
    HOME: /home/trez/dev

test_project:
    variables:
        PATH: '{HOME}/{PROJECT}'
        CONDAENV: test_environment

    layout: A|(B/C)

    windows:
        A:
            - conda activate {CONDAENV}
            - cd {PATH}
            - nvim src/{PROJECT}/__main__.py
        B:
            - conda activate {CONDAENV}
            - cd {PATH}
            - git status
        C:
            - conda activate {CONDAENV}
            - cd {PATH}
            - echo {PROJECT}
```

Example commands:
```bash
# List projects from config.yaml
$ workmaster list
test_project

$ workmaster setup test_project
# Starts a screen session named 'test_project' with 3 windows named A, B and C.
# Workarea is split like this:
#  +-----------+
#  |     |  B  |
#  |  A  |-----|
#  |     |  C  |
#  +-----------+
```

## Install
```bash
$ pip install .
```
