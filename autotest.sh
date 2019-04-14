#!/bin/bsh

# docker build -t dbma:0.0.0.0 .
# docker run --rm -it  dbma:0.0.0.0 /bin/bash

python3 -m unittest tests/dbma/utils/users_test.py
python3 -m unittest tests/dbma/utils/directorys_test.py
python3 -m unittest tests/dbma/config_test.py
python3 -m unittest tests/dbma/utils/cnfs_test.py