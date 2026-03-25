from erpnext_assignment_portal.checks.base import BaseChecker

COMPANY_NAME = "Greenfield Trading & Services Pvt. Ltd."
COMPANY_ABBR = "GTS"


class Day1Checker(BaseChecker):
	"""Validates Day 1 assignment: Master Data Setup."""

	def run(self) -> dict:
		self.check_company()
		self.check_fiscal_year()
		self.check_customers()
		self.check_suppliers()
		self.check_items()
		self.check_warehouses()
		self.check_users()
		self.check_accounting_masters()
		return self.get_summary()

	# ── Company Setup ──────────────────────────────────────────

	def check_company(self):
		section = "Company Setup"
		company = self.doc_exists("Company", COMPANY_NAME)

		self.check(
			section, "Company exists", company is not None,
			expected=COMPANY_NAME,
			actual=COMPANY_NAME if company else "Not found",
			message="" if company else f"You haven't created the company '{COMPANY_NAME}' yet. Go to Company list and create it.",
		)
		if not company:
			for name in ["Abbreviation is GTS", "Default Cost Center set", "Default Warehouse set", "Default Currency set", "Country set"]:
				self.check(section, name, False, message=f"Cannot check — company '{COMPANY_NAME}' not found.")
			return

		self.check(
			section, "Abbreviation is GTS",
			company.get("abbr") == COMPANY_ABBR,
			expected=COMPANY_ABBR, actual=company.get("abbr", ""),
			message="" if company.get("abbr") == COMPANY_ABBR else f"Company abbreviation should be '{COMPANY_ABBR}', but found '{company.get('abbr', '')}'.",
		)
		self.check(
			section, "Default Cost Center set",
			bool(company.get("cost_center")),
			actual=company.get("cost_center", "Not set"),
			message="" if company.get("cost_center") else "Default Cost Center is not set. Open Company settings and configure it.",
		)
		# default_warehouse is on Stock Settings, not Company
		stock_settings = self.doc_exists("Stock Settings", "Stock Settings")
		default_wh = stock_settings.get("default_warehouse") if stock_settings else None
		self.check(
			section, "Default Warehouse set",
			bool(default_wh),
			actual=default_wh or "Not set",
			message="" if default_wh else "Default Warehouse is not set. Go to Stock Settings and set it.",
		)
		self.check(
			section, "Default Currency set",
			bool(company.get("default_currency")),
			actual=company.get("default_currency", "Not set"),
			message="" if company.get("default_currency") else "Default Currency is not set. This is usually configured during company creation.",
		)
		self.check(
			section, "Country set",
			bool(company.get("country")),
			actual=company.get("country", "Not set"),
			message="" if company.get("country") else "Country is not set. Open Company settings and configure it.",
		)

	# ── Fiscal Year ────────────────────────────────────────────

	def check_fiscal_year(self):
		section = "Fiscal Year"
		# Try common naming patterns for FY 2025-26
		fy = None
		for name in ["2025-2026", "2025-26", "FY 2025-26", "FY2025-26"]:
			fy = self.doc_exists("Fiscal Year", name)
			if fy:
				break

		if not fy:
			# Search by date range
			fy_list = self.doc_list(
				"Fiscal Year",
				filters=[
					["year_start_date", ">=", "2025-01-01"],
					["year_start_date", "<=", "2025-12-31"],
				],
				fields=["name", "disabled"],
			)
			if fy_list:
				fy = self.doc_exists("Fiscal Year", fy_list[0]["name"])

		self.check(
			section, "Fiscal Year 2025-26 exists",
			fy is not None,
			expected="FY 2025-26",
			actual=fy.get("name") if fy else "Not found",
			message="Checked names: 2025-2026, 2025-26, FY 2025-26" if not fy else "",
		)

	# ── Customers ──────────────────────────────────────────────

	def check_customers(self):
		section = "Customers"

		# Customer 1: Sunrise Electronics
		c1 = self.doc_exists("Customer", "Sunrise Electronics")
		self.check(
			section, "Sunrise Electronics exists", c1 is not None,
			expected="Sunrise Electronics",
			actual="Sunrise Electronics" if c1 else "Not found",
			message="" if c1 else "You haven't created customer 'Sunrise Electronics'. Go to Customer list and create it.",
		)
		if c1:
			self.check(
				section, "Sunrise Electronics - Customer Type is Company",
				c1.get("customer_type") == "Company",
				expected="Company", actual=c1.get("customer_type", ""),
			)
			self.check(
				section, "Sunrise Electronics - Customer Group is Commercial",
				c1.get("customer_group") == "Commercial",
				expected="Commercial", actual=c1.get("customer_group", ""),
			)
			self.check(
				section, "Sunrise Electronics - Territory is USA",
				c1.get("territory") in ("United States", "USA", "US"),
				expected="USA", actual=c1.get("territory", ""),
			)
			self.check(
				section, "Sunrise Electronics - Currency is USD",
				c1.get("default_currency") == "USD",
				expected="USD", actual=c1.get("default_currency", ""),
			)
		else:
			for name in [
				"Sunrise Electronics - Customer Type is Company",
				"Sunrise Electronics - Customer Group is Commercial",
				"Sunrise Electronics - Territory is USA",
				"Sunrise Electronics - Currency is USD",
			]:
				self.check(section, name, False, message="Cannot check — customer 'Sunrise Electronics' not found.")

		# Customer 2: Bright Future Technologies
		c2 = self.doc_exists("Customer", "Bright Future Technologies Pvt. Ltd.")
		self.check(
			section, "Bright Future Technologies Pvt. Ltd. exists", c2 is not None,
			expected="Bright Future Technologies Pvt. Ltd.",
			actual="Bright Future Technologies Pvt. Ltd." if c2 else "Not found",
			message="" if c2 else "You haven't created customer 'Bright Future Technologies Pvt. Ltd.'. Go to Customer list and create it.",
		)
		if c2:
			self.check(
				section, "Bright Future Technologies - Customer Type is Company",
				c2.get("customer_type") == "Company",
				expected="Company", actual=c2.get("customer_type", ""),
			)
			self.check(
				section, "Bright Future Technologies - Customer Group is Commercial",
				c2.get("customer_group") == "Commercial",
				expected="Commercial", actual=c2.get("customer_group", ""),
			)
		else:
			for name in [
				"Bright Future Technologies - Customer Type is Company",
				"Bright Future Technologies - Customer Group is Commercial",
			]:
				self.check(section, name, False, message="Cannot check — customer 'Bright Future Technologies Pvt. Ltd.' not found.")

		# Check for at least one address linked to any customer
		addr_links = self.doc_list(
			"Dynamic Link",
			filters={"link_doctype": "Customer", "parenttype": "Address"},
			fields=["name"],
		)
		self.check(
			section, "At least one customer has a billing/shipping address",
			len(addr_links) > 0,
		)

		# Check for at least one contact linked to any customer
		contact_links = self.doc_list(
			"Dynamic Link",
			filters={"link_doctype": "Customer", "parenttype": "Contact"},
			fields=["name"],
		)
		self.check(
			section, "At least one customer has a contact person",
			len(contact_links) > 0,
		)

	# ── Suppliers ──────────────────────────────────────────────

	def check_suppliers(self):
		section = "Suppliers"

		# Supplier 1: TechSource Distributors
		s1 = self.doc_exists("Supplier", "TechSource Distributors")
		self.check(
			section, "TechSource Distributors exists", s1 is not None,
			expected="TechSource Distributors",
			actual="TechSource Distributors" if s1 else "Not found",
			message="" if s1 else "You haven't created supplier 'TechSource Distributors'. Go to Supplier list and create it.",
		)
		if s1:
			self.check(
				section, "TechSource Distributors - Supplier Group is Local",
				s1.get("supplier_group") == "Local",
				expected="Local", actual=s1.get("supplier_group", ""),
			)
			self.check(
				section, "TechSource Distributors - Country is India",
				s1.get("country") == "India",
				expected="India", actual=s1.get("country", ""),
			)
		else:
			for name in [
				"TechSource Distributors - Supplier Group is Local",
				"TechSource Distributors - Country is India",
			]:
				self.check(section, name, False, message="Cannot check — supplier 'TechSource Distributors' not found.")

		# Supplier 2: Global Components Ltd.
		s2 = self.doc_exists("Supplier", "Global Components Ltd.")
		self.check(
			section, "Global Components Ltd. exists", s2 is not None,
			expected="Global Components Ltd.",
			actual="Global Components Ltd." if s2 else "Not found",
			message="" if s2 else "You haven't created supplier 'Global Components Ltd.'. Go to Supplier list and create it.",
		)
		if s2:
			self.check(
				section, "Global Components Ltd. - Supplier Group is International",
				s2.get("supplier_group") == "International",
				expected="International", actual=s2.get("supplier_group", ""),
			)
			self.check(
				section, "Global Components Ltd. - Currency is USD",
				s2.get("default_currency") == "USD",
				expected="USD", actual=s2.get("default_currency", ""),
			)
		else:
			for name in [
				"Global Components Ltd. - Supplier Group is International",
				"Global Components Ltd. - Currency is USD",
			]:
				self.check(section, name, False, message="Cannot check — supplier 'Global Components Ltd.' not found.")

		# Check for address and contact linked to suppliers
		addr_links = self.doc_list(
			"Dynamic Link",
			filters={"link_doctype": "Supplier", "parenttype": "Address"},
			fields=["name"],
		)
		self.check(
			section, "At least one supplier has an address",
			len(addr_links) > 0,
		)

		contact_links = self.doc_list(
			"Dynamic Link",
			filters={"link_doctype": "Supplier", "parenttype": "Contact"},
			fields=["name"],
		)
		self.check(
			section, "At least one supplier has a contact person",
			len(contact_links) > 0,
		)

	# ── Items ──────────────────────────────────────────────────

	def check_items(self):
		section = "Items"

		# Item 1: LED Monitor 24 inch
		item1 = self.doc_exists("Item", "LED Monitor 24 inch")
		self.check(
			section, "LED Monitor 24 inch exists", item1 is not None,
			expected="LED Monitor 24 inch",
			actual="LED Monitor 24 inch" if item1 else "Not found",
			message="" if item1 else "You haven't created item 'LED Monitor 24 inch'. Go to Item list and create it.",
		)
		if item1:
			self.check(
				section, "LED Monitor - Item Group is Products",
				item1.get("item_group") == "Products",
				expected="Products", actual=item1.get("item_group", ""),
			)
			self.check(
				section, "LED Monitor - Maintain Stock is Yes",
				item1.get("is_stock_item") == 1,
				expected="Yes", actual="Yes" if item1.get("is_stock_item") else "No",
			)
			self.check(
				section, "LED Monitor - Stock UOM is Nos",
				item1.get("stock_uom") in ("Nos", "nos", "Numbers"),
				expected="Nos", actual=item1.get("stock_uom", ""),
			)
			self.check(
				section, "LED Monitor - Valuation Method is FIFO",
				item1.get("valuation_method") == "FIFO",
				expected="FIFO", actual=item1.get("valuation_method", ""),
			)
		else:
			for name in [
				"LED Monitor - Item Group is Products",
				"LED Monitor - Maintain Stock is Yes",
				"LED Monitor - Stock UOM is Nos",
				"LED Monitor - Valuation Method is FIFO",
			]:
				self.check(section, name, False, message="Cannot check — item not found.")

		# Item 2: Wireless Keyboard (KB-WL)
		item2 = self.doc_exists("Item", "KB-WL")
		self.check(
			section, "Wireless Keyboard (KB-WL) exists", item2 is not None,
			expected="KB-WL",
			actual="KB-WL" if item2 else "Not found",
			message="" if item2 else "You haven't created item with code 'KB-WL'. Go to Item list and create it with Item Code: KB-WL.",
		)
		if item2:
			self.check(
				section, "KB-WL - Item Name is Wireless Keyboard",
				item2.get("item_name") == "Wireless Keyboard",
				expected="Wireless Keyboard", actual=item2.get("item_name", ""),
			)
			self.check(
				section, "KB-WL - Maintain Stock is Yes",
				item2.get("is_stock_item") == 1,
				expected="Yes", actual="Yes" if item2.get("is_stock_item") else "No",
			)
		else:
			for name in [
				"KB-WL - Item Name is Wireless Keyboard",
				"KB-WL - Maintain Stock is Yes",
			]:
				self.check(section, name, False, message="Cannot check — item not found.")

		# Item 3: Installation Service (SERV-INST)
		item3 = self.doc_exists("Item", "SERV-INST")
		self.check(
			section, "Installation Service (SERV-INST) exists", item3 is not None,
			expected="SERV-INST",
			actual="SERV-INST" if item3 else "Not found",
			message="" if item3 else "You haven't created item with code 'SERV-INST'. Go to Item list and create it with Item Code: SERV-INST.",
		)
		if item3:
			self.check(
				section, "SERV-INST - Item Group is Services",
				item3.get("item_group") == "Services",
				expected="Services", actual=item3.get("item_group", ""),
			)
			self.check(
				section, "SERV-INST - Maintain Stock is No",
				item3.get("is_stock_item") == 0,
				expected="No", actual="No" if not item3.get("is_stock_item") else "Yes",
			)
		else:
			for name in [
				"SERV-INST - Item Group is Services",
				"SERV-INST - Maintain Stock is No",
			]:
				self.check(section, name, False, message="Cannot check — item not found.")

		# Item 4: AMC (SERV-AMC)
		item4 = self.doc_exists("Item", "SERV-AMC")
		self.check(
			section, "Annual Maintenance Contract (SERV-AMC) exists", item4 is not None,
			expected="SERV-AMC",
			actual="SERV-AMC" if item4 else "Not found",
			message="" if item4 else "You haven't created item with code 'SERV-AMC'. Go to Item list and create it with Item Code: SERV-AMC.",
		)
		if item4:
			self.check(
				section, "SERV-AMC - Maintain Stock is No",
				item4.get("is_stock_item") == 0,
				expected="No", actual="No" if not item4.get("is_stock_item") else "Yes",
			)
		else:
			self.check(section, "SERV-AMC - Maintain Stock is No", False, message="Cannot check — item not found.")

	# ── Warehouses ─────────────────────────────────────────────

	def check_warehouses(self):
		section = "Warehouses"

		# Get all warehouses for the company
		all_warehouses = self.doc_list(
			"Warehouse",
			filters={"company": COMPANY_NAME},
			fields=["name", "parent_warehouse", "warehouse_name"],
			limit_page_length=200,
		)
		wh_names = [w.get("warehouse_name", w.get("name", "")) for w in all_warehouses]
		# Also check the full name with abbreviation suffix
		wh_full_names = [w.get("name", "") for w in all_warehouses]

		def wh_exists(name):
			"""Check if warehouse exists by name or full name (with - GTS suffix)."""
			return (
				name in wh_names
				or f"{name} - {COMPANY_ABBR}" in wh_full_names
				or any(name.lower() in n.lower() for n in wh_full_names)
			)

		# Mumbai Warehouse hierarchy
		warehouses_to_check = [
			("Mumbai Warehouse exists", "Mumbai Warehouse"),
			("Raw Material Store exists", "Raw Material Store"),
			("Finished Goods Store exists", "Finished Goods Store"),
			("WIP Warehouse exists", "WIP"),
			("Scrap Warehouse exists", "Scrap"),
			("Pune Warehouse exists", "Pune Warehouse"),
			("Pune - Trading Stock exists", "Trading Stock"),
			("Pune - Damaged Goods exists", "Damaged Goods"),
			("Delhi Warehouse exists", "Delhi Warehouse"),
		]
		for check_name, wh_name in warehouses_to_check:
			found = wh_exists(wh_name)
			self.check(
				section, check_name, found,
				expected=wh_name,
				actual=wh_name if found else "Not found",
				message="" if found else f"You haven't created warehouse '{wh_name}'. Go to Warehouse list and create it under the correct parent.",
			)

	# ── Users & Roles ──────────────────────────────────────────

	def check_users(self):
		section = "Users & Roles"

		users_config = {
			"sales@greenfield.com": {
				"name": "Rahul Sharma",
				"roles": ["Sales User"],
			},
			"purchase@greenfield.com": {
				"name": "Neha Verma",
				"roles": ["Purchase User"],
			},
			"accounts@greenfield.com": {
				"name": "Asmita Hodge",
				"roles": ["Accounts User", "Accounts Manager"],
			},
			"store@greenfield.com": {
				"name": "Mihir Nikam",
				"roles": ["Stock User", "Stock Manager"],
			},
			"hr@greenfield.com": {
				"name": "Kavita Rao",
				"roles": ["HR User", "HR Manager"],
			},
			"md@greenfield.com": {
				"name": "Kiran Rao",
				"roles": ["System Manager", "Accounts Manager", "Sales Manager"],
			},
		}

		for email, config in users_config.items():
			user = self.doc_exists("User", email)
			self.check(
				section, f"User {email} exists",
				user is not None,
				expected=email,
				actual=email if user else "Not found",
				message="" if user else f"You haven't created user '{email}'. Go to User list and create this user.",
			)
			if user:
				# Check roles
				user_roles = [r.get("role") for r in user.get("roles", [])]
				missing_roles = [r for r in config["roles"] if r not in user_roles]
				self.check(
					section, f"{email} has required roles ({', '.join(config['roles'])})",
					len(missing_roles) == 0,
					expected=", ".join(config["roles"]),
					actual=", ".join(user_roles) if user_roles else "No roles",
					message=f"Missing roles: {', '.join(missing_roles)}. Open the user and add these roles." if missing_roles else "",
				)
			else:
				self.check(
					section, f"{email} has required roles ({', '.join(config['roles'])})",
					False, message=f"Cannot check roles — user '{email}' not found.",
				)

	# ── Accounting Masters ─────────────────────────────────────

	def check_accounting_masters(self):
		section = "Chart of Accounts"

		required_accounts = [
			"Raw Material Inventory",
			"Finished Goods Inventory",
			"Bank - HDFC",
			"Petty Cash",
			"Furniture & Fixtures",
			"Computers & Equipment",
			"Sales - Trading",
			"Sales - Manufacturing",
			"Service Income",
			"Purchase - Raw Material",
			"Purchase - Trading Goods",
		]

		# Fetch all accounts for the company
		all_accounts = self.doc_list(
			"Account",
			filters={"company": COMPANY_NAME},
			fields=["name", "account_name"],
			limit_page_length=500,
		)
		account_names = [a.get("account_name", "") for a in all_accounts]
		account_full_names = [a.get("name", "") for a in all_accounts]

		for acct in required_accounts:
			found = (
				acct in account_names
				or f"{acct} - {COMPANY_ABBR}" in account_full_names
				or any(acct.lower() in n.lower() for n in account_full_names)
			)
			self.check(
				section, f"Account '{acct}' exists", found,
				message="" if found else f"You haven't created account '{acct}'. Go to Chart of Accounts and add it under the appropriate parent group.",
			)
