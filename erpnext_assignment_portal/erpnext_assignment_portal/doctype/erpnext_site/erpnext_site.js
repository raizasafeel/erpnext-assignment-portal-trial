frappe.ui.form.on("ERPNext Site", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Test Connection"), function () {
				frappe.call({
					method: "test_connection",
					doc: frm.doc,
					freeze: true,
					freeze_message: __("Testing connection..."),
					callback(r) {
						if (r.message && r.message.status === "Connected") {
							frappe.show_alert({
								message: __("Connected successfully as {0}", [r.message.user]),
								indicator: "green",
							});
						} else {
							frappe.show_alert({
								message: __("Connection failed: {0}", [r.message?.error || "Unknown error"]),
								indicator: "red",
							});
						}
						frm.reload_doc();
					},
				});
			});
		}
	},
});
