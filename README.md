# Reposte
[![Python application](https://github.com/rgiles4/Reposte/actions/workflows/python-app.yml/badge.svg)](https://github.com/rgiles4/Reposte/actions/workflows/python-app.yml)

## Statement of Intent
This capstone project is for the development of a video replay software system for the sport of fencing. This project is for Dr. Terry Yoo, in partial fulfillment of the Computer Science BS degree for the University of Maine. Our team will also be working closely with the University of Maine’s fencing club, the Blade Society, when developing this product.

The goal of this project is to create open-source video replay software that can run on a laptop using MacOS or Windows. The USA National Fencing requires a video replay system to help referees review calls during fencing matches. Currently the replay system used is outdated, expensive, closed-sourced and needs to be updated. This product aims to give a solution to clubs and competitions by offering an open-source solution that can increase accessibility to video replay systems.

## Important Repository File Structure
```
/Reposte
| --.github/
|    |-- workflows/
|    |    | -- python-app.yml  # GitHub Action to Lint, Format, and Build a Python Package
| -- docs/  # Documentation Directory
|    | -- diagrams/
|    |    | -- Reposte-EDA(1).jpg
|    |    | -- SDDDecomposition(1).jpg
|    |    | -- sysUseCase.jpg
|    | -- Cocomo Report.pdf
|    | -- Prototype Stage 1 Dev.pdf
|    | -- SDD.pdf
|    | -- SRS.pdf
| -- python_package_exercise/  # Assignment 5 File Directory; Note this is not a critical Directory
| -- .gitignore
| -- .pre-commit-config.yaml  # pre-commit-hooks action config file
| -- README.md
| -- Repose_Prototype.py  # Current working prototype file
```

## Run the Reposte Prototype
1. Ensure packages are installed
    - pip install PyQt6 imageio imageio-ffmpeg
2. Run program
    - python reposte_prototype.py


## Assignment 5: CI/CD Python Package
All files for Assignment 5 can be found in the python_package_exercise folder.

