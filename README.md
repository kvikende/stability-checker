# Stability-checker

Simple script to log Internet outtakes.

This script periodically opens a socket to test 
whether the Internet connection is down and for how long.

Usage
-
Open a tmux or screen terminal and run the script with

~~~
python3 stability-checker.py
~~~

Note
-
It uses a list of public DNS servers which is randomly selected from. 
This is to avoid relying on just one provider and spread the load a bit.

This can be changed by adding/removing IP, PORT pairs
from the SERVER list.