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
|    | -- CDR-RePoste.pdf
|    | -- CDR.pdf
|    | -- Cocomo Report.pdf
|    | -- Prototype Stage 1 Dev.pdf
|    | -- Prototype Stage 2 Dev-1.pdf
|    | -- SDD-1.pdf
|    | -- SRS-1.pdf
|    | -- UIDD-1.pdf
| -- RePoste/ # App Package Files
|    | -- __init__.py
|    | -- gui.py
|    | -- main.py
|    | -- replay_manager.py # Not Implemented
|    | -- settings.py # Not Implemented
|    | -- utils.py # Not Implemented
|    | -- video_manager.py
| -- RePoste_Tests/ # Unit Test Files
|    | -- __init__.py
|    | -- gui_test.py
|    | -- main_test.py
|    | -- replay_manager_test.py # Not Implemented
|    | -- settings_test.py # Not Implemented
|    | -- video_manager_test.py # Not Implemented
| -- .gitignore
| -- .pre-commit-config.yaml  # pre-commit-hooks action config file
| -- README.md
| -- Repose_Prototype.py  # Old Prototype File (Legacy)
```

## Run the Reposte Prototype
1. Ensure packages are installed
    - pip install PyQt6 imageio imageio-ffmpeg==0.4.5
2. Run program
    - python reposte_prototype.py
