import pdb
import os
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlencode
from dotenv import load_dotenv
from seleniumrequests import Chrome
load_dotenv()


USERNAME = os.environ.get("BAAA_USERNAME")
PASSWORD = os.environ.get("BAAA_PASSWORD")
DEFAULT_WAIT_SEC = 30


class Baaa:
    LOGIN_URL = 'https://login.certification.systems/login.aspx'

    def __init__(self):
        """
        docstring
        """
        pass

    """
    docstring
    """

    def login_sequence(self):
        """
        docstring
        """
        print("Loggin in...")
        self.driver = Chrome()
        self.driver.get(self.LOGIN_URL)
        element = WebDriverWait(self.driver, DEFAULT_WAIT_SEC * 2).until(
            EC.presence_of_element_located((By.ID, "username")))
        element.send_keys(USERNAME)

        element = WebDriverWait(self.driver, DEFAULT_WAIT_SEC).until(
            EC.presence_of_element_located((By.ID, "checkButton")))
        element.click()

        element = WebDriverWait(self.driver, DEFAULT_WAIT_SEC).until(
            EC.element_to_be_clickable((By.ID, "passwordRow")))
        element.send_keys(PASSWORD)

        element = WebDriverWait(self.driver, DEFAULT_WAIT_SEC).until(
            EC.presence_of_element_located((By.ID, "loginButton")))
        element.click()

    def lookup_project(self, project_name):
        """
        docstring
        """
        print(f"Looking up Project {project_name}")
        url = f'https://baaa.certification.systems/navbar/Search/?search={project_name}'
        response = self.driver.request("GET", url)
        if not response.status_code == 200:
            print(f"Project Not found {project_name}")
            return

        response_data = response.json()
        for r in response_data:
            if project_name in r['Result'] and len(r['Result']) >= 8:
                parts = r['TargetUrl'].split("/")
                if not parts or len(parts) < 3:
                    return

                return {**r, "file_no": parts[-2]}

    def update_pm(self, project_name, desired):
        """
        docstring
        """

        project = self.lookup_project(project_name)
        if not project:
            print(f"Project not found: {project_name}")
            return

        try:

            url = f"https://baaa.certification.systems/ProjectFile/Edit/{project['file_no']}"
            print(f"Updating project: {url}")
            self.driver.get(url)
            print("Waiting for project manager...")
            # Scroll first
            element = WebDriverWait(self.driver, DEFAULT_WAIT_SEC).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="project-configuration"]/div[2]/div[9]/div/div/input')))
            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", element)

            element = WebDriverWait(self.driver, DEFAULT_WAIT_SEC).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="general-details"]/div[2]/div[5]/div/div/div/span/span[1]/span')))

            element.click()
            time.sleep(2)
            element = WebDriverWait(self.driver, DEFAULT_WAIT_SEC).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.select2-search__field')))

            # element.send_keys("Chris Franklin")
            element.send_keys(desired)
            element.send_keys(Keys.RETURN)

            print("Saving updates...")
            element = WebDriverWait(self.driver, DEFAULT_WAIT_SEC).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="page-footer-bar"]/div/div/div/div/button[2]')))
            element.click()
            WebDriverWait(self.driver, DEFAULT_WAIT_SEC).until(
                EC.presence_of_element_located((By.ID, 'toggle-view')))
            print(
                f"Project with document no. {project['file_no']} updated successfully")
        except Exception as e:
            print(f"Error: {e}")

    def list_projects(self, manager='Elizabeth Henderson'):
        """
        docstring
        """
        data = {
            "Filter.DateFrom": "1/01/1980",
            "Filter.DateTo": "31/12/2035",
            "Filter.SelectedProjectManagerIds": "1113",
            "Filter.SelectedColumns": "Name,ProjectManager",
            "Filter.SelectedProjectMode": "1",
        }
        url_params = urlencode(data)
        url = f'https://baaa.certification.systems/Search/Projects?{url_params}'
        self.driver.get(url)

        WebDriverWait(self.driver, DEFAULT_WAIT_SEC).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.pagination")))
        table = WebDriverWait(self.driver, DEFAULT_WAIT_SEC).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-bordered")))
        soup = BeautifulSoup(table.get_attribute("outerHTML"), 'html.parser')
        rows = soup.find_all("tr")
        import pdb
        pdb.set_trace()

        for row in rows:
            import pdb
            pdb.set_trace()
        import pdb
        pdb.set_trace()
