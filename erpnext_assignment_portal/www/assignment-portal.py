import frappe

no_cache = 1


def get_context():
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()

	context = frappe._dict()
	context.boot = frappe._dict(
		csrf_token=csrf_token,
		frappe_version=frappe.__version__,
		site_name=frappe.local.site,
	)
	return context
