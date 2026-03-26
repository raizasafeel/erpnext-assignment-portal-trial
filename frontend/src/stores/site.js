import { defineStore } from "pinia"
import { createListResource } from "frappe-ui"
import { computed } from "vue"

export const useSiteStore = defineStore("assignment-portal-site", () => {
	const sites = createListResource({
		doctype: "ERPNext Site",
		fields: ["name", "site_url", "site_username", "connection_status"],
		cache: "StudentSite",
		auto: true,
	})

	const site = computed(() => sites.data?.[0] || null)
	const hasSite = computed(() => !!site.value)
	const siteName = computed(() => site.value?.name || "")

	function reload() {
		sites.reload()
	}

	return {
		sites,
		site,
		hasSite,
		siteName,
		reload,
	}
})
