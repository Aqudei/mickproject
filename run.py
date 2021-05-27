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

DEFAULT_WAIT_SEC = 30

rgx = re.compile(r'B\d+(\.\d+)*')


def search(project, driver):
    """
    docstring
    """
    match = rgx.search(project)
    if not match:
        return

    project_name = match.group(0)
    print(f"Looking up Project {project_name}")
    url = f'https://baaa.certification.systems/navbar/Search/?search={project_name}'
    response = driver.request('GET', url)
    if not response.status_code == 200:
        print(f"Project Not found {project_name}")
        return

    response_data = response.json()
    for r in response_data:
        if project_name in r['Result'] and len(r['Result']) >= 8:
            return r

    print(f"Project Not found {project_name}")


def read_excel(fname):
    """
    docstring
    """
    wb = openpyxl.load_workbook(fname, data_only=True)
    ws = wb.active

    headers = []
    items = []
    for row in ws.iter_rows(values_only=True):
        if not headers or len(headers) <= 0:
            if row[0] and "project name" in row[0].lower():
                # process header
                headers.extend(row)
                continue

        else:
            item = {}
            for h, v in zip(headers, row):
                item[h] = v
            items.append(item)

    return items


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


def edit_project_manager(driver, targetUrl, manager):
    """
    docstring
    """
    if not targetUrl:
        return

    parts = targetUrl.strip("/").split("/")
    if len(parts) < 3:
        return

    try:
        file_no = parts[1]

        url = f"https://baaa.certification.systems/ProjectFile/Edit/{file_no}"
        print(f"Edit project Url: {url}")
        driver.get(url)
        print("Waiting for project manager...")
        # Scroll first
        element = WebDriverWait(driver, DEFAULT_WAIT_SEC).until(EC.presence_of_element_located(
            (By.NAME, 'ProjectFile-ProposalAddress-PostCode')))
        driver.execute_script("arguments[0].scrollIntoView(true);", element)

        element = WebDriverWait(driver, DEFAULT_WAIT_SEC).until(EC.presence_of_element_located(
            (By.XPATH, '//*[contains(@id,"select2-ProjectFile-ProjectManagerId")]')))

        element.click()
        time.sleep(2)
        element = WebDriverWait(driver, DEFAULT_WAIT_SEC).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.select2-search__field')))

        # element.send_keys("Chris Franklin")
        element.send_keys(manager)
        element.send_keys(Keys.RETURN)

        print("Saving updates...")
        element = WebDriverWait(driver, DEFAULT_WAIT_SEC).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="page-footer-bar"]/div/div/div/div/button[2]')))
        element.click()

        WebDriverWait(driver, DEFAULT_WAIT_SEC).until(
            EC.presence_of_element_located((By.ID, 'toggle-view')))
        print(f"Project with document no. {file_no} updated successfully")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """
    docstring
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--manager", default="Chris Franklin")

    options = parser.parse_args()

    config = read_config()
    items = read_excel(options.input)

    driver = Chrome()

    driver.get(config['site'])
    login(config, driver)

    items_len = len(items)
    for idx, item in enumerate(items):
        print(f"Processing {idx+1} of {items_len} items")

        project = search(item['Project Name'], driver)
        if not project:
            continue

        print(f"Found target Url: {project['TargetUrl']}")
        edit_project_manager(driver, project['TargetUrl'], options.manager)


if __name__ == "__main__":
    main()
