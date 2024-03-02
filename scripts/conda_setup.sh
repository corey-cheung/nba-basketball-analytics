#!/bin/bash

set -eufo pipefail

echo "Setting up nba-basketball-analytics conda env"

# Config shell session to work with conda
. ~/miniconda3/etc/profile.d/conda.sh

conda deactivate
conda env remove -n nba-basketball-analytics
conda create -yqn nba-basketball-analytics python=3.10
conda activate nba-basketball-analytics
conda install \
	--channel conda-forge \
	--channel defaults \
	--quiet \
	--yes \
    streamlit \
	python-duckdb \
	pandas \
    numpy \
    matplotlib
conda install \
	--channel conda-forge \
	--channel defaults \
	--quiet \
	--yes \
    black \
    pylint \
	isort


echo "Finished, now spin up your new conda environment with 'conda activate nba-basketball-analytics'"
