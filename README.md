***pre-requisite***

It is recommended to use Python 3.x, the packages required are included in requirements.txt. 
You can use pip to install them directly (for Python 3.x):
```
pip3 install requirements.txt
```
You also need to install SUMO properly: https://sumo.dlr.de/docs/Installing/index.html

***Layout of the repository***

main.py: The entrance of the project. Can simply run it when all pre-requisites are installed using:
```
python3 main.py {--sumo-gui or --sumo} {how many times you want the testbed to run. it creates N amount of processes running the testbed simultaneously for speed}
Ex: python3 main.py --sumo-gui 50
```
