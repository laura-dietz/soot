from setuptools import setup

setup(
    name = 'soot',
    version = '0.6',
    packages = [ 'soot' ],
    install_requires = [
        'flask',
        'Mastodon.py>=1.5.1',
        'keyring'
    ],
    entry_points = {
        'console_scripts': [
            'soot-server=soot.server:main',
            'soot-bm25=soot.bm25:main',
        ]
    },
    include_package_data = True,
    python_requires = "~=3.7",
    url = 'https://github.com/laura-dietz/soot',
    license='BSD 3-Clause License',
    author = 'laura-dietz',
    author_email = '',
    description = 'Soot - search on toots'
)
