#!/bin/bash

cd $(readlink -fn $(dirname "$BASH_SOURCE"))

PIPENV_VENV_IN_PROJECT=1 pipenv sync
