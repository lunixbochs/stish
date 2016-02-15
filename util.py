import os
import string
import subprocess

def extract_path(cmd, delim=':'):
    path = popen(cmd, os.environ).communicate()[0].decode()
    path = path.split('__SUBL__', 1)[1].strip('\r\n')
    return ':'.join(path.split(delim))

def find_path(env):
    # find PATH using shell --login
    if 'SHELL' in env:
        shell_path = env['SHELL']
        shell = os.path.basename(shell_path)

        if shell in ('bash', 'zsh'):
            return extract_path(
                (shell_path, '--login', '-c', 'echo __SUBL__$PATH')
            )
        elif shell == 'fish':
            return extract_path(
                (shell_path, '--login', '-c', 'echo __SUBL__; for p in $PATH; echo $p; end'),
                '\n'
            )

    # guess PATH if we haven't returned yet
    split = env['PATH'].split(':')
    p = env['PATH']
    for path in (
        '/usr/bin', '/usr/local/bin',
        '/usr/local/php/bin', '/usr/local/php5/bin'
                ):
        if not path in split:
            p += (':' + path)

    return p

@memoize
def create_environment():
    if os.name == 'posix':
        os.environ['PATH'] = find_path(os.environ)
    return os.environ

def can_exec(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

def which(cmd):
    env = create_environment()
    for base in env.get('PATH', '').split(os.pathsep):
        path = os.path.join(base, cmd)
        if can_exec(path):
            return path
    return None

def popen(cmd, env=None):
    if isinstance(cmd, str):
        cmd = cmd,

    stdin = subprocess.PIPE
    stdout = subprocess.PIPE
    stderr = subprocess.PIPE

    master = None
    info = None
    if os.name == 'nt':
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = subprocess.SW_HIDE
    elif use_pty:
        import pty
        master, slave = pty.openpty()
        stdin = slave
        stdout = slave

    if env is None:
        env = create_environment()

    try:
        p = subprocess.Popen(cmd, stdin=stdin,
            stdout=stdout, stderr=stderr,
            startupinfo=info, env=env)

        if master:
            p.pty = True
            p.stdout = os.fdopen(master, 'rb')
            p.stdin = os.fdopen(master, 'wb')
        else:
            p.pty = False

        return p
    except OSError as err:
        print('Error launching', repr(cmd))
        print('Error was:', err.strerror)
        print('Environment:', env)
        return err.strerror

def get_windows_drives():
    from ctypes import windll
    bitmask = windll.kernel32.GetLogicalDrives()
    return [c for i, c in enumerate(string.ascii_uppercase) if bitmask & 1 << i]
