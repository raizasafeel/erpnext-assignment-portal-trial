from erpnext_assignment_portal.checks.base import BaseChecker


class Day2Checker(BaseChecker):
	def run(self) -> dict:
		self.check_purchase_cycle()
		self.check_stock_transfer()
		self.check_sales_cycle()
		return self.get_summary()

	# ── Scenario 1: Standard Sales Cycle ──────────────────────

	def check_sales_cycle(self):
		section = "Sales Cycle"

		# Find Sales Order for Sunrise Electronics
		so_list = self.doc_list(
			"Sales Order",
			filters={"customer": "Sunrise Electronics", "docstatus": 1},
			fields=["name", "customer", "status", "grand_total"],
		)
		has_so = len(so_list) > 0
		self.check(section, "Sales Order exists for Sunrise Electronics (submitted)", has_so,
			expected="Yes", actual="Yes" if has_so else "No")

		so_name = so_list[0]["name"] if has_so else None

		if has_so:
			# Check SO items
			so = self.doc_exists("Sales Order", so_name)
			items = so.get("items", []) if so else []
			item_map = {i.get("item_code") or i.get("item_name"): i for i in items}

			led_item = None
			service_item = None
			for item in items:
				code = item.get("item_code", "")
				name = item.get("item_name", "")
				if "LED Monitor" in name or "LED Monitor" in code:
					led_item = item
				if "Installation" in name or "SERV-INST" in code:
					service_item = item

			self.check(
				section, "SO has LED Monitor with qty 10",
				led_item is not None and led_item.get("qty") == 10,
				expected="10",
				actual=str(led_item.get("qty")) if led_item else "Not found",
			)
			self.check(
				section, "SO has Installation Service with qty 2",
				service_item is not None and service_item.get("qty") == 2,
				expected="2",
				actual=str(service_item.get("qty")) if service_item else "Not found",
			)
		else:
			self.check(section, "SO has LED Monitor with qty 10", False, message="No Sales Order found")
			self.check(section, "SO has Installation Service with qty 2", False, message="No Sales Order found")

		# Check Delivery Note (partial delivery)
		dn_filters = {"customer": "Sunrise Electronics", "docstatus": 1}
		if so_name:
			# Try to find DN linked to the SO
			dn_items = self.doc_list(
				"Delivery Note Item",
				filters={"against_sales_order": so_name, "docstatus": 1},
				fields=["parent"],
			)
			if dn_items:
				dn_filters = {"name": dn_items[0]["parent"], "docstatus": 1}

		dn_list = self.doc_list(
			"Delivery Note",
			filters=dn_filters,
			fields=["name", "customer", "status"],
		)
		has_dn = len(dn_list) > 0
		self.check(section, "Delivery Note exists for Sunrise Electronics (submitted)", has_dn,
			expected="Yes", actual="Yes" if has_dn else "No")

		if has_dn:
			dn = self.doc_exists("Delivery Note", dn_list[0]["name"])
			dn_items = dn.get("items", []) if dn else []

			led_dn = None
			service_dn = None
			for item in dn_items:
				code = item.get("item_code", "")
				name = item.get("item_name", "")
				if "LED Monitor" in name or "LED Monitor" in code:
					led_dn = item
				if "Installation" in name or "SERV-INST" in code:
					service_dn = item

			self.check(
				section, "Delivery Note has LED Monitor with qty 6 (partial)",
				led_dn is not None and led_dn.get("qty") == 6,
				expected="6",
				actual=str(led_dn.get("qty")) if led_dn else "Not found",
			)
			self.check(
				section, "Delivery Note has Installation Service with qty 2",
				service_dn is not None and service_dn.get("qty") == 2,
				expected="2",
				actual=str(service_dn.get("qty")) if service_dn else "Not found",
			)
		else:
			self.check(section, "Delivery Note has LED Monitor with qty 6 (partial)", False, message="No Delivery Note found")
			self.check(section, "Delivery Note has Installation Service with qty 2", False, message="No Delivery Note found")

		# Check Sales Invoice
		si_list = self.doc_list(
			"Sales Invoice",
			filters={"customer": "Sunrise Electronics", "docstatus": 1},
			fields=["name", "grand_total", "outstanding_amount"],
		)
		has_si = len(si_list) > 0
		self.check(section, "Sales Invoice exists for Sunrise Electronics (submitted)", has_si,
			expected="Yes", actual="Yes" if has_si else "No")

		# Check Payment Entry (partial payment ~50%)
		pe_list = self.doc_list(
			"Payment Entry",
			filters={
				"party_type": "Customer",
				"party": "Sunrise Electronics",
				"payment_type": "Receive",
				"docstatus": 1,
			},
			fields=["name", "paid_amount", "mode_of_payment"],
		)
		has_pe = len(pe_list) > 0
		self.check(section, "Payment Entry exists (Receive from Sunrise Electronics)", has_pe,
			expected="Yes", actual="Yes" if has_pe else "No")

		if has_pe and has_si:
			invoice_total = si_list[0].get("grand_total", 0)
			paid = pe_list[0].get("paid_amount", 0)
			# Check if payment is approximately 50% (allow 40-60% range)
			if invoice_total > 0:
				pct = (paid / invoice_total) * 100
				self.check(
					section, "Payment is approximately 50% of invoice",
					40 <= pct <= 60,
					expected=f"~50% of {invoice_total}",
					actual=f"{paid} ({pct:.0f}%)",
				)
			else:
				self.check(section, "Payment is approximately 50% of invoice", False, message="Invoice total is 0")
		elif not has_pe:
			self.check(section, "Payment is approximately 50% of invoice", False, message="No Payment Entry found")
		else:
			self.check(section, "Payment is approximately 50% of invoice", False, message="No Sales Invoice found")

	# ── Scenario 2: Standard Purchase Cycle ───────────────────

	def check_purchase_cycle(self):
		section = "Purchase Cycle"

		# Purchase Order for TechSource Distributors
		po_list = self.doc_list(
			"Purchase Order",
			filters={"supplier": "TechSource Distributors", "docstatus": 1},
			fields=["name", "supplier", "status", "grand_total"],
		)
		has_po = len(po_list) > 0
		self.check(section, "Purchase Order exists for TechSource Distributors (submitted)", has_po,
			expected="Yes", actual="Yes" if has_po else "No")

		po_name = po_list[0]["name"] if has_po else None

		if has_po:
			po = self.doc_exists("Purchase Order", po_name)
			po_items = po.get("items", []) if po else []

			led_po = None
			for item in po_items:
				code = item.get("item_code", "")
				name = item.get("item_name", "")
				if "LED Monitor" in name or "LED Monitor" in code:
					led_po = item
					break

			self.check(
				section, "PO has LED Monitor with qty 50",
				led_po is not None and led_po.get("qty") == 50,
				expected="50",
				actual=str(led_po.get("qty")) if led_po else "Not found",
			)
		else:
			self.check(section, "PO has LED Monitor with qty 50", False, message="No Purchase Order found")

		# Purchase Receipt (partial - 40 units)
		pr_filters = {"supplier": "TechSource Distributors", "docstatus": 1}
		pr_list = self.doc_list(
			"Purchase Receipt",
			filters=pr_filters,
			fields=["name", "supplier", "status"],
		)
		has_pr = len(pr_list) > 0
		self.check(section, "Purchase Receipt exists for TechSource Distributors (submitted)", has_pr,
			expected="Yes", actual="Yes" if has_pr else "No")

		if has_pr:
			pr = self.doc_exists("Purchase Receipt", pr_list[0]["name"])
			pr_items = pr.get("items", []) if pr else []

			led_pr = None
			for item in pr_items:
				code = item.get("item_code", "")
				name = item.get("item_name", "")
				if "LED Monitor" in name or "LED Monitor" in code:
					led_pr = item
					break

			self.check(
				section, "Purchase Receipt has LED Monitor with qty 40 (partial)",
				led_pr is not None and led_pr.get("qty") == 40,
				expected="40",
				actual=str(led_pr.get("qty")) if led_pr else "Not found",
			)
		else:
			self.check(section, "Purchase Receipt has LED Monitor with qty 40 (partial)", False, message="No Purchase Receipt found")

		# Purchase Invoice for delivered quantity
		pi_list = self.doc_list(
			"Purchase Invoice",
			filters={"supplier": "TechSource Distributors", "docstatus": 1},
			fields=["name", "grand_total"],
		)
		has_pi = len(pi_list) > 0
		self.check(section, "Purchase Invoice exists for TechSource Distributors (submitted)", has_pi,
			expected="Yes", actual="Yes" if has_pi else "No")

	# ── Inter-Warehouse Stock Transfer ────────────────────────

	def check_stock_transfer(self):
		section = "Stock Transfer"

		# Look for Stock Entry with purpose Material Transfer
		se_list = self.doc_list(
			"Stock Entry",
			filters={"purpose": "Material Transfer", "docstatus": 1},
			fields=["name", "purpose", "stock_entry_type"],
		)
		has_se = len(se_list) > 0
		self.check(section, "Stock Entry (Material Transfer) exists and is submitted", has_se,
			expected="Yes", actual="Yes" if has_se else "No")

		if has_se:
			# Check the most recent material transfer
			se = self.doc_exists("Stock Entry", se_list[0]["name"])
			se_items = se.get("items", []) if se else []

			transfer_item = None
			for item in se_items:
				code = item.get("item_code", "")
				name = item.get("item_name", "")
				if "LED Monitor" in name or "LED Monitor" in code:
					transfer_item = item
					break

			# If no LED Monitor found, check any item with qty 20
			if not transfer_item:
				for item in se_items:
					if item.get("qty") == 20:
						transfer_item = item
						break

			self.check(
				section, "Transfer quantity is 20 units",
				transfer_item is not None and transfer_item.get("qty") == 20,
				expected="20",
				actual=str(transfer_item.get("qty")) if transfer_item else "Not found",
			)

			if transfer_item:
				self.check(
					section, "Source warehouse is set",
					bool(transfer_item.get("s_warehouse")),
					expected="Yes", actual=transfer_item.get("s_warehouse") or "Not set",
				)
				self.check(
					section, "Target warehouse is set",
					bool(transfer_item.get("t_warehouse")),
					expected="Yes", actual=transfer_item.get("t_warehouse") or "Not set",
				)
			else:
				self.check(section, "Source warehouse is set", False, message="Transfer item not found")
				self.check(section, "Target warehouse is set", False, message="Transfer item not found")
		else:
			self.check(section, "Transfer quantity is 20 units", False, message="No Stock Entry found")
			self.check(section, "Source warehouse is set", False, message="No Stock Entry found")
			self.check(section, "Target warehouse is set", False, message="No Stock Entry found")
