# AASMA20 Group 45

This repository contains the Stock Management System that we modelled for our masters class of Autonomous Agents and Multi-Agent Systems.
Detailed in-depth information of the systems architecture, assumptions and goals can be found on the paper Stock Management System.pdf 

 ## Running the program:

#### Setting up initial data to feed the neural network and create the test dataset:

`make setup`

 This setup will include charts and results that can be checked for predictions and conceptualization of the expected agent behaviour.

#### Simulating the agent on the generated data:

`make run`

This command will run the file main.py with a starting risk of 0.5 and decision processes "crescent" and "MinimizeBuyPrice".
In case of wanting to try different decision process or initial risk one just needs to change the Makefile and include the string that matches the desired decision processes and initial risk.

#### Charting results with different decisions processes:

`make chart`

Runs file chart_script.py to create charts for every different combination of decision processes defined in the program. 
<b> WARNING </b> This script uses python's multi-processor library and before execution the variable n_threads should be changed to fit the test machine CPU cores or threads. Default n_threads = 10. 

#### Cleaning results and data-sets:

`make clean`

Deletes every file in the folders initial_data and results. 
<b> WARNING </b> Using without caution will lead to loss of results.

Link para video:
https://drive.google.com/file/d/1qNoqWnLLHkpcf8X_FJEIyFy4kEnkGEef/view