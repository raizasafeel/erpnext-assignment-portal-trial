<template>
	<div class="p-2">
		<Dropdown :options="userDropdownOptions">
			<template v-slot="{ open }">
				<button
					class="flex h-12 py-2 items-center rounded-md duration-300 ease-in-out"
					:class="
						isCollapsed
							? 'px-0 w-auto'
							: open
								? 'bg-surface-white shadow-sm px-2 w-52'
								: 'hover:bg-surface-gray-3 px-2 w-52'
					"
				>
					<img
						v-if="branding.data?.banner_image"
						:src="branding.data.banner_image.file_url"
						class="w-8 h-8 rounded flex-shrink-0"
					/>
					<PortalLogo v-else class="w-8 h-8 rounded flex-shrink-0" />
					<div
						class="flex flex-1 flex-col text-left duration-300 ease-in-out"
						:class="
							isCollapsed
								? 'opacity-0 ml-0 w-0 overflow-hidden'
								: 'opacity-100 ml-2 w-auto'
						"
					>
						<div
							class="text-base font-medium text-ink-gray-9 leading-none"
						>
							<span
								v-if="
									branding.data?.app_name &&
									branding.data.app_name !== 'Frappe'
								"
							>
								{{ branding.data.app_name }}
							</span>
							<span v-else>Assignment Portal</span>
						</div>
						<div
							v-if="user"
							class="mt-1 text-sm text-ink-gray-7 leading-none"
						>
							{{ user.full_name }}
						</div>
					</div>
					<div
						class="duration-300 ease-in-out"
						:class="
							isCollapsed
								? 'opacity-0 ml-0 w-0 overflow-hidden'
								: 'opacity-100 ml-2 w-auto'
						"
					>
						<ChevronDown class="h-4 w-4 text-ink-gray-7" />
					</div>
				</button>
			</template>
		</Dropdown>
	</div>
</template>

<script setup>
import { Dropdown } from "frappe-ui"
import { computed, markRaw } from "vue"
import { sessionStore } from "@/stores/session"
import { usersStore } from "@/stores/user"
import Apps from "./Apps.vue"
import { ChevronDown, LogOut, Sun, Moon } from "lucide-vue-next"
import PortalLogo from "@/components/Icons/PortalLogo.vue"

defineProps({
	isCollapsed: {
		type: Boolean,
		default: false,
	},
})

const { userResource } = usersStore()
const session = sessionStore()
const { branding } = session
const user = computed(() => userResource.data)

const isSystemUser = computed(() => {
	const cookies = new URLSearchParams(
		document.cookie.split("; ").join("&"),
	)
	return cookies.get("system_user") === "yes"
})

function isDark() {
	return document.documentElement.getAttribute("data-theme") === "dark"
}

function toggleTheme() {
	const next = isDark() ? "light" : "dark"
	document.documentElement.setAttribute("data-theme", next)
	localStorage.setItem("ap_theme", next)
}

const userDropdownOptions = computed(() => {
	const items = []

	if (isSystemUser.value) {
		items.push({
			component: markRaw(Apps),
		})
	}

	items.push({
		icon: isDark() ? Sun : Moon,
		label: isDark() ? "Light mode" : "Dark mode",
		onClick: toggleTheme,
	})

	items.push({
		icon: LogOut,
		label: "Log out",
		onClick: () => {
			session.logout.submit()
		},
	})

	return [{ group: "", items }]
})
</script>
