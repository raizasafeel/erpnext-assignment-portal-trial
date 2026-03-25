import ipaddress
import socket
from urllib.parse import urlparse

import frappe
from frappe.frappeclient import AuthError, FrappeClient, SiteExpiredError, SiteUnreachableError
from frappe.model.document import Document
from frappe.utils.password import get_decrypted_password

_BLOCKED_HOSTS = frozenset({
	"169.254.169.254",
	"fd00:ec2::254",
	"metadata.google.internal",
	"metadata.goog",
	"169.254.169.253",
})

_ERROR_PATTERNS = {
	("auth", "login", "password", "401", "403"): "Invalid credentials. Check your username and password.",
	("connection", "resolve", "refused", "adapter", "timeout"): "Could not reach site. Check the URL.",
}


def _is_local_dev() -> bool:
	if getattr(frappe.conf, "developer_mode", False):
		return True
	site = getattr(frappe.local, "site", "") or ""
	return site.endswith(".localhost")


def _validate_url_safe(url: str):
	parsed = urlparse(url)

	if parsed.scheme not in ("http", "https"):
		frappe.throw("Only HTTP/HTTPS URLs are allowed.")

	hostname = parsed.hostname
	if not hostname:
		frappe.throw("Invalid URL: no hostname found.")

	if hostname in _BLOCKED_HOSTS:
		frappe.throw("This URL is not allowed.")

	if not _is_local_dev() and hostname in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
		frappe.throw("Localhost URLs are not allowed.")

	if not _is_local_dev():
		try:
			resolved = socket.getaddrinfo(hostname, None)
			for _, _, _, _, addr in resolved:
				ip = ipaddress.ip_address(addr[0])
				if ip.is_private or ip.is_loopback or ip.is_link_local:
					frappe.throw("Cannot connect to private/internal addresses.")
		except socket.gaierror:
			pass


def _friendly_error(e: Exception) -> str:
	if isinstance(e, AuthError):
		return "Invalid credentials. Check your username and password."
	if isinstance(e, SiteExpiredError):
		return "Site has expired."
	if isinstance(e, SiteUnreachableError):
		return "Site is unreachable (502)."

	error_str = str(e).lower()
	for keywords, message in _ERROR_PATTERNS.items():
		if any(kw in error_str for kw in keywords):
			return message
	return "Connection failed. Check your site details."


class ERPNextSite(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		connection_status: DF.Literal["", "Unknown", "Connected", "Failed"]
		last_checked: DF.Datetime | None
		site_password: DF.Password
		site_url: DF.Data
		site_username: DF.Data
		student: DF.Link | None
	# end: auto-generated types

	def validate(self):
		if self.site_url:
			self.site_url = self.site_url.strip().rstrip("/")
			if not self.site_url.startswith(("http://", "https://")):
				if _is_local_dev() and ("localhost" in self.site_url or "127.0.0.1" in self.site_url):
					self.site_url = f"http://{self.site_url}"
				else:
					self.site_url = f"https://{self.site_url}"

			_validate_url_safe(self.site_url)

	@frappe.whitelist()
	def test_connection(self):
		try:
			password = get_decrypted_password("ERPNext Site", self.name, "site_password")
			client = FrappeClient(self.site_url, self.site_username, password)
			user = client.get_api("frappe.auth.get_logged_user")
			self.connection_status = "Connected"
			self.save()
			return {"status": "Connected", "user": user}
		except Exception as e:
			self.connection_status = "Failed"
			self.save()
			frappe.log_error(title="ERPNext Site connection failed", message=f"Site: {self.name}")
			return {"status": "Failed", "error": _friendly_error(e)}
