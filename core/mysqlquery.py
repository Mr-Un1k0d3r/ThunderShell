"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/mysqlquery.py
"""

import MySQLdb
from core.ui import UI

class MySQLQuery:

    	def __init__(self, config):
        	self.config = config
	        self.init_mysql()

	def init_mysql(self):
		try:
			self.conn = MySQLdb.connect(host=self.config.get("mysql-host"), port=int(self.config.get("mysql-port")), user=self.config.get("mysql-user"), passwd=self.config.get("mysql-pass"))
			self.conn.autocommit(True)
		except:
			UI.error("Failed to connect to the MySQL instance", True)

	def install_db(self):
		cursor = self.conn.cursor()
		cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_schema = 'thundershell' AND table_name = 'active_session'")

		if cursor.rowcount == 0:
			UI.error("Creating MySQL tables for first time use")
			cursor.execute("CREATE DATABASE thundershell")
			cursor.execute("CREATE TABLE thundershell.active_session (uid varchar(36), shell varchar(16))")
			cursor.execute("CREATE TABLE thundershell.shell_cmd (shell varchar(16), guid varchar(36), uid varchar(36), timestamp int, origin varchar(50))")
			cursor.execute("CREATE TABLE thundershell.shell_response (shell varchar(16), guid varchar(36), uid varchar(36), timestamp int)")
			cursor.execute("CREATE TABLE thundershell.shell_cmd_data(guid varchar(36), data longtext)")
			self.conn.commit()

		cursor.close()
		return self

	def init_uid(self):
		self.delete_active_user(self.config.get("uid"))

	def push_cmd_data(self, guid, data):
		cursor = self.conn.cursor()
		cursor.execute("INSERT INTO thundershell.shell_cmd_data VALUES (%s, %s)", (guid, data, ))
		self.conn.commit()
		cursor.close()

	def add_active_user(self, uid, shell):
		cursor = self.conn.cursor()
		self.delete_active_user(uid)
		cursor.execute("INSERT INTO thundershell.active_session VALUES (%s, %s)", (uid, shell, ))
		self.conn.commit()
		cursor.close()

	def delete_active_user(self, uid, shell=None):
                cursor = self.conn.cursor()
		if shell == None:
	                cursor.execute("DELETE FROM thundershell.active_session WHERE uid = %s", (uid, ))
        	else:
			cursor.execute("DELETE FROM thundershell.active_session WHERE uid = %s AND shell = %s", (uid, shell, ))
	        self.conn.commit()
                cursor.close()

	def add_cmd(self, shell, guid, uid, timestamp, origin):
		cursor = self.conn.cursor()
		cursor.execute("INSERT INTO thundershell.shell_cmd VALUES (%s, %s, %s, %s, %s)", (shell, guid, uid, timestamp, origin, ))
		self.conn.commit()
		cursor.close()

	def add_response(self, shell, guid, uid, timestamp):
		cursor = self.conn.cursor()
		cursor.execute("INSERT INTO thundershell.shell_response VALUES (%s, %s, %s, %s)", (shell, guid, uid, timestamp, ))
		self.conn.commit()
		cursor.close()

	def delete_cmd(self, shell, uid, guid, timestamp):
		cursor = self.conn.cursor()
                cursor.execute("DELETE FROM thundershell.shell_cmd WHERE shell = %s AND uid = %s AND guid = %s AND timestamp = %s", (shell, uid, guid, timestamp, ))
                self.conn.commit()
                cursor.close()

	def delete_response(self, shell, uid, guid, timestamp):
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM thundershell.shell_response WHERE shell = %s AND uid = %s AND guid = %s AND timestamp = %s", (shell, uid, guid, timestamp, ))
                self.conn.commit()
                cursor.close()

	def get_active_session(self, shell):
		output = []
		cursor = self.conn.cursor()
		cursor.execute("SELECT uid FROM thundershell.active_session WHERE shell = %s", (shell, ))
		sessions = cursor.fetchall()
		cursor.close()
		for session in sessions:
			output.append(session[0])
		return output

	def get_active_shell_by_uid(self, uid):
                output = []
                cursor = self.conn.cursor()
                cursor.execute("SELECT shell FROM thundershell.active_session WHERE uid = %s", (uid, ))
                shells = cursor.fetchall()
		cursor.close()
                for shell in shells:
                        output.append(shell[0])
                return output

	def get_cmd(self, uid):
		output = []

		for shell in self.get_active_shell_by_uid(uid):
                	cursor = self.conn.cursor()
	                cursor.execute("SELECT * FROM thundershell.shell_cmd WHERE shell = %s AND uid = %s", (shell, uid, ))
			shells = cursor.fetchall()
			cursor.close()
			output += shells

		return output

	def get_cmd_response(self, uid):
                output = []

                for shell in self.get_active_shell_by_uid(uid):
                        cursor = self.conn.cursor()
                        cursor.execute("SELECT * FROM thundershell.shell_response WHERE shell = %s AND uid = %s", (shell, uid, ))
                        shells = cursor.fetchall()
                        cursor.close()
                        output += shells

                return output


	def get_cmd_data(self, guid):
		cursor = self.conn.cursor()
		cursor.execute("SELECT * FROM thundershell.shell_cmd_data WHERE guid = %s", (guid, ))
		data = cursor.fetchone()
		cursor.close()
		return data[1]
