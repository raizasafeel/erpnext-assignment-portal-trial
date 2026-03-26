from erpnext_assignment_portal.checks.base import BaseChecker, normalize, match, contains

COMPANY_NAME = "Greenfield Trading & Services Pvt. Ltd."
COMPANY_ABBR = "GTS"


class Day3Checker(BaseChecker):
	def run(self) -> dict:
		self.check_budget_setup()
		self.check_accounting_dimensions()
		self.check_journal_entries()
		self.check_bom()
		return self.get_summary()

	# ── Budget Setup ───────────────────────────────────────────

	def check_budget_setup(self):
		section = "Budget Setup"

		# Step 1: Cost Centers
		cost_centers = {
			"Sales Department": "Main",
			"Administration": "Main",
			"Operations": "Main",
		}
		all_cc = self.doc_list(
			"Cost Center",
			filters={"company": COMPANY_NAME},
			fields=["name", "cost_center_name", "parent_cost_center"],
			limit_page_length=200,
		)
		cc_names = [c.get("cost_center_name", "") for c in all_cc]
		cc_full_names = [c.get("name", "") for c in all_cc]

		for cc_name, parent in cost_centers.items():
			found = (
				any(match(cc_name, n) for n in cc_names)
				or any(match(f"{cc_name} - {COMPANY_ABBR}", n) for n in cc_full_names)
				or any(contains(n, cc_name) for n in cc_full_names)
			)
			self.check(section, f"Cost Center '{cc_name}' exists", found,
				expected="Yes", actual="Yes" if found else "No")

		# Step 2: Expense Accounts
		expense_accounts = [
			"Salary Expense",
			"Marketing Expense",
			"Office Rent",
			"Travel Expense",
		]
		all_accounts = self.doc_list(
			"Account",
			filters={"company": COMPANY_NAME},
			fields=["name", "account_name"],
			limit_page_length=0,
		)
		acct_names = [a.get("account_name", "") for a in all_accounts]
		acct_full_names = [a.get("name", "") for a in all_accounts]

		for acct in expense_accounts:
			norm_acct = normalize(acct)
			found = any(
				normalize(a.get("account_name", "")) == norm_acct
				or normalize(a.get("name", "")) == normalize(f"{acct} - {COMPANY_ABBR}")
				or norm_acct in normalize(a.get("name", ""))
				for a in all_accounts
			)
			self.check(section, f"Expense Account '{acct}' exists", found,
				expected="Yes", actual="Yes" if found else "No")

		# Step 3: Budget exists for Sales Department
		budgets = self.doc_list(
			"Budget",
			filters={
				"company": COMPANY_NAME,
				"budget_against": "Cost Center",
				"docstatus": 1,
			},
			fields=["name", "cost_center", "fiscal_year"],
		)

		sales_budget = None
		for b in budgets:
			cc = b.get("cost_center", "")
			if contains(cc, "Sales Department") or contains(cc, "Sales"):
				sales_budget = b
				break

		self.check(
			section,
			"Budget exists for Sales Department (submitted)",
			sales_budget is not None,
			expected="Yes", actual="Yes" if sales_budget is not None else "No",
		)

		if sales_budget:
			budget_doc = self.doc_exists("Budget", sales_budget["name"])
			budget_accounts = budget_doc.get("accounts", []) if budget_doc else []

			# Check Marketing Expense budget line
			marketing_line = None
			travel_line = None
			for line in budget_accounts:
				acct = line.get("account", "")
				if contains(acct, "Marketing"):
					marketing_line = line
				if contains(acct, "Travel"):
					travel_line = line

			self.check(
				section,
				"Budget has Marketing Expense allocation",
				marketing_line is not None,
				expected="500000",
				actual=str(marketing_line.get("budget_amount", "")) if marketing_line else "Not found",
			)
			self.check(
				section,
				"Budget has Travel Expense allocation",
				travel_line is not None,
				expected="200000",
				actual=str(travel_line.get("budget_amount", "")) if travel_line else "Not found",
			)

			# Step 4: Budget control actions
			self.check(
				section,
				"Action if Annual Budget Exceeded is 'Warn'",
				match(budget_doc.get("action_if_annual_budget_exceeded", ""), "Warn"),
				expected="Warn",
				actual=budget_doc.get("action_if_annual_budget_exceeded", "Not set"),
			)
			self.check(
				section,
				"Action if Monthly Budget Exceeded is 'Stop'",
				match(budget_doc.get("action_if_monthly_budget_exceeded", ""), "Stop"),
				expected="Stop",
				actual=budget_doc.get("action_if_monthly_budget_exceeded", "Not set"),
			)
		else:
			for name in [
				"Budget has Marketing Expense allocation",
				"Budget has Travel Expense allocation",
				"Action if Annual Budget Exceeded is 'Warn'",
				"Action if Monthly Budget Exceeded is 'Stop'",
			]:
				self.check(section, name, False, message="Budget not found")

	# ── Accounting Dimensions ──────────────────────────────────

	def check_accounting_dimensions(self):
		section = "Accounting Dimensions"

		# Step 1: Branch dimension exists
		dim = self.doc_exists("Accounting Dimension", "Branch")
		self.check(section, "Accounting Dimension 'Branch' exists", dim is not None,
			expected="Yes", actual="Yes" if dim is not None else "No")

		if dim:
			self.check(
				section,
				"Dimension document type is 'Branch'",
				match(dim.get("document_type", ""), "Branch"),
				expected="Branch",
				actual=dim.get("document_type", ""),
			)
		else:
			self.check(section, "Dimension document type is 'Branch'", False, message="Dimension not found")

		# Check branches exist
		branches = ["Mumbai Branch", "Pune Branch", "Bangalore Branch"]
		# Try alternate names too
		alternate_names = {
			"Mumbai Branch": ["Mumbai", "Mumbai Branch"],
			"Pune Branch": ["Pune", "Pune Branch"],
			"Bangalore Branch": ["Bangalore", "Bangalore Branch", "Bengaluru Branch", "Bengaluru"],
		}
		all_branches = self.doc_list("Branch", fields=["name"])
		branch_names = [b.get("name", "") for b in all_branches]

		for branch in branches:
			alts = alternate_names.get(branch, [branch])
			found = any(any(match(alt, bn) for bn in branch_names) for alt in alts) or any(
				contains(bn, branch.split()[0]) for bn in branch_names
			)
			self.check(section, f"Branch '{branch}' exists", found,
				expected="Yes", actual="Yes" if found else "No")

		# Sales Invoice with Branch = Mumbai
		si_list = self.doc_list(
			"Sales Invoice",
			filters={
				"customer": "Sunrise Electronics",
				"docstatus": 1,
			},
			fields=["name", "branch"],
		)
		si_with_mumbai = any(
			contains(si.get("branch", ""), "Mumbai") for si in si_list
		)
		self.check(
			section,
			"Sales Invoice for Sunrise Electronics with Branch = Mumbai",
			si_with_mumbai,
			expected="Yes", actual="Yes" if si_with_mumbai else "No",
		)

		if si_with_mumbai:
			# Verify items
			for si in si_list:
				if contains(si.get("branch", ""), "Mumbai"):
					si_doc = self.doc_exists("Sales Invoice", si["name"])
					items = si_doc.get("items", []) if si_doc else []
					led_item = None
					for item in items:
						if contains(item.get("item_name", ""), "LED Monitor") or contains(item.get("item_code", ""), "LED Monitor"):
							led_item = item
							break
					self.check(
						section,
						"Mumbai Sales Invoice has LED Monitor with qty 5",
						led_item is not None and led_item.get("qty") == 5,
						expected="5",
						actual=str(led_item.get("qty")) if led_item else "Not found",
					)
					break
		else:
			self.check(
				section,
				"Mumbai Sales Invoice has LED Monitor with qty 5",
				False,
				message="No Sales Invoice with Mumbai branch found",
			)

		# Purchase Invoice with Branch = Pune
		pi_list = self.doc_list(
			"Purchase Invoice",
			filters={
				"supplier": "TechSource Distributors",
				"docstatus": 1,
			},
			fields=["name", "branch"],
		)
		pi_with_pune = any(
			contains(pi.get("branch", ""), "Pune") for pi in pi_list
		)
		self.check(
			section,
			"Purchase Invoice for TechSource Distributors with Branch = Pune",
			pi_with_pune,
			expected="Yes", actual="Yes" if pi_with_pune else "No",
		)

		if pi_with_pune:
			for pi in pi_list:
				if contains(pi.get("branch", ""), "Pune"):
					pi_doc = self.doc_exists("Purchase Invoice", pi["name"])
					items = pi_doc.get("items", []) if pi_doc else []
					led_item = None
					for item in items:
						if contains(item.get("item_name", ""), "LED Monitor") or contains(item.get("item_code", ""), "LED Monitor"):
							led_item = item
							break
					self.check(
						section,
						"Pune Purchase Invoice has LED Monitor with qty 10",
						led_item is not None and led_item.get("qty") == 10,
						expected="10",
						actual=str(led_item.get("qty")) if led_item else "Not found",
					)
					break
		else:
			self.check(
				section,
				"Pune Purchase Invoice has LED Monitor with qty 10",
				False,
				message="No Purchase Invoice with Pune branch found",
			)

	# ── Journal Entries ────────────────────────────────────────

	def check_journal_entries(self):
		section = "Journal Entries"

		# Verify required accounts exist first
		required_accounts = [
			"Bank Account",
			"Office Rent Expense",
			"Salary Expense",
			"Depreciation Expense",
			"Office Equipment",
			"Employee Advance",
		]
		all_accounts = self.doc_list(
			"Account",
			filters={"company": COMPANY_NAME},
			fields=["name", "account_name"],
			limit_page_length=0,
		)
		acct_names = [a.get("account_name", "") for a in all_accounts]
		acct_full_names = [a.get("name", "") for a in all_accounts]

		for acct in required_accounts:
			norm_acct = normalize(acct)
			found = any(
				normalize(a.get("account_name", "")) == norm_acct
				or normalize(a.get("name", "")) == normalize(f"{acct} - {COMPANY_ABBR}")
				or norm_acct in normalize(a.get("name", ""))
				for a in all_accounts
			)
			self.check(section, f"Account '{acct}' exists", found,
				expected="Yes", actual="Yes" if found else "No")

		# Get all submitted Journal Entries for the company
		je_list = self.doc_list(
			"Journal Entry",
			filters={"company": COMPANY_NAME, "docstatus": 1},
			fields=["name"],
			limit_page_length=200,
		)

		# Helper to find a JE with specific debit/credit accounts and amounts
		def find_je(debit_keyword, credit_keyword, debit_amount, credit_amount):
			for je_ref in je_list:
				je = self.doc_exists("Journal Entry", je_ref["name"])
				if not je:
					continue
				entries = je.get("accounts", [])
				has_debit = False
				has_credit = False
				for entry in entries:
					acct = entry.get("account", "")
					if contains(acct, debit_keyword) and entry.get("debit_in_account_currency", 0) == debit_amount:
						has_debit = True
					if contains(acct, credit_keyword) and entry.get("credit_in_account_currency", 0) == credit_amount:
						has_credit = True
				if has_debit and has_credit:
					return je
			return None

		# Step 2: Office Rent Payment (Debit: Office Rent 50000, Credit: Bank 50000)
		je_rent = find_je("Office Rent", "Bank", 50000, 50000)
		self.check(
			section,
			"Journal Entry: Office Rent Payment (₹50,000)",
			je_rent is not None,
			expected="Debit Office Rent 50,000 / Credit Bank 50,000",
			actual="Found" if je_rent is not None else "Not found",
		)

		# Step 3: Salary Expense (Debit: Salary Expense 100000, Credit: Salary Payable 100000)
		je_salary = find_je("Salary Expense", "Salary Payable", 100000, 100000)
		self.check(
			section,
			"Journal Entry: Salary Expense (₹1,00,000)",
			je_salary is not None,
			expected="Debit Salary Expense 1,00,000 / Credit Salary Payable 1,00,000",
			actual="Found" if je_salary is not None else "Not found",
		)

		# Step 4: Depreciation Entry (Debit: Depreciation 10000, Credit: Office Equipment 10000)
		je_dep = find_je("Depreciation", "Office Equipment", 10000, 10000)
		self.check(
			section,
			"Journal Entry: Depreciation (₹10,000)",
			je_dep is not None,
			expected="Debit Depreciation 10,000 / Credit Office Equipment 10,000",
			actual="Found" if je_dep is not None else "Not found",
		)

		# Step 5: Employee Advance (Debit: Employee Advance 20000, Credit: Bank 20000)
		je_advance = find_je("Employee Advance", "Bank", 20000, 20000)
		self.check(
			section,
			"Journal Entry: Employee Advance (₹20,000)",
			je_advance is not None,
			expected="Debit Employee Advance 20,000 / Credit Bank 20,000",
			actual="Found" if je_advance is not None else "Not found",
		)

	# ── BOM Creation ───────────────────────────────────────────

	def check_bom(self):
		section = "BOM Creation"

		# Check if any BOM exists for the company
		bom_list = self.doc_list(
			"BOM",
			filters={"company": COMPANY_NAME, "docstatus": 1},
			fields=["name", "item", "item_name", "is_active", "is_default"],
		)
		self.check(
			section,
			"At least one submitted BOM exists",
			len(bom_list) > 0,
			expected="Yes", actual="Yes" if len(bom_list) > 0 else "No",
		)

		if bom_list:
			bom = self.doc_exists("BOM", bom_list[0]["name"])
			if bom:
				self.check(
					section,
					"BOM has raw materials (items in BOM)",
					len(bom.get("items", [])) > 0,
					expected="Yes",
					actual=f"{len(bom.get('items', []))} items" if bom.get("items") else "0 items",
				)
				self.check(
					section,
					"BOM is active",
					bom.get("is_active") == 1,
					expected="Yes", actual="Yes" if bom.get("is_active") == 1 else "No",
				)
				self.check(
					section,
					"BOM is default",
					bom.get("is_default") == 1,
					expected="Yes", actual="Yes" if bom.get("is_default") == 1 else "No",
				)
			else:
				for name in ["BOM has raw materials (items in BOM)", "BOM is active", "BOM is default"]:
					self.check(section, name, False, message="Could not fetch BOM details")
		else:
			for name in ["BOM has raw materials (items in BOM)", "BOM is active", "BOM is default"]:
				self.check(section, name, False, message="No BOM found")
