# ATLAS

### Atlas of variable stars captured by the TESS mission.

## General Context

All the scripts in this project are designed to be executed from the command line, ideally on Linux systems.

Using a python virtual environment is recommended, to keep dependencies up to date.

Some of the processes that this project deploys are extremely demanding on the CPU; At least a computer with 4 real cores is required to successfully run the similarity.py and super_similarity.py scripts.

Binary files generated on Linux are not compatible with Windows, so the todumb.py script is provided to convert the files to DUMB format.

## Dependencies

Python 3.8 or higher is required, with the following libraries:

- astroquery
- lightkurve
- matplotlib
- numpy
- PyMySQL
- scipy
- similaritymeasures
- tabulate

The dependencies.txt file can be used to install the requirements via PIP.

## Workflow

Starting from a binary file, which contains a dictionary with light curves, the standard workflow is:

### Preliminary grouping

- block_smooth: Produces the binary file with smoothed light curves.
- reduce.py: Simplifies the light curve data by removing very close coordinates. Eliminate non-continuous light curves.
- align.py: Calculates the turning points of the light curves and does a quick preliminary clustering.
- similarity.py: Calculates the area between each pair of light curves of the same preliminary group.
- compare.py: It uses a graph optimization algorithm to generate the most suitable set of groups, based on a threshold area between the curves.

At the end of this stage you will obtain a directory with all the relevant information, and a summary.bin file necessary to continue the process.

### Super grouping

The following scripts must be executed, in the indicated order, using the summay.bin file chosen in the previous phase as a source.

- super_reduce.py
- super_align.py
- super_similarity.py
- super_compare.py

As a result, you will obtain a directory with the relevant information of the calculated super groups. Additionally, you will obtain a summary.bin file with which you can repeat this phase as many times as you deem necessary.

### Obtaining the necessary data to work

You can use the tables.sql file and the get_data.py, sync_curves.py and save_curves.py scripts, in the same order; to download all the original information from the public servers.

However, you must take into account that the total volume of information exceeds one terabyte, and that it will take several days to complete this process.

To simplify this task, you can download the base binary files from <https://starwalker.app>, separated by exposure time and whose weight does not exceed 10 Gigabytes.

---

Title: Eng. MSc

Author: Antonio Maria Perez

E-mail: aperez137@gmail.com

Year: 2022

---
