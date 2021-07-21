# Fatjack 
## An Introduction to reinforcement learning with blackjack game
-----
## Abstract

This repository aims to discuss the implementation of reinforcement learning algorithms to solve the casino game blackjack. It is also my Final
Project for the Master in Data Science at KSchool.

## You just feel curious and don't want to dwell on details too much...

Then, go straight to the [Casino](http://34.77.255.37) and see how RL agents have fun there!

The casino is intended to be intuitive. If you don't think it is, you'll find a user guide in the last section of the memorandum [../master/Memorandum.pdf].

RL agents are tireless, so remember to press **Stop** to give the floor to different players!

###Requirements and technical details:

All you need to know or have when downloading this project is: 

1. A Miniconda/Anaconda package manager. 
2. The project has been developed on an Ubuntu 20.04.2 LTS operating system,
but it is intended to be cross-platform for most of its operations, except for some of them that are mentioned in the point right below. 
3. Some operations carried out in some notebooks are multiprocessed and do not work on Windows.
Anyways, the notebooks are presented after execution and results can be perfectly read regardless of the OS. 
4. The project is written in Python, except for the web-based front-end that has been written in
HTML5, CSS, and Vanilla JavaScript powered by the D3 library (for plotting). 
5. The Python version and third-party packages used are listed in [hist-environment.yml](../master/hist-environment.yml) file in the Github repository.  
6. To create an environment with those libraries, execute on a terminal: `conda env create –f hist-environment.yml` **in the root folder of the project**. 
7. **To make sure that the project properly runs, notebooks and folders must be at the same filesystem level. In other words, the Github repository
structure must be exactly replicated on the local filesystem. Otherwise, notebooks cannot load the RL libraries.
This requirement includes renaming neither folders nor files.** 
8. Terminal commands must be executed from the root folder of the project, the one containing the whole file structure presented in this repository.
