from flask import Flask, session, redirect, url_for, escape, request, render_template, Response
from flask_cors import CORS
from core.apis import CliApi
from core.config import CONFIG
import sys
import hashlib

errors = ["Wrong password", "Session was destroyed"]
version = "1.0"

class ThunderShellFlask(Flask):

	def init(self, config, web_config):
		self.secret_key = "lkasjdlkj"
		self.session = session
		self.request = request
		self.realconf = config
		self.web_conf = web_config

                self.thunder_config = {}
                self.thunder_config["version"] = "1.0"
                self.thunder_config["banner"] = "ThunderShell Server Login"

        def auth(self):
                if "authenticated" in self.session:
                        return True
                return False

        def get_user(self):
                if "username" in self.session:
                        return self.session["username"]
                return "unknown"

        def set_user(self):
                self.session["authenticated"] = True
                self.session["username"] = request.form["username"].strip()
		self.session["password"] = hashlib.sha512(request.form["password"].strip()).hexdigest()

        def post_login(self):
		try:
	                if self.request.form["password"].strip() == self.realconf.get("server-password"):
				print "successful login"
        	                self.set_user()
                	        return True
		except:
			pass
	
                return False

        def get_config(self, key):
		if self.web_conf.has_key(key):
			return self.web_conf[key]
		if self.thunder_config.has_key(key):
	                return self.thunder_config[key]

		return ""

	def logout(self):
		self.session.pop("authenticated")
		self.session.pop("username")

	def get_shells(self):
                self.web_conf["password"] = self.session["password"]
		self.apis = CliApi(self.web_conf)

		
		return self.apis.list_shell()


	def format_shells(self, shells):
		output = {}
		for shell in shells:
			data = shell.split(" ", 1)
			output[data[0]] = data[1]
		return output

	def get_password(self):
		return  self.session["password"]

webui = ThunderShellFlask(__name__)

@webui.route("/")
def index():
        if webui.auth():
                return redirect(url_for("dashboard"))
        else:
                return redirect(url_for("login"))

@webui.route("/dashboard")
def dashboard():
        if webui.auth():
		shells = webui.get_shells()["shells"]
                return render_template("dashboard.html", username=webui.get_user(), version=webui.get_config("version"), shells=webui.format_shells(shells), path=webui.get_config("server"), auth=webui.get_password())
        else:
                return redirect(url_for("login"))


@webui.route("/login/<int:error>", methods=["GET", "POST"])
@webui.route("/login", methods=["GET", "POST"], defaults={"error": None})
def login(error):
	if request.method == "POST":
		if webui.post_login():
			print "loading dashboard"
			return redirect(url_for("dashboard"))
		return redirect(url_for("login", error=1))

	if error:
		error = errors[error - 1]

	return render_template("login.html", error=error, banner=webui.get_config("banner"), version=webui.get_config("version"))

@webui.route("/logout", methods=["GET"])
def logout():
	error = None
        if webui.auth():
		webui.logout()
		error = 2

	return redirect(url_for("login", error=error))

if __name__ == "__main__":



	config = CONFIG(sys.argv[1])

	
	prefix = "http://"
	if config.get("https-enabled") == "on":
		prefix = "https://"

	web_config = {}
	web_config["server"] = "%s%s:%s" % (prefix, config.get("http-host"), config.get("http-port"))
	print web_config["server"]
	web_config["version"] = version


	
        cors_conf = {
                "origins": [web_config["server"]],
		"methods": ["OPTIONS", "POST", "GET"],
        }


	cors = CORS(webui, resources={r"/api/*": cors_conf})
	webui.init(config, web_config)
	webui.run(host="0.0.0.0", port=8000)
