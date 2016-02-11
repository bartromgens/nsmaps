#!/usr/bin/env python3

import os
import subprocess

from nsmaps.local_settings import DEPLOY_DIR


def main():
    if not os.path.exists(DEPLOY_DIR):
        print('ERROR: Deploy dir ' + DEPLOY_DIR + ' does not exists. Please set it in local_settings.py')

    print('Deploying to: ' + DEPLOY_DIR)

    filepaths = {
        'website/index.html',
        'website/station_map.js'
    }

    filepaths_css = {
        'website/css/nsmaps.css',
        'website/css/bootstrap_readable.min.css'
    }

    for file in filepaths:
        subprocess.check_call(['scp', file, DEPLOY_DIR])

    for file in filepaths_css:
        subprocess.check_call(['scp', file, os.path.join(DEPLOY_DIR, 'css')])


if __name__ == "__main__":
    main()