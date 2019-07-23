#!/bin/bsh

# docker build -t 1721900707/dbma:0.0.0.8 .
# docker run --rm -it  1721900707/dbma:0.0.0.8 /bin/bash

python3 -m unittest tests/dbma/utils/users_test.py
python3 -m unittest tests/dbma/utils/directorys_test.py
python3 -m unittest tests/dbma/config_test.py
python3 -m unittest tests/dbma/utils/cnfs_test.py
python3 -m unittest tests/dbma/log_test.py
