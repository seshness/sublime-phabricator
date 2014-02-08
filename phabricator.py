import os
try:
    # Attempt to load Python 2 quote
    from urllib import quote
except ImportError:
    # Fallback to Python 3 quote
    from urllib.parse import quote
import sublime
import sublime_plugin
import subprocess


class PhabricatorOpenCommand(sublime_plugin.WindowCommand):
    def run(self):
        """Open a file inside of Phabricator with the selected lines."""
        # Get the first selection
        view = sublime.active_window().active_view()
        first_sel = view.sel()[0]

        # Find the lines that are selected
        # Logic taken from https://github.com/ehamiter/ST2-GitHubinator/blob/c3fce41aaf2fc564115f83f1afef672f9a173d58/githubinator.py#L44-L49
        begin_line = view.rowcol(first_sel.begin())[0] + 1
        end_line = view.rowcol(first_sel.end())[0] + 1
        if begin_line == end_line:
            lines = begin_line
        else:
            lines = '{0}-{1}'.format(begin_line, end_line)

        # Find the file directory and name
        filepath = view.file_name()
        filedir = os.path.dirname(filepath)
        filename = os.path.basename(filepath)

        # Get current branch
        git_args = ['git', 'symbolic-ref', 'HEAD']
        git_child = subprocess.Popen(
            git_args, cwd=filedir,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        git_stdout = str(git_child.stdout.read())
        git_stderr = str(git_child.stderr.read())
        if git_stderr:
            print('Ran `{0}` in `{1}`'.format(' '.join(git_args), filedir))
            print('STDERR: {0}'.format(git_stderr))

        # Format the current branch
        # `refs/heads/dev/my.branch` -> `dev/my.branch` -> `dev%2Fmy.branch` -> `dev%252Fmy.branch`
        git_branch = git_stdout.replace('refs/heads/', '').replace('\r', '').replace('\n', '')
        escaped_branch = quote(quote(git_branch, safe=''), safe='')

        # Run `arc browse` and dump the output to the console
        browse_path = '{0}${1}'.format(filename, lines)
        arc_args = ['arc', 'browse', browse_path, '--branch', escaped_branch]
        arc_child = subprocess.Popen(
            arc_args, cwd=filedir,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        arc_stdout = str(arc_child.stdout.read())
        arc_stderr = str(arc_child.stderr.read())
        if arc_stdout or arc_stderr:
            print('Ran `{0}` in `{1}`'.format(' '.join(arc_args), filedir))
            if arc_stdout:
                print('STDOUT: {0}'.format(arc_stdout))
            if arc_stderr:
                print('STDERR: {0}'.format(arc_stderr))
