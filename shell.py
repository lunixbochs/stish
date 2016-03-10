import subprocess

def run(cmdline):
    p = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) 
    out, err = p.communicate('') 
    text = ((out.decode('utf8', 'replace') or '') + (err.decode('utf8', 'replace') or '')).strip() + '\n' 
    return text
