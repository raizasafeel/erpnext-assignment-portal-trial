from frappe.frappeclient import FrappeClient


class BaseChecker:
	def __init__(self, site_url: str, username: str, password: str):
		self.client = FrappeClient(site_url, username, password)
		self.client.session.headers.update({
			"Cache-Control": "no-cache, no-store, must-revalidate",
			"Pragma": "no-cache",
		})
		self.results: list[dict] = []

	def check(
		self,
		section: str,
		name: str,
		passed: bool,
		expected: str = "",
		actual: str = "",
		message: str = "",
	):
		self.results.append(
			{
				"section": section,
				"check": name,
				"status": "Pass" if passed else "Fail",
				"expected": str(expected),
				"actual": str(actual),
				"message": message,
			}
		)

	def doc_exists(self, doctype: str, name: str) -> dict | None:
		try:
			return self.client.get_doc(doctype, name)
		except Exception:
			return None

	def doc_list(
		self,
		doctype: str,
		filters: dict | list | None = None,
		fields: list[str] | None = None,
		limit_page_length: int = 100,
	) -> list[dict]:
		try:
			return self.client.get_list(
				doctype,
				filters=filters,
				fields=fields or ["name"],
				limit_page_length=limit_page_length,
			)
		except Exception:
			return []

	def get_value(self, doctype: str, name: str, fieldname: str):
		try:
			doc = self.client.get_doc(doctype, name)
			return doc.get(fieldname)
		except Exception:
			return None

	def has_linked_doc(self, doctype: str, link_doctype: str, link_name: str) -> bool:
		return bool(self.doc_list(
			doctype,
			filters={"link_doctype": link_doctype, "link_name": link_name},
		))

	def get_summary(self) -> dict:
		total = len(self.results)
		passed = sum(1 for r in self.results if r["status"] == "Pass")
		sections: dict[str, dict] = {}
		for r in self.results:
			s = r["section"]
			if s not in sections:
				sections[s] = {"total": 0, "passed": 0}
			sections[s]["total"] += 1
			if r["status"] == "Pass":
				sections[s]["passed"] += 1

		return {
			"total": total,
			"passed": passed,
			"percentage": round((passed / total) * 100, 1) if total else 0,
			"sections": sections,
			"results": self.results,
		}

	def run(self) -> dict:
		raise NotImplementedError
