from os import pardir, urandom
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import argparse
import openpyxl
import json
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumrequests import Chrome
import time
import re
import os
from datetime import datetime, timedelta

DEFAULT_WAIT_SEC = 30


def login(config, driver):
    """
    docstring
    """
    print("Loggin in...")
    element = WebDriverWait(driver, DEFAULT_WAIT_SEC * 2).until(
        EC.presence_of_element_located((By.ID, "username")))
    element.send_keys(config["username"])

    element = WebDriverWait(driver, DEFAULT_WAIT_SEC).until(
        EC.presence_of_element_located((By.ID, "checkButton")))
    element.click()

    element = WebDriverWait(driver, DEFAULT_WAIT_SEC).until(
        EC.element_to_be_clickable((By.ID, "passwordRow")))
    element.send_keys(config["password"])

    element = WebDriverWait(driver, DEFAULT_WAIT_SEC).until(
        EC.presence_of_element_located((By.ID, "loginButton")))
    element.click()


def read_config():
    """
    docstring
    """
    with open('config.json', 'rt') as fp:
        config = json.loads(fp.read())
        return config


def download_tasks(config, driver):
    """
    docstring
    """
    start_ndex = 0
    page_size = 100
    tasks = []
    # due_start = datetime.now().replace(month=1, day=1)
    # due_end = datetime.now().replace(month=12, day=31)
    filt = config['filter']

    data = {
        "AssignStatus": 0,
        "ReminderStatus": 0,
        "CompletionStatus": 1,
        "SearchKeyword": filt.strip(),
        "IncludedCategories": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "DueDateStart": config['due_start'],
        "DueDateEnd": config['due_end'],
        "StartIndex": start_ndex,
        "PageSize": page_size
    }

    response = driver.request(
        'POST', 'https://baaa.certification.systems/Reminder/Search/Tasks', data=data)

    if not response.status_code == 200:
        raise Exception("failed to fetch tasks!")

    notes = response.json()['Data']['Notes']

    tasks.extend(notes)

    while len(notes) > 0:
        start_ndex = start_ndex + page_size
        data["StartIndex"] = start_ndex

        response = driver.request(
            'POST', 'https://baaa.certification.systems/Reminder/Search/Tasks', data=data)

        if not response.status_code == 200:
            raise Exception("failed to fetch tasks!")

        notes = response.json()['Data']['Notes']

        tasks.extend(notes)

        return tasks


def change_assignee(tasks, config, manager_id, driver):
    """
    docstring
    """
    print(f"Now @ change_assignee() using Id: {manager_id}")
    headers = {
        "Referer": "https://baaa.certification.systems/",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json; charset=UTF-8",
        "Host": "baaa.certification.systems",
        "Origin": "https://baaa.certification.systems",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    data = {"userid": manager_id}

    for task in tasks:
        url = f"https://baaa.certification.systems/Reminder/Note/{task['Id']}/Assignee/"
        print(f"Url: {url}")
        response = driver.request(
            'POST', url, data=json.dumps(data), headers=headers)
        print(f"Response status code: {response.status_code}")

        if not response.status_code == 200:
            print(f"Error updating assginee for task {task['Id']}")
            print(response.text)
            continue
        print(f"Successfully updated assginee for task {task['Id']}")


def read_managers():
    """
    docstring
    """
    with open("managers.json", 'rt') as fp:
        managers = json.loads(fp.read())
        print(f"Loaded ({len(managers)}) managers")
        return managers


def main():
    """
    docstring
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--manager", default="Chris Franklin")

    options = parser.parse_args()

    config = read_config()
    managers = read_managers()
    if not config['manager'] in managers:
        print(f"Error! Can't lookup ID of Manager <{config['manager']}>")
        return

    manager_id = managers[config['manager']]

    driver = Chrome()

    driver.get(config['site'])
    login(config, driver)

    tasks = download_tasks(config, driver)
    if tasks and len(tasks) > 0:
        change_assignee(tasks, config, manager_id, driver)


if __name__ == "__main__":
    main()
