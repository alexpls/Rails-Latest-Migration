import sublime, sublime_plugin
import os
import re

class RailsLatestMigrationCommand(sublime_plugin.WindowCommand):
	def run(self):
		try:
			# Try to get a path from the currently open file.
			cur_path = self.window.active_view().file_name()
		except AttributeError:
			cur_path = None
			
		# If no file is open, try to get it from the currently open folders.
		if cur_path == None:
			if self.window.folders():
				cur_path = self.window.folders()[0]

		if cur_path:
			if os.path.isfile(cur_path):
				cur_path = os.path.dirname(cur_path)
			root = self.find_ror_root(cur_path)
		else:
			raise NothingOpen("Please open a file or folder in order to search for the latest migration")

		if root:
			migrations_dir = os.path.join(root, 'db', 'migrate')
			migrations = os.listdir(migrations_dir)

			pattern = re.compile('^\d+_\w+.rb$')
			migrations = sorted([m for m in migrations if pattern.match(m)])
			latest_migration = os.path.join(migrations_dir, migrations[-1])

			self.window.open_file(latest_migration)

	# Recursively searches each up a directory structure for the 
	# expected items that are common to a Rails application.
	def find_ror_root(self, path):
		expected_items = ['Gemfile', 'app', 'config', 'db']
		files = os.listdir(path)

		# The recursive search has gone too far and we've reached the system's
		# root directory! At this stage it's safe to assume that we won't come
		# across a familiar directory structure for a Rails app.
		if path == '/':
			raise NotRailsApp("Cannot recognize this file structure as a Rails app")

		if len([x for x in expected_items if x in files]) == len(expected_items):
			return path
		else:
			return self.find_ror_root(self.parent_path(path))

	# Returns the parent path of the path passed to it.
	def parent_path(self, path):
		return os.path.abspath(os.path.join(path, '..'))

class Error(Exception):
	def __init__(self, msg):
		self.msg = msg
		sublime.error_message(self.msg)

class NotRailsApp(Error):
	pass
class NothingOpen(Error):
	pass