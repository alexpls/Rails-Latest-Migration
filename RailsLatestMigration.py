import sublime, sublime_plugin
import os
import re

class RailsLatestMigrationCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# Check to see if current file is saved to the file system
		if self.view.file_name() == None:
			raise UnsavedFile("Cannot execute Rails Latest Migration on an unsaved file.")

		cur_path = self.parent_path(self.view.file_name())
		root = self.find_ror_root(cur_path)

		if root:
			migrations_dir = os.path.join(root, 'db', 'migrate')
			migrations = os.listdir(migrations_dir)

			pattern = re.compile('^\d+_\w+.rb$')
			migrations = sorted([m for m in migrations if pattern.match(m)])
			latest_migration = os.path.join(migrations_dir, migrations[-1])

			self.view.window().open_file(latest_migration)

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
class UnsavedFile(Error):
	pass