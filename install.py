import os
import sys
import shutil
import subprocess

if __name__ == '__main__':
    return_code = 1
    try:
        subprocess.check_output(['node', '-v'])
    except FileNotFoundError:
        sys.stderr.write('\nerror: requires Node.js to run, make sure it is installed and can be found under PATH\n')
    else:
        onig_path = os.path.abspath(os.path.join(sys.path[0], 'node_modules/vscode-oniguruma/release/onig.wasm'))
        dest_dir = os.path.abspath(os.path.join(sys.path[0], 'resources'))
        if os.path.isfile(onig_path):
            try:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy(onig_path, dest_dir)
            except:
                sys.stderr.write('\nerror: failed to copy files, make sure you have all permissions\n')
            else:
                return_code = 0
        else:
            try:
                subprocess.run(['npm', 'install'], shell=True)
                onig_path = os.path.abspath(os.path.join(sys.path[0], 'node_modules/vscode-oniguruma/release/onig.wasm'))
                if not os.path.isfile(onig_path):
                    raise
            except Exception:
                sys.stderr.write('\nerror: failed to install dependencies, you may do it manually: "npm install"\n')
            else:
                try:
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.copy(onig_path, dest_dir)
                except:
                    sys.stderr.write('\nerror: failed to copy files, make sure you have all permissions\n')
                else:
                    return_code = 0
    finally:
        if return_code == 0:
            print('\ndone.')
        sys.exit(return_code)
