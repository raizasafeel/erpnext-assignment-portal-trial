from erpnext_assignment_portal.checks.base import BaseChecker, normalize, match, contains

COMPANY_NAME = "Greenfield Trading & Services Pvt. Ltd."
COMPANY_ABBR = "GTS"


class Day1Checker(BaseChecker):
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

	# Company Setup ──

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
			for name in ["Abbreviation is GTS", "Default Cost Center set", "Default Warehouse set", "Default Currency set", "Country set", "Chart of Accounts template is set"]:
				self.check(section, name, False, message=f"Cannot check — company '{COMPANY_NAME}' not found.")
			return

		self.check(
			section, "Abbreviation is GTS",
			match(company.get("abbr", ""), COMPANY_ABBR),
			expected=COMPANY_ABBR, actual=company.get("abbr", ""),
			message="" if match(company.get("abbr", ""), COMPANY_ABBR) else f"Company abbreviation should be '{COMPANY_ABBR}', but found '{company.get('abbr', '')}'.",
		)
		self.check(
			section, "Default Cost Center set",
			bool(company.get("cost_center")),
			expected="Any cost center",
			actual=company.get("cost_center", "Not set"),
			message="" if company.get("cost_center") else "Default Cost Center is not set. Open Company settings and configure it.",
		)
		# default_warehouse is on Stock Settings, not Company
		stock_settings = self.doc_exists("Stock Settings", "Stock Settings")
		default_wh = stock_settings.get("default_warehouse") if stock_settings else None
		self.check(
			section, "Default Warehouse set",
			bool(default_wh),
			expected="Any warehouse",
			actual=default_wh or "Not set",
			message="" if default_wh else "Default Warehouse is not set. Go to Stock Settings and set it.",
		)
		self.check(
			section, "Default Currency set",
			bool(company.get("default_currency")),
			expected="Any currency",
			actual=company.get("default_currency", "Not set"),
			message="" if company.get("default_currency") else "Default Currency is not set. This is usually configured during company creation.",
		)
		self.check(
			section, "Country set",
			bool(company.get("country")),
			expected="Any country",
			actual=company.get("country", "Not set"),
			message="" if company.get("country") else "Country is not set. Open Company settings and configure it.",
		)
		self.check(
			section, "Chart of Accounts template is set",
			bool(company.get("chart_of_accounts")),
			expected="Any template",
			actual=company.get("chart_of_accounts", "Not set"),
			message="" if company.get("chart_of_accounts") else "Chart of Accounts template is not set. This is configured during company creation.",
		)

	# Fiscal Year 

	def check_fiscal_year(self):
		section = "Fiscal Year"
		fy = None
		for name in ["2025-2026", "2025-26", "FY 2025-26", "FY2025-26"]:
			fy = self.doc_exists("Fiscal Year", name)
			if fy:
				break

		if not fy:
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

	# Helpers

	def _has_contact(self, link_doctype, link_name):
		return bool(self.doc_list(
			"Contact",
			filters=[
				["Dynamic Link", "link_doctype", "=", link_doctype],
				["Dynamic Link", "link_name", "=", link_name],
			],
		))

	def _has_address(self, link_doctype, link_name, address_type=None):
		addrs = self.doc_list(
			"Address",
			filters=[
				["Dynamic Link", "link_doctype", "=", link_doctype],
				["Dynamic Link", "link_name", "=", link_name],
			],
			fields=["name", "address_type", "is_primary_address", "is_shipping_address"],
		)
		if not address_type:
			return bool(addrs)
		for a in addrs:
			if match(a.get("address_type", ""), address_type):
				return True
			if match(address_type, "Billing") and a.get("is_primary_address"):
				return True
			if match(address_type, "Shipping") and a.get("is_shipping_address"):
				return True
		return False

	def _get_item_price(self, item_code, price_list):
		prices = self.doc_list(
			"Item Price",
			filters={"item_code": item_code, "price_list": price_list, "selling": 1 if contains(price_list, "Selling") else 0, "buying": 1 if contains(price_list, "Buying") else 0},
			fields=["price_list_rate"],
		)
		return prices[0].get("price_list_rate") if prices else None

	# Customers 

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
				match(c1.get("customer_type", ""), "Company"),
				expected="Company", actual=c1.get("customer_type", ""),
			)
			self.check(
				section, "Sunrise Electronics - Customer Group is Commercial",
				match(c1.get("customer_group", ""), "Commercial"),
				expected="Commercial", actual=c1.get("customer_group", ""),
			)
			self.check(
				section, "Sunrise Electronics - Territory is USA",
				match(c1.get("territory", ""), "United States") or match(c1.get("territory", ""), "USA") or match(c1.get("territory", ""), "US"),
				expected="USA", actual=c1.get("territory", ""),
			)
			self.check(
				section, "Sunrise Electronics - Currency is USD",
				match(c1.get("default_currency", ""), "USD"),
				expected="USD", actual=c1.get("default_currency", ""),
			)
			passed = self._has_address("Customer", "Sunrise Electronics", "Billing")
			self.check(
				section, "Sunrise Electronics - has billing address",
				passed,
				expected="Yes", actual="Yes" if passed else "No",
			)
			passed = self._has_address("Customer", "Sunrise Electronics", "Shipping")
			self.check(
				section, "Sunrise Electronics - has shipping address",
				passed,
				expected="Yes", actual="Yes" if passed else "No",
			)
			passed = self._has_contact("Customer", "Sunrise Electronics")
			self.check(
				section, "Sunrise Electronics - has a contact person",
				passed,
				expected="Yes", actual="Yes" if passed else "No",
			)
		else:
			for name in [
				"Sunrise Electronics - Customer Type is Company",
				"Sunrise Electronics - Customer Group is Commercial",
				"Sunrise Electronics - Territory is USA",
				"Sunrise Electronics - Currency is USD",
				"Sunrise Electronics - has billing address",
				"Sunrise Electronics - has shipping address",
				"Sunrise Electronics - has a contact person",
			]:
				self.check(section, name, False, message="Cannot check — customer not found.")

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
				match(c2.get("customer_type", ""), "Company"),
				expected="Company", actual=c2.get("customer_type", ""),
			)
			self.check(
				section, "Bright Future Technologies - Customer Group is Commercial",
				match(c2.get("customer_group", ""), "Commercial"),
				expected="Commercial", actual=c2.get("customer_group", ""),
			)
			passed = self._has_address("Customer", "Bright Future Technologies Pvt. Ltd.", "Billing")
			self.check(
				section, "Bright Future Technologies - has billing address",
				passed,
				expected="Yes", actual="Yes" if passed else "No",
			)
			passed = self._has_address("Customer", "Bright Future Technologies Pvt. Ltd.", "Shipping")
			self.check(
				section, "Bright Future Technologies - has shipping address",
				passed,
				expected="Yes", actual="Yes" if passed else "No",
			)
			passed = self._has_contact("Customer", "Bright Future Technologies Pvt. Ltd.")
			self.check(
				section, "Bright Future Technologies - has a contact person",
				passed,
				expected="Yes", actual="Yes" if passed else "No",
			)
		else:
			for name in [
				"Bright Future Technologies - Customer Type is Company",
				"Bright Future Technologies - Customer Group is Commercial",
				"Bright Future Technologies - has billing address",
				"Bright Future Technologies - has shipping address",
				"Bright Future Technologies - has a contact person",
			]:
				self.check(section, name, False, message="Cannot check — customer not found.")

	# Suppliers 

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
				match(s1.get("supplier_group", ""), "Local"),
				expected="Local", actual=s1.get("supplier_group", ""),
			)
			self.check(
				section, "TechSource Distributors - Country is India",
				match(s1.get("country", ""), "India"),
				expected="India", actual=s1.get("country", ""),
			)
			passed = self._has_address("Supplier", "TechSource Distributors")
			self.check(
				section, "TechSource Distributors - has an address",
				passed,
				expected="Yes", actual="Yes" if passed else "No",
			)
			passed = self._has_contact("Supplier", "TechSource Distributors")
			self.check(
				section, "TechSource Distributors - has a contact person",
				passed,
				expected="Yes", actual="Yes" if passed else "No",
			)
		else:
			for name in [
				"TechSource Distributors - Supplier Group is Local",
				"TechSource Distributors - Country is India",
				"TechSource Distributors - has an address",
				"TechSource Distributors - has a contact person",
			]:
				self.check(section, name, False, message="Cannot check — supplier not found.")

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
				match(s2.get("supplier_group", ""), "International"),
				expected="International", actual=s2.get("supplier_group", ""),
			)
			self.check(
				section, "Global Components Ltd. - Currency is USD",
				match(s2.get("default_currency", ""), "USD"),
				expected="USD", actual=s2.get("default_currency", ""),
			)
			passed = self._has_address("Supplier", "Global Components Ltd.")
			self.check(
				section, "Global Components Ltd. - has an address",
				passed,
				expected="Yes", actual="Yes" if passed else "No",
			)
			passed = self._has_contact("Supplier", "Global Components Ltd.")
			self.check(
				section, "Global Components Ltd. - has a contact person",
				passed,
				expected="Yes", actual="Yes" if passed else "No",
			)
		else:
			for name in [
				"Global Components Ltd. - Supplier Group is International",
				"Global Components Ltd. - Currency is USD",
				"Global Components Ltd. - has an address",
				"Global Components Ltd. - has a contact person",
			]:
				self.check(section, name, False, message="Cannot check — supplier not found.")

	# Items 

	def _check_item(self, section, item_code, label, checks, not_found_names):
		item = self.doc_exists("Item", item_code)
		self.check(
			section, f"{label} exists", item is not None,
			expected=item_code,
			actual=item_code if item else "Not found",
			message="" if item else f"You haven't created item '{item_code}'.",
		)
		if not item:
			for name in not_found_names:
				self.check(section, name, False, message="Cannot check — item not found.")
			return
		for check_fn in checks:
			check_fn(item)

	def check_items(self):
		section = "Items"

		# Item 1: LED Monitor 24 inch
		def item1_checks(item):
			self.check(section, "LED Monitor - Item Group is Products",
				match(item.get("item_group", ""), "Products"),
				expected="Products", actual=item.get("item_group", ""))
			self.check(section, "LED Monitor - Maintain Stock is Yes",
				item.get("is_stock_item") == 1,
				expected="Yes", actual="Yes" if item.get("is_stock_item") else "No")
			self.check(section, "LED Monitor - Stock UOM is Nos",
				match(item.get("stock_uom", ""), "Nos") or match(item.get("stock_uom", ""), "Numbers"),
				expected="Nos", actual=item.get("stock_uom", ""))
			self.check(section, "LED Monitor - Valuation Method is FIFO",
				match(item.get("valuation_method", ""), "FIFO"),
				expected="FIFO", actual=item.get("valuation_method", ""))
			val_rate = item.get("valuation_rate", 0)
			self.check(section, "LED Monitor - Valuation Rate is 5000",
				val_rate == 5000,
				expected="5000", actual=str(val_rate))

		self._check_item(section, "LED Monitor 24 inch", "LED Monitor 24 inch", [item1_checks], [
			"LED Monitor - Item Group is Products",
			"LED Monitor - Maintain Stock is Yes",
			"LED Monitor - Stock UOM is Nos",
			"LED Monitor - Valuation Method is FIFO",
			"LED Monitor - Valuation Rate is 5000",
		])

		# Item 2: Wireless Keyboard (KB-WL)
		def item2_checks(item):
			self.check(section, "KB-WL - Item Name is Wireless Keyboard",
				match(item.get("item_name", ""), "Wireless Keyboard"),
				expected="Wireless Keyboard", actual=item.get("item_name", ""))
			self.check(section, "KB-WL - Maintain Stock is Yes",
				item.get("is_stock_item") == 1,
				expected="Yes", actual="Yes" if item.get("is_stock_item") else "No")
			self.check(section, "KB-WL - Stock UOM is Nos",
				match(item.get("stock_uom", ""), "Nos") or match(item.get("stock_uom", ""), "Numbers"),
				expected="Nos", actual=item.get("stock_uom", ""))
			selling = self._get_item_price("KB-WL", "Standard Selling")
			self.check(section, "KB-WL - Standard Selling Price is 1200",
				selling == 1200,
				expected="1200", actual=str(selling) if selling else "Not set")
			buying = self._get_item_price("KB-WL", "Standard Buying")
			self.check(section, "KB-WL - Standard Buying Price is 800",
				buying == 800,
				expected="800", actual=str(buying) if buying else "Not set")

		self._check_item(section, "KB-WL", "Wireless Keyboard (KB-WL)", [item2_checks], [
			"KB-WL - Item Name is Wireless Keyboard",
			"KB-WL - Maintain Stock is Yes",
			"KB-WL - Stock UOM is Nos",
			"KB-WL - Standard Selling Price is 1200",
			"KB-WL - Standard Buying Price is 800",
		])

		# Item 3: Installation Service (SERV-INST)
		def item3_checks(item):
			self.check(section, "SERV-INST - Item Group is Services",
				match(item.get("item_group", ""), "Services"),
				expected="Services", actual=item.get("item_group", ""))
			self.check(section, "SERV-INST - Maintain Stock is No",
				item.get("is_stock_item") == 0,
				expected="No", actual="No" if not item.get("is_stock_item") else "Yes")
			defaults = item.get("item_defaults", [])
			income_acct = ""
			for d in defaults:
				if d.get("income_account"):
					income_acct = d.get("income_account", "")
					break
			expected_acct = f"Service - {COMPANY_ABBR}"
			self.check(section, "SERV-INST - Income Account is Service Income",
				match(income_acct, expected_acct),
				expected=expected_acct, actual=income_acct or "Not set")
			selling = self._get_item_price("SERV-INST", "Standard Selling")
			self.check(section, "SERV-INST - Standard Selling Price is 1500",
				selling == 1500,
				expected="1500", actual=str(selling) if selling else "Not set")

		self._check_item(section, "SERV-INST", "Installation Service (SERV-INST)", [item3_checks], [
			"SERV-INST - Item Group is Services",
			"SERV-INST - Maintain Stock is No",
			"SERV-INST - Income Account is Service Income",
			"SERV-INST - Standard Selling Price is 1500",
		])

		# Item 4: AMC (SERV-AMC)
		def item4_checks(item):
			self.check(section, "SERV-AMC - Maintain Stock is No",
				item.get("is_stock_item") == 0,
				expected="No", actual="No" if not item.get("is_stock_item") else "Yes")
			selling = self._get_item_price("SERV-AMC", "Standard Selling")
			self.check(section, "SERV-AMC - Standard Selling Price is 5000",
				selling == 5000,
				expected="5000", actual=str(selling) if selling else "Not set")

		self._check_item(section, "SERV-AMC", "Annual Maintenance Contract (SERV-AMC)", [item4_checks], [
			"SERV-AMC - Maintain Stock is No",
			"SERV-AMC - Standard Selling Price is 5000",
		])

	# Warehouses ─

	def check_warehouses(self):
		section = "Warehouses"

		all_warehouses = self.doc_list(
			"Warehouse",
			filters={"company": COMPANY_NAME},
			fields=["name", "parent_warehouse", "warehouse_name"],
			limit_page_length=200,
		)

		# Build lookup: {warehouse_name: [parent_warehouse_name, ...]}
		wh_by_name: dict[str, list[str]] = {}
		for w in all_warehouses:
			wh_name = w.get("warehouse_name", "")
			parent = w.get("parent_warehouse", "")
			wh_by_name.setdefault(wh_name, []).append(parent)

		def wh_exists(name, parent_name=None):
			matching_parents = []
			for wh_name_key, parents in wh_by_name.items():
				if match(wh_name_key, name):
					matching_parents.extend(parents)
			if not matching_parents:
				return False
			if parent_name is None:
				return True
			expected_parent = f"{parent_name} - {COMPANY_ABBR}"
			return any(match(p, expected_parent) for p in matching_parents)

		# (check label, warehouse name, required parent or None for top-level)
		warehouses_to_check = [
			("Mumbai Warehouse", "Mumbai Warehouse", None),
			("Mumbai - Raw Material Store", "Raw Material", "Mumbai Warehouse"),
			("Mumbai - Finished Goods Store", "Finished Goods", "Mumbai Warehouse"),
			("Mumbai - WIP", "Work in Progress", "Mumbai Warehouse"),
			("Mumbai - Scrap", "Scrap", "Mumbai Warehouse"),
			("Pune Warehouse", "Pune Warehouse", None),
			("Pune - Trading Stock", "Pune Trading Stock", "Pune Warehouse"),
			("Pune - Damaged Goods", "Pune Damaged Goods", "Pune Warehouse"),
			("Delhi Warehouse", "Delhi Warehouse", None),
			("Delhi - Trading Stock", "Delhi Trading Stock", "Delhi Warehouse"),
			("Delhi - Damaged Goods", "Delhi Damaged Goods", "Delhi Warehouse"),
		]
		for check_label, wh_name, parent_name in warehouses_to_check:
			found = wh_exists(wh_name, parent_name)
			expected = f"{wh_name} under {parent_name}" if parent_name else wh_name
			self.check(
				section, check_label, found,
				expected=expected,
				actual=expected if found else "Not found",
				message="" if found else f"Warehouse '{wh_name}' not found{f' under {parent_name}' if parent_name else ''}.",
			)

	# Users & Roles ──

	def check_users(self):
		section = "Users & Roles"

		role_profiles = {
			"Sales Executive": ["Sales User"],
			"Purchase Officer": ["Purchase User", "Stock User"],
			"Accountant": ["Accounts User", "Accounts Manager"],
			"Store Manager": ["Stock User", "Stock Manager"],
			"HR Manager": ["HR User", "HR Manager"],
			"Managing Director": ["System Manager", "Accounts Manager", "Sales Manager"],
		}

		users_config = [
			{"email": "sales@greenfield.com", "first_name": "Rahul", "last_name": "Sharma", "profile": "Sales Executive"},
			{"email": "purchase@greenfield.com", "first_name": "Neha", "last_name": "Verma", "profile": "Purchase Officer"},
			{"email": "accounts@greenfield.com", "first_name": "Asmita", "last_name": "Hodge", "profile": "Accountant"},
			{"email": "store@greenfield.com", "first_name": "Mihir", "last_name": "Nikam", "profile": "Store Manager"},
			{"email": "hr@greenfield.com", "first_name": "Kavita", "last_name": "Rao", "profile": "HR Manager"},
			{"email": "md@greenfield.com", "first_name": "Kiran", "last_name": "Rao", "profile": "Managing Director"},
		]

		# Step 1 & 2: Check Role Profiles exist and have the right roles
		for profile_name, expected_roles in role_profiles.items():
			profile = self.doc_exists("Role Profile", profile_name)
			self.check(
				section, f"Role Profile '{profile_name}' exists",
				profile is not None,
				expected=profile_name, actual=profile_name if profile else "Not found",
			)
			if profile:
				profile_roles = [r.get("role") for r in profile.get("roles", [])]
				missing = [r for r in expected_roles if not any(match(r, pr) for pr in profile_roles)]
				extra = [r for r in profile_roles if not any(match(r, er) for er in expected_roles)]
				self.check(
					section, f"Role Profile '{profile_name}' has all required roles",
					not missing,
					expected=", ".join(expected_roles),
					actual=", ".join(profile_roles) if profile_roles else "No roles",
					message=f"Missing: {', '.join(missing)}" if missing else "",
				)
				self.check(
					section, f"Role Profile '{profile_name}' has no extra roles",
					not extra,
					expected=", ".join(expected_roles),
					actual=", ".join(profile_roles),
					message=f"Extra roles: {', '.join(extra)}. Remove them." if extra else "",
				)
			else:
				for name in [
					f"Role Profile '{profile_name}' has all required roles",
					f"Role Profile '{profile_name}' has no extra roles",
				]:
					self.check(section, name, False, message=f"Cannot check — Role Profile '{profile_name}' not found.")

		# Step 3 & 4: Check users exist with correct name and profile
		for u in users_config:
			email = u["email"]
			full_name = f"{u['first_name']} {u['last_name']}"
			profile_name = u["profile"]

			user = self.doc_exists("User", email)
			self.check(section, f"User {email} exists", user is not None,
				expected=email, actual=email if user else "Not found")

			if not user:
				for name in [
					f"{email} - name is {full_name}",
					f"{email} - has Role Profile '{profile_name}'",
				]:
					self.check(section, name, False, message="Cannot check — user not found.")
				continue

			actual_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
			self.check(
				section, f"{email} - name is {full_name}",
				match(user.get("first_name", ""), u["first_name"]) and match(user.get("last_name", ""), u["last_name"]),
				expected=full_name, actual=actual_name or "Not set",
			)

			actual_profile = user.get("role_profile_name", "") or ""
			self.check(
				section, f"{email} - has Role Profile '{profile_name}'",
				match(actual_profile, profile_name),
				expected=profile_name, actual=actual_profile or "Not set",
			)

	# Accounting Masters ─

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
			limit_page_length=0,
		)
		account_names = [a.get("account_name", "") for a in all_accounts]
		account_full_names = [a.get("name", "") for a in all_accounts]

		for acct in required_accounts:
			found_acct = ""
			norm_acct = normalize(acct)
			for a in all_accounts:
				if normalize(a.get("account_name", "")) == norm_acct or normalize(a.get("name", "")) == normalize(f"{acct} - {COMPANY_ABBR}"):
					found_acct = a.get("name", "")
					break
			if not found_acct:
				for a in all_accounts:
					if norm_acct in normalize(a.get("name", "")):
						found_acct = a.get("name", "")
						break
			self.check(
				section, f"Account '{acct}' exists", bool(found_acct),
				expected=f"{acct} - {COMPANY_ABBR}",
				actual=found_acct or "Not found",
				message="" if found_acct else f"Account '{acct}' not found. Go to Chart of Accounts and add it.",
			)
