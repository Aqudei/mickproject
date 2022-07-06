import os
from selenium import webdriver
import argparse
import openpyxl
import json
import csv
import time
import re
from pybaaa import Baaa
import pandas as pd
from dotenv import load_dotenv
load_dotenv()


def read_excel(fname, original):
    """
    docstring
    """
    print(f"Reading excel file: {os.path.abspath(fname)}")
    df = pd.read_excel(fname, header=2)
    df = df[df['Project Manager'] == original]
    return df


def read_config():
    """
    docstring
    """
    with open('config.json', 'rt') as fp:
        config = json.loads(fp.read())
        return config


def main():
    """
    docstring
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--manager", default="Chris Franklin")

    options = parser.parse_args()

    config = read_config()

    df = read_excel(config['input'], config['original'])

    baaa = Baaa()
    baaa.login_sequence()

    print(f"Updating Project  Manager to: {config['desired']}")
    for idx, item in df.iterrows():
        print(f"Updating ProjectL  {item['Project Name']}...")
        baaa.update_pm(item['Project Name'],  config['desired'])


if __name__ == "__main__":
    main()
