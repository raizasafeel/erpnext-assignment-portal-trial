import json

import frappe
from frappe.rate_limiter import rate_limit
from frappe.utils.password import get_decrypted_password

from erpnext_assignment_portal.checks.day1 import Day1Checker
from erpnext_assignment_portal.checks.day2 import Day2Checker
from erpnext_assignment_portal.checks.day3 import Day3Checker

STAFF_ROLES = ["Moderator", "Course Creator", "Batch Evaluator", "System Manager"]


@frappe.whitelist(methods=["GET"])
def get_csrf_token():
	"""Return a fresh CSRF token for the current session."""
	token = frappe.sessions.get_csrf_token()
	frappe.db.commit()
	return token


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=10, seconds=60)
def create_site(site_url: str, site_username: str, site_password: str) -> dict:
	"""Create an ERPNext Site connection for the current student."""
	site = frappe.new_doc("ERPNext Site")
	site.site_url = site_url.strip()
	site.site_username = site_username.strip()
	site.site_password = site_password
	site.insert()
	
	return {"name": site.name, "site_url": site.site_url, "site_username": site.site_username}

CHECKERS = {
	"Day 1": Day1Checker,
	"Day 2": Day2Checker,
	"Day 3": Day3Checker,
}


def _verify_site_owner(site_name: str):
	owner = frappe.db.get_value("ERPNext Site", site_name, "student")
	if owner != frappe.session.user:
		frappe.throw("You don't have access to this site.", frappe.PermissionError)


def _get_course_student_emails() -> list[str]:
	course = frappe.db.get_single_value("Assignment Portal Settings", "course")
	if not course:
		return []

	return list(
		set(
			frappe.get_all(
				"LMS Enrollment",
				filters={"course": course, "member_type": "Student"},
				pluck="member",
			)
		)
	)

@frappe.whitelist()
def test_connection(site_name: str) -> dict:
	"""Test connection to a remote ERPNext site (owner only)."""
	_verify_site_owner(site_name)
	site = frappe.get_doc("ERPNext Site", site_name)
	return site.test_connection()


@frappe.whitelist(methods=["POST"])
def delete_site(site_name: str):
	"""Delete an ERPNext Site connection. Assignment results are preserved."""
	_verify_site_owner(site_name)
	frappe.db.set_value(
		"ERPNext Assignment Result",
		{"site": site_name, "student": frappe.session.user},
		"site",
		"",
	)

	frappe.delete_doc("ERPNext Site", site_name, ignore_permissions=True)
	frappe.db.commit()

@frappe.whitelist(methods=["POST"])
@rate_limit(limit=10, seconds=60)
def run_check(site_name: str, day: str) -> dict:
	"""Run assignment checks for a given day against the student's ERPNext site."""
	_verify_site_owner(site_name)

	if day not in CHECKERS:
		frappe.throw(f"Invalid day: {day}. Choose from: {', '.join(CHECKERS.keys())}")

	site = frappe.get_doc("ERPNext Site", site_name)
	password = get_decrypted_password("ERPNext Site", site.name, "site_password")

	try:
		checker = CHECKERS[day](site.site_url, site.site_username, password)
		result = checker.run()
	except Exception:
		frappe.log_error(title=f"Check failed: {site_name} - {day}")
		result = {
			"total": 0,
			"passed": 0,
			"percentage": 0,
			"sections": {},
			"results": [],
			"error": (
				"Connection failed: Could not connect to your site or invalid credentials. "
				"Please verify your Site URL and credentials in Site Setup."
			),
		}

	site.last_checked = frappe.utils.now()
	site.connection_status = "Failed" if result.get("error") else "Connected"
	site.save(ignore_permissions=True)

	if not result.get("error"):
		_save_assignment_result(site.name, day, result)

	return result


def _save_assignment_result(site_name: str, day: str, result: dict):
	student = frappe.session.user

	existing = frappe.db.get_value(
		"ERPNext Assignment Result",
		{"student": student, "day": day},
		"name",
	)
	if existing:
		doc = frappe.get_doc("ERPNext Assignment Result", existing)
	else:
		doc = frappe.new_doc("ERPNext Assignment Result")
		doc.student = student
		doc.day = day

	doc.site = site_name
	doc.total_checks = result["total"]
	doc.passed_checks = result["passed"]
	doc.percentage = result["percentage"]
	doc.checked_at = frappe.utils.now()
	doc.result_json = json.dumps(result)
	doc.save(ignore_permissions=True)
	frappe.db.commit()


@frappe.whitelist()
def get_my_results() -> list[dict]:
	return frappe.get_all(
		"ERPNext Assignment Result",
		filters={"student": frappe.session.user},
		fields=["name", "day", "passed_checks", "total_checks", "percentage", "checked_at", "result_json"],
		order_by="day asc",
	)


@frappe.whitelist()
def get_student_results(student: str) -> list[dict]:
	frappe.only_for(STAFF_ROLES)
	return frappe.get_all(
		"ERPNext Assignment Result",
		filters={"student": student},
		fields=["name", "day", "passed_checks", "total_checks", "percentage", "checked_at", "result_json"],
		order_by="day asc",
	)


@frappe.whitelist()
def get_dashboard() -> dict:
	frappe.only_for(STAFF_ROLES)

	student_emails = _get_course_student_emails()
	if not student_emails:
		return {"total_students": 0, "with_submissions": 0, "overall_average": 0, "submissions": []}

	results = frappe.get_all(
		"ERPNext Assignment Result",
		filters={"student": ["in", student_emails]},
		fields=["student", "day", "percentage", "checked_at"],
		order_by="checked_at desc",
		limit_page_length=0,
	)

	users = frappe.get_all(
		"User",
		filters={"name": ["in", student_emails]},
		fields=["name", "full_name", "user_image"],
	)
	user_map = {u.name: u for u in users}

	user_data: dict[str, dict] = {}
	all_percentages = []

	for r in results:
		all_percentages.append(r.percentage or 0)
		if r.student not in user_data:
			u = user_map.get(r.student, {})
			user_data[r.student] = {
				"student": r.student,
				"full_name": u.get("full_name") or r.student,
				"user_image": u.get("user_image"),
				"submissions": 0,
				"total_percentage": 0,
				"days_completed": [],
				"last_checked": None,
			}
		entry = user_data[r.student]
		entry["submissions"] += 1
		entry["total_percentage"] += r.percentage or 0
		entry["days_completed"].append(r.day)
		if not entry["last_checked"] or str(r.checked_at) > str(entry["last_checked"]):
			entry["last_checked"] = r.checked_at

	submission_list = []
	for data in user_data.values():
		data["average_percentage"] = round(data["total_percentage"] / data["submissions"], 1) if data["submissions"] else 0
		del data["total_percentage"]
		data["days_completed"] = sorted(set(data["days_completed"]))
		submission_list.append(data)

	for email in student_emails:
		if email not in user_data:
			u = user_map.get(email, {})
			submission_list.append({
				"student": email,
				"full_name": u.get("full_name") or email,
				"user_image": u.get("user_image"),
				"submissions": 0,
				"average_percentage": 0,
				"days_completed": [],
				"last_checked": None,
			})

	submission_list.sort(key=lambda x: (-x["submissions"], -x["average_percentage"]))

	with_subs = sum(1 for s in submission_list if s["submissions"] > 0)
	overall_avg = round(sum(all_percentages) / len(all_percentages), 1) if all_percentages else 0

	return {
		"total_students": len(student_emails),
		"with_submissions": with_subs,
		"overall_average": overall_avg,
		"submissions": submission_list,
	}
