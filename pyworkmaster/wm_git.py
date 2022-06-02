from git import Repo


def status(config, project):
    if path := config[project]["variables"].get("PATH"):
        repo = Repo(path)
        branch = repo.active_branch

        # ’A’ for added paths
        # ’D’ for deleted paths
        # ’R’ for renamed paths
        # ’M’ for paths with modified data
        # ’T’ for changed in the type paths

        diffs = [diff.change_type for diff in repo.index.diff(None)]
        status = {
            'untracked': len(repo.untracked_files),
            'added': diffs.count('A'),
            'renamed': diffs.count('R'),
            'deleted': diffs.count('D'),
            'modified': diffs.count('M'),
            'changed': diffs.count('T'),
        }
        return branch, status
