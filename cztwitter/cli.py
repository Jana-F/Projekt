import os
import sys

from datetime import date

import cztwitter as project
from cztwitter.connections import cur
from cztwitter.twitter import download_followers, get_user, get_followers_sum, download_tweets


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


def automated_check():
    """
    Does an automated check for all stuff we want (tweets, followers, likes, rts)
    """
    cur.execute('''SELECT * FROM twitter_user WHERE do_check = true''')
    users = cur.fetchall()
    if not users:
        return True

    for user in users:
        print("handling user %s" % user['screen_name'])
        user = get_user(user_id=user['id'])
        download_followers(user)
        download_tweets(user)


def manage(*args, **kwargs):
    allowed_functions = {
        'bump_version': bump_version,
        'automated_check': automated_check,
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
