# release_helper

This is a simple utility that will help with updating Binary Ninja plugins in the plugin manager

We recommend adding it as a submodule to your existing plugin so that you can easily get updates without having to manually copy the file:

```
$ cd vector35/snippets
$ git submodule add https://github.com/Vector35/release_helper release
$ git submodule update --init --recursive
$ chmod +x release/do_release.py
$ pip3 install githubrelease gitpython
```

## new release

Whenever you have a new release, you can either let the script automatically increment the version number for you, or you can specify it yourself. You can either manually edit the `plugin.json` file with the new version in which case the release script will create the appropriate tag and release for you, or specify it yourself on the command-line:

```
$ cd vector35/snippets
$ ./release/do_release.py --help

usage: do_release.py [-h] [-d DESCRIPTION] [-v NEW_VERSION] [--force]

optional arguments:
  -h, --help            show this help message and exit
  -d DESCRIPTION, --description DESCRIPTION
                        Description for the new release
  -v NEW_VERSION, --version NEW_VERSION
                        New version string
  --force               Override the repository dirty check

$ ./release/do_release.py --version 1.5.1
```
