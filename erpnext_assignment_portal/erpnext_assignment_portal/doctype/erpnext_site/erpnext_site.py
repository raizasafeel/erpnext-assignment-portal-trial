import ipaddress
import socket
from urllib.parse import urlparse

import frappe
from frappe.frappeclient import FrappeClient
from frappe.model.document import Document
from frappe.utils.password import get_decrypted_password

# Cloud metadata hostnames and IPs to block (AWS, GCP, Azure)
_BLOCKED_HOSTS = frozenset({
	"169.254.169.254",
	"fd00:ec2::254",
	"metadata.google.internal",
	"metadata.goog",
	"169.254.169.253",  # AWS DNS
})


def _is_local_dev() -> bool:
	"""Allow private IPs when running on a local bench (developer_mode or .localhost site)."""
	if getattr(frappe.conf, "developer_mode", False):
		return True
	# .localhost TLD (RFC 6761) is only used for local development
	site = getattr(frappe.local, "site", "") or ""
	return site.endswith(".localhost")


def _validate_url_safe(url: str):
	"""Block SSRF: reject private IPs, metadata endpoints, non-HTTP schemes."""
	parsed = urlparse(url)

	if parsed.scheme not in ("http", "https"):
		frappe.throw("Only HTTP/HTTPS URLs are allowed.")

	hostname = parsed.hostname
	if not hostname:
		frappe.throw("Invalid URL: no hostname found.")

	# Block cloud metadata endpoints (always, even in dev mode)
	if hostname in _BLOCKED_HOSTS:
		frappe.throw("This URL is not allowed.")

	# Block localhost unless local dev
	if not _is_local_dev() and hostname in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
		frappe.throw("Localhost URLs are not allowed.")

	# Resolve hostname and check for private IPs (skip in local dev)
	if not _is_local_dev():
		try:
			resolved = socket.getaddrinfo(hostname, None)
			for _, _, _, _, addr in resolved:
				ip = ipaddress.ip_address(addr[0])
				if ip.is_private or ip.is_loopback or ip.is_link_local:
					frappe.throw("Cannot connect to private/internal addresses.")
		except socket.gaierror:
			pass  # DNS resolution will fail later during connection


def _friendly_error(e: Exception) -> str:
	"""Return user-friendly error without leaking internals."""
	error_str = str(e).lower()
	if any(kw in error_str for kw in ("auth", "login", "password", "401", "403")):
		return "Invalid credentials. Check your username and password."
	if any(kw in error_str for kw in ("connection", "resolve", "refused", "adapter", "timeout")):
		return "Could not reach site. Check the URL."
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
			# Default to https in production, http for localhost dev
			if not self.site_url.startswith(("http://", "https://")):
				if _is_local_dev() and ("localhost" in self.site_url or "127.0.0.1" in self.site_url):
					self.site_url = f"http://{self.site_url}"
				else:
					self.site_url = f"https://{self.site_url}"

			_validate_url_safe(self.site_url)

	@frappe.whitelist()
	def test_connection(self):
		"""Test connection to the remote ERPNext site."""
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
			# Log full error server-side, return sanitized message to client
			frappe.log_error(title="ERPNext Site connection failed", message=f"Site: {self.name}")
			return {"status": "Failed", "error": _friendly_error(e)}
