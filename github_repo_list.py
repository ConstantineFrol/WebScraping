from collections import defaultdict

import requests

# owner = user name on GitHub
owner = 'ConstantineFrol'

url = f'https://api.github.com/users/{owner}/repos'

response = requests.get(url)
j_data = []
if response.ok:
    j_data = response.json()

res = defaultdict(list)

{res[key].append(sub[key]) for sub in j_data for key in sub}

# print(str(dict(res['name'])))

print(f"Person:\t{owner} has {len(res['name'])} repositories on GitHub\n")

for repo_name in res['name']:
    print(repo_name, '\n')
