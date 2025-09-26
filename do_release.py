#!/usr/bin/env python3
#Little utility to automatically do a new release.
from git import Repo
from json import load, dump
from github_release import gh_release_create
from sys import exit
from os import path
from argparse import ArgumentParser
from subprocess import run
from pathlib import Path
'''WARNING: BY DEFAULT THIS PLUGIN WILL REGENERATE YOUR README.md! 
Use --skip-regen-readme to only update the version number in README.md.'''

parser = ArgumentParser()
parser.add_argument("-d", "--description", help="Description for the new release", action="store", dest="description", default="")
parser.add_argument("-s", "--subdir", help="Specify a subdirectory", action="store", dest="subdir", default="")
parser.add_argument("-v", "--version", help="New version string", action="store", dest="new_version", default="")
parser.add_argument("--force", help="Override the repository dirty check", action="store_true", dest="dirtyoverride", default=False)
parser.add_argument("--skip-regen-readme", help="Skip regenerating README.md, only update version number", action="store_true", dest="skip_regen_readme", default=False)
args = parser.parse_args()
#TODO

repo = Repo(".")
reponame = list(repo.remotes.origin.urls)[0].split(':')[1].split('.')[0]
if repo.is_dirty() and not args.dirtyoverride:
	print("Cowardly refusing to do anything as the plugin repository is currently dirty.")
	exit(-1)

generator = Path(__file__).parents[0] / "generate_plugininfo.py"
if not generator.is_file():
	generator = Path("./generate_plugininfo.py")
	if not generator.is_file():
		print("Unable to find ./generate_plugininfo.py.")
		exit(-1)

if args.subdir:
    pluginfile = path.join(args.subdir, 'plugin.json')
else:
    pluginfile = 'plugin.json'
with open(pluginfile) as plugin:
	data = load(plugin)

def update_version(data):
	print(f"Updating plugin with new version {data['version']}")
	with open(pluginfile, 'w') as plugin:
		dump(data, plugin, indent=4)
	
	readme_path = 'README.md'
	
	if args.skip_regen_readme:
		# Only update the version number in the README without regenerating it
		import re
		if path.exists(readme_path):
			print("Updating only version number in README.md without regenerating")
			with open(readme_path, 'r') as f:
				readme_content = f.read()
			
			# Update version in the title (format example: # Plugin Name (vX.Y.Z))
			old_version = None
			for line in readme_content.split('\n'):
				if line.startswith('# ') and ' (v' in line:
					match = re.search(r'\(v([\d\.]+)\)', line)
					if match:
						old_version = match.group(1)
						break
			
			if old_version:
				print(f"Replacing version {old_version} with {data['version']} in README.md")
				updated_content = re.sub(
					r'(# .+?\(v)[\d\.]+(\))',
					f'\\1{data["version"]}\\2',
					readme_content
				)
				
				with open(readme_path, 'w') as f:
					f.write(updated_content)
				
				repo.index.add(readme_path)
			else:
				print("Warning: Could not find version pattern in README.md")
	else:
		# Full README regeneration
		run([generator, "-r", "-f"], check=True)
		repo.index.add(readme_path)
	
	repo.index.add(pluginfile)
	if args.description == "":
		repo.index.commit(f"Updating to {data['version']}")
	else:
		repo.index.commit(args.description)
	repo.git.push('origin')

for tag in repo.tags:
	if tag.name == data['version']:
		if args.new_version == "":
			print(f"Current plugin version {data['version']} is already a tag. Shall I increment it for you?")
			yn = input("[y/n]: ")
			if yn == "Y" or yn == "y":
				digits = data['version'].split('.')
				newlast = str(int(digits[-1])+1)
				digits[-1] = newlast
				inc_version = '.'.join(digits)
				data['version'] = inc_version
				update_version(data)
			else:
				print("Stopping...")
				exit(-1)
		else:
			data['version'] = args.new_version
			update_version(data)

# Create new tag
new_tag = repo.create_tag(data['version'])
# Push
repo.remotes.origin.push(data['version'])
# Create release
gh_release_create(reponame, data['version'], publish=True, name="%s v%s" % (data['name'], data['version']))
