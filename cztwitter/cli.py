import os
import sys

import cztwitter as project


def bump_version():
    """
    increase the `patch` version number of the project
    """
    v = project.__version__
    new_version = v[:-1] + (v[-1] + 1,)
    new_version_str = '.'.join(map(str, new_version))
    initfile = os.path.join(os.path.dirname(project.__file__), '__init__.py')

    with open(initfile, 'r') as ifile:
        print("Reading old package init file...")
        istr = ifile.read()
        istr = istr.replace(str(v), str(new_version))

    with open(initfile, 'w') as ifile:
        print("Writing new init file with version %s..." % new_version_str)
        ifile.write(istr)

    with open('version', 'w') as ifile:
        ifile.write(new_version_str)


def check_followers():
    pass


def manage(*args, **kwargs):
    allowed_functions = {
        'bump_version': bump_version,
        'check_followers': check_followers,
    }

    try:
        function, params = sys.argv[1], sys.argv[2:]
        to_run = allowed_functions[function]
    except (IndexError, KeyError) as e:
        print('available functions\n')
        for name, ref in allowed_functions.items():
            print("%s  %s" % (name, ref.__doc__))
        sys.exit(-1)
    else:
        print(to_run(*params))
