app_name = "erpnext_assignment_portal"
app_title = "ERPNext Assignment Portal"
app_publisher = "Frappe School"
app_description = "Assignment portal for ERPNext course grading"
app_email = "school@frappe.io"
app_license = "mit"

export_python_type_annotations = True
require_type_annotated_api_methods = True

# Route all /assignment-portal/* paths to the Vue SPA
website_route_rules = [
	{"from_route": "/assignment-portal/<path:app_path>", "to_route": "assignment-portal"},
]
