import os
import subprocess
import json


__jspath: str = None
__libdir: str = None
__extlib: dict = None


def initialize(jspath: str = 'tokenize.js', libdir: str = 'resources'):
    """(CALL FIRST) to initialize the module, re-calling this will refresh the paths and reload ext.json

    Parameters
    ----------
    - jspath : str, optional,
        path to the "tokenize.js", by default 'tokenize.js'
    - libdir : str, optional,
        path to the "resources" folder, containing ext.json and language definitions, by default 'resources'
    """
    global __jspath, __libdir, __extlib
    
    jspath = os.path.abspath(jspath)
    libdir = os.path.abspath(libdir)
    if not os.path.isfile(jspath):
        raise FileNotFoundError(f'cannot find JS script path "{jspath}"')
    if not os.path.isdir(libdir):
        raise FileNotFoundError(f'cannot find library path "{libdir}"')
    extlib_path: str = os.path.realpath(os.path.join(libdir, 'ext.json'))
    if not os.path.isfile(extlib_path):
        raise FileNotFoundError(
            f'cannot find "ext.json" under directory "{__libdir}"')
    with open(extlib_path, encoding='utf8') as f:
        __extlib = json.loads(f.read())
        if not isinstance(__extlib, dict):
            __extlib = None
            raise SyntaxError(f'extension registry "{extlib_path}" is not properly written')
    __jspath = jspath
    __libdir = libdir


def tokenize(paths: list, syntax: str = ''):
    """to tokenize files

    Parameters
    ----------
    - paths : list,
        the files to tokenize (must be the same syntax)
    - syntax : str, optional,
        the syntax of the files, by default: auto-detect by extension name

    Returns
    -------
    - list -> all files match their position in "paths"
        - list -> results of all lines in a file
            - dict -> result of a line
                - 'raw': str -> the line's original text
                - 'tokens': list -> the tokens in this line
                    - dict -> info of a token
                        - 'startIndex': int -> the starting index of the matched sub-string
                        - 'endIndex': int -> 1 + the last index of the matched sub-string
                        - 'scopes': list -> all scopes that this token falls in
                            - str -> a scope
    """
    global __jspath, __libdir, __extlib
    
    if not __libdir or not __jspath or not __extlib:
        msg = 'the module is not initialized, '
        msg += 'call "initialize(jspath, libdir)" first to provide necessary paths'
        raise RuntimeError(msg)
    
    if len(paths) == 0:
        return list()

    # Determine file syntax type
    if syntax == '':
        ext: str = os.path.splitext(paths[0])[1]
        if ext == '' or not ext:
            raise ValueError(f'file "{paths[0]}" has no extension name, please specify "syntax" manually')
        else:
            ext = ext.lstrip('.')
        try:
            syntax = __extlib[ext]
        except Exception as e:
            msg = f'syntax for file extension "{ext}" is unknown, '
            msg += f'available syntaxes: [{str().join([f"{s}, " for s in set(__extlib.values())])[:-2]}], '
            msg += f'available extensions: [{str().join([f"{s}, " for s in __extlib.keys()])[:-2]}], '
            msg += 'you can also specify manually with the "syntax" parameter; '
            msg += 'hint: official tmBundles available at: http://github.com/orgs/textmate/repositories'
            raise KeyError(msg) from e

    # Ensure tmLanguage file
    tmlang_path: str = os.path.realpath(os.path.join(__libdir, f'{syntax}.tmLanguage'))
    if not os.path.isfile(tmlang_path):
        raise FileNotFoundError(f'cannot find "{syntax}.tmLanguage" under directory "{__libdir}"')

    # Run JS
    abs_paths = [os.path.abspath(p) for p in paths]
    try:
        result_bytes = subprocess.check_output(
            ['node', __jspath, *abs_paths, syntax, __libdir], stderr=subprocess.DEVNULL)
    except FileNotFoundError as e:
        raise RuntimeError('cannot run Node.js, please run installation script first') from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError('JavaScript exception occurred') from 
    result: list[list[dict]] = list()
    for result_line in bytes.decode(result_bytes).splitlines():
        result.append(json.loads(result_line))
    return result
