import json
from pprint import pprint
from bs4 import BeautifulSoup
import re
pat = re.compile(r"[\r\n\t\s+]+")

if __name__ == "__main__":
    with open("./raw-managers.html") as infile:
        soup = BeautifulSoup(infile.read(), 'html.parser')
        inputs = soup.find_all("input")
        managers = {}
        for inp in inputs:
            value = inp.get('value')
            text = pat.sub(" ", inp.next.text)
            managers[text.strip()] = value.strip() if value else ''

        with open('./managers.json', 'wt') as outfile:
            outfile.write(json.dumps(managers, indent=2))
            outfile.flush()
        
        pprint(managers)
