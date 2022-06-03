# pyworkmaster
Work setup manager

Example config:
```yaml
# Located at ~/.config/workmaster/config.yml
variables:
    HOME: /home/trez/dev

test_project:
    variables:
        PATH: '{HOME}/{PROJECT}'
        CONDAENV: test_environment
        
    git:
        repo: https://github.com/trez/pyworkmaster
        
    # Workarea is split like this:
    #  +-----------+
    #  |     |  B  |
    #  |  A  |-----|
    #  |     |  C  |
    #  +-----------+
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
# List projects from config.yml and show their git status and current branch if possible.
$ workmaster
✓ test_project [master]

# Starts a screen session named 'test_project' with 3 windows named A, B and C.
# With a workspace split into 3 regions.
$ workmaster test_project attach

# Print config
$ workmaster test_project config
{'layout': |[A, /[B, C]],
 'variables': {'PROJECT': 'test_project', 'CONDAENV': 'test_environment'},
 'windows': {'A': [...],
             'B': [...],
             'C': [...]}}
```

## Install
```bash
$ pip install .
```

## Usage
### configuration
Default path for user configuration is set to '~/.config/workmaster/config.yml'.

Project specific configuration are read if located in current directory named '.workmaster.yml'.


### variables
Define variables that can be scoped on a global level or on a project level.

Variables can be nested in other variable definitions (order matters) and in window command specifications.

### windows
Titles can use any alphabet characters and can be longer than 1.

Use variable placeholders by encapsulate the variable with {}.

### layout
Define how a workspace should be split into regions where | denotes vertical split and / denotes horizontal splits.

The titles used corresponds to the defined titles in windows section of the configuration file.

Using parentheses indicate that the region should be further split into subregions.

If one wants to split a workspace into 3 regions do so by using definition A | B | C.

Not all windows need to be used in the layout.

### tasks
Run commands for a task in a specific window.

## Tips'n'tricks
### screenrc
```
# Switch region with mouse action.
mousetrack on
defmousetrack on

# Switch region using vim bindings.
bind h focus left
bind j focus down
bind k focus up
bind l focus right
bind t focus top
bind b focus bottom

# disable screen freezing, fixed by ctrl-a q, but anyways.
bind s 

# fix for not needing double ESC when running vim inside a screen session.
maptimeout 10

# status bar.
caption always "%{= kw}%-w%{= BW}%n %t%{-}%+w %-= @%H - %LD %d %LM - %c"

# use ctrl-b instead of ctrl-a.
escape ^Bb
```

### bashrc (auto complete)
```
_workmaster_cmds() {
    local known_projects cur sub_commands

    cur="${COMP_WORDS[COMP_CWORD]}"
    if [ $COMP_CWORD -lt 2 ]; then
        known_projects=$(workmaster -q)
    else
        known_projects=""
    fi
    sub_commands=$(${COMP_WORDS[@]:0:COMP_CWORD} --help | sed -n -e '/Subcommands:/,$p' | tail -n +2 | awk '{print $1}' | grep -Ewv '[[:upper:]]+')
    
    COMPREPLY=( $(compgen -W "$sub_commands $known_projects" -- ${cur}) )
    return 0
}

complete -F _workmaster_cmds workmaster
```
