# mosquito-identification
Mosquito observation and identification system

## How to run

0. ***Optional, if using Ubuntu*** Ensure Ansible is installed in the target machine:

    `sudo apt update && sudo apt install ansible-core`

    `ansible-playbook -i ansible/hosts.ini ansible/setup.yml`

    The playbook will install Docker and Python in the target machine to ensure the docker container works.

1. With Docker installed:

    `docker compose up --build`

2. Visit `http://localhost:8000/docs`. Here you can create new test Observations manually. Upon creation the entry is written in the database and an async task is executed to classify the image provided in the request via an AI model.

    You can list Observations via GET in the docs, and you should see a randomly generated classification for its species. (There's a small chance it returns `None`, so try several times if this happens).

3. The API provided offers a series of endpoints and methods to manage Observations and allows experts to list AI predictions and provide their own classifications/annotations via the `expert_classifications` endpoint.

4. To run tests, create a virtual environment, install Poetry, install the required packages, and finally run the tests:

    `python3 -m venv .venv`

    `source .venv/bin/activate` 

    `curl -sSL https://install.python-poetry.org | python3 -`

    `export PATH="$HOME/.local/bin:$PATH"`

    `poetry install`

    `PYTHONPATH=src pytest`
