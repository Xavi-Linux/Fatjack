# Fatjack 
## An Introduction to reinforcement learning with blackjack game
-----
## Abstract

<<<<<<< HEAD
### Coming up soon..
After knuckling down, I'm converting the game into a RL environment...
=======
This repository aims to discuss the implementation of reinforcement learning algorithms to solve the casino game blackjack. It is also my Final
Project for the Master in Data Science at KSchool.

## You just feel curious and don't want to dwell on details too much...

Then, go straight to the [Casino](http://34.77.255.37) and see how mortgage-free RL agents have mind-boggling fun there!

The casino is intended to be intuitive. If you don't think it is, you'll find a user guide in the last section of the [memorandum](../master/Memorandum.pdf).

RL agents are tireless, so remember to press **Stop** button to give the floor to different players!

## You have lately developed a geekish behaviour and delving into the project looks tempting...

Then, All in! Download and go for it!

However, I **strongly** recommend that you first have a read through the [memorandum](../master/Memorandum.pdf) before executing the Notebooks attached herewith.

### Requirements and technical details:

All you need to have when downloading this project is: 

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

### Project structure overview

- [games](../master/games): It is a hand-made Python module that encapsulates the blackjack game logic.
- [environments](../master/environments): It turns the blackjack game supplied by game module into a RL environment.
- [agents](../master/agents): This module abstracts the algorithms and provide agents with some other persistence-oriented capabilities.
- [interfaces](../master/interfaces): The web folder contains all necessary files to run the final data product as a web page.
- [results](../master/results): a bunch of binary files storing agents’ results after their training.
- [stored_agents](../master/stored_agents): a bunch of binary files storing ready-to-be-deployed agents.
- [tables](../master/tables): a bunch of binary files storing agents's Q/V-tables.
- The notebooks: every notebooks follows the same structure:
  * Goals: it is stated what the purpose of the notebook is and what should be achieved at the end of it. 
  * Library importations: every library used throughout the notebook is declared beforehand. 
  * Plot utilities: it exposes methods that help draw recurrent plots. 
  * Experiment definition: it contains the methods that allow interaction between agents and environments.  
  * Notebook-specific code: the necessary code execution is carried out to achieve the goals stated at the beginning of the notebook. 

### RL algorithms implemented

- Every visit Montecarlo
- Off Policy Montecarlo
- QLearning
- Sarsa
- Sarsa Lambda
- Watkins Lambda
>>>>>>> dev
