# DevOps Exercise
[![Python application](https://github.com/rgiles4/Reposte/actions/workflows/python-app.yml/badge.svg)](https://github.com/rgiles4/Reposte/actions/workflows/python-app.yml)

This repository creates Python package for sorting integer 
lists using the DevOps software development approach. The
package is built using Python 3.9 and 3.10 on Ubuntu, Windows,
and MacOS latest.

## DevOps
This repository utilizes a GitHub action to install dependencies,
format, lint, test, and build the Python package on a push to main, and on pull requests.

### The Action
1. Installs Python 3.9 and 3.10
2. Installs flake8, black, and pytest
3. Checks committed files size (files over 1000mb fail the test)
4. Formats with black
5. Lints with flake8
6. Runs tests using pytest
7. Builds the Python Package


  
