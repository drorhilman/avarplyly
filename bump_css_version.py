import re
import os

target_file = '_includes/css_links.html'


with open(target_file) as f:
    content = f.read()
version = re.findall('{{ site.baseurl }}main-v(.+).css', content)[0]
new_version = int(version) + 1

target_css = f'main-v{version}.css'
assert os.path.isfile(target_css)
new_css = f'main-v{new_version}.css'
os.rename(target_css, new_css)

old_string  = f'{{{{ site.baseurl }}}}main-v{version}.css'
new_string  = f'{{{{ site.baseurl }}}}main-v{new_version}.css'
content = content.replace(old_string, new_string)

with open(target_file, 'w') as f:
    f.write(content)
print(f'version bump from {version} to {new_version}')