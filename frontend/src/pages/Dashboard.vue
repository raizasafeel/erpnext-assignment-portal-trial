<template>
	<AppLayout>
		<div class="p-6 sm:p-8 w-full">
			<template v-if="!portalStatus.data?.course_configured">
				<div class="flex flex-1 items-center justify-center py-20">
					<div class="text-center max-w-md">
						<h2 class="text-2xl font-bold text-ink-gray-9 mb-2">
							Coming Soon
						</h2>
						<p class="text-ink-gray-5">
							The assignment portal is being set up. Please
							check back later.
						</p>
					</div>
				</div>
			</template>

			<template v-else-if="!portalStatus.data?.enrolled">
				<div class="flex flex-1 items-center justify-center py-20">
					<div class="text-center max-w-md">
						<h2 class="text-2xl font-bold text-ink-gray-9 mb-2">
							Not Enrolled
						</h2>
						<p class="text-ink-gray-5">
							You are not enrolled in the course linked to this
							portal. Please contact your instructor to get
							enrolled.
						</p>
					</div>
				</div>
			</template>

			<template v-else>
			<h2 class="text-2xl font-bold text-ink-gray-9">Dashboard</h2>
			<p class="mt-1 text-base text-ink-gray-5 mb-8">
				Your ERPNext assignment progress.
			</p>

			<div v-if="siteStore.hasSite" class="mb-8">
				<div class="flex items-center justify-between p-4 bg-surface-white rounded-lg border border-outline-gray-2">
					<div class="flex items-center gap-3">
						<div
							class="w-2.5 h-2.5 rounded-full"
							:class="siteStore.site.connection_status === 'Connected' ? 'bg-green-500' : 'bg-gray-300'"
						/>
						<div>
							<div class="font-medium text-ink-gray-9">
								{{ siteStore.site.site_url }}
							</div>
							<div class="text-sm text-ink-gray-5 mt-0.5">
								{{ siteStore.site.site_username }}
							</div>
						</div>
					</div>
					<Badge
						:theme="siteStore.site.connection_status === 'Connected' ? 'green' : 'gray'"
					>
						{{ siteStore.site.connection_status || "Unknown" }}
					</Badge>
				</div>
			</div>
			<div v-else class="mb-8">
				<div class="p-6 bg-surface-white rounded-lg border border-dashed border-outline-gray-2 text-center">
					<p class="text-ink-gray-5 mb-3">
						No ERPNext site connected yet.
					</p>
					<router-link to="/setup">
						<Button variant="solid">Connect Your Site</Button>
					</router-link>
				</div>
			</div>

			<h3 class="text-lg font-semibold text-ink-gray-9 mb-4">
				Assignments
			</h3>
			<div class="space-y-4">
				<div
					v-for="day in days"
					:key="day.num"
					class="bg-surface-white rounded-lg border border-outline-gray-2 overflow-hidden"
				>
					<router-link
						:to="`/day/${day.num}`"
						class="block p-5 hover:bg-surface-gray-2 transition-colors"
					>
						<div class="flex items-center justify-between">
							<div>
								<div class="text-sm font-medium text-ink-gray-5 mb-1">
									Day {{ day.num }}
								</div>
								<div class="font-semibold text-ink-gray-9 mb-1">
									{{ day.title }}
								</div>
								<div class="text-sm text-ink-gray-5">
									{{ day.desc }}
								</div>
							</div>
							<div
								v-if="bestByDay[`Day ${day.num}`]"
								class="text-right ml-4 shrink-0"
							>
								<span
									class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold"
									:class="
										bestByDay[`Day ${day.num}`].percentage === 100
											? 'bg-green-100 text-green-800'
											: 'bg-red-100 text-red-800'
									"
								>
									{{ bestByDay[`Day ${day.num}`].percentage === 100 ? "Passed" : "Failed" }}
								</span>
								<div
									class="text-lg font-bold mt-1"
									:class="scoreColor(bestByDay[`Day ${day.num}`].percentage)"
								>
									{{ bestByDay[`Day ${day.num}`].passed_checks }}/{{ bestByDay[`Day ${day.num}`].total_checks }}
								</div>
								<div class="text-xs text-ink-gray-5">
									{{ bestByDay[`Day ${day.num}`].percentage }}%
								</div>
								<div class="text-xs text-ink-gray-4">
									{{ attemptsByDay[`Day ${day.num}`].length }}
									{{ attemptsByDay[`Day ${day.num}`].length === 1 ? "attempt" : "attempts" }}
								</div>
							</div>
							<div v-else class="text-right ml-4 shrink-0">
								<span class="text-sm text-ink-gray-4 italic">
									Not attempted
								</span>
							</div>
						</div>
						<div
							v-if="bestByDay[`Day ${day.num}`]"
							class="mt-3"
						>
							<div class="w-full bg-gray-100 rounded-full h-1.5">
								<div
									class="h-1.5 rounded-full transition-all duration-500"
									:class="barColor(bestByDay[`Day ${day.num}`].percentage)"
									:style="{ width: `${bestByDay[`Day ${day.num}`].percentage}%` }"
								/>
							</div>
						</div>
					</router-link>

					<div
						v-if="attemptsByDay[`Day ${day.num}`]?.length"
						class="border-t border-outline-gray-1"
					>
						<button
							class="w-full flex items-center justify-between px-5 py-2.5 text-sm text-ink-gray-5 hover:bg-surface-gray-2"
							@click="toggleDay(`Day ${day.num}`)"
						>
							<span>
								{{ openDays[`Day ${day.num}`] ? "Hide" : "Show" }}
								attempts
							</span>
							<ChevronDown
								class="w-4 h-4 transition-transform"
								:class="{ 'rotate-180': openDays[`Day ${day.num}`] }"
							/>
						</button>

						<div
							v-if="openDays[`Day ${day.num}`]"
							class="border-t border-outline-gray-1"
						>
							<div
								v-for="(attempt, idx) in attemptsByDay[`Day ${day.num}`]"
								:key="attempt.name"
								class="border-b border-outline-gray-1 last:border-b-0"
							>
								<button
									class="w-full flex items-center justify-between px-5 py-3 text-sm hover:bg-surface-gray-2"
									@click="toggleAttempt(attempt.name)"
								>
									<div class="flex items-center gap-3">
										<CheckCircle2
											v-if="attempt.percentage === 100"
											class="w-4 h-4 text-green-500"
										/>
										<XCircle v-else class="w-4 h-4 text-red-500" />
										<span class="font-medium text-ink-gray-7">
											Attempt #{{ attemptsByDay[`Day ${day.num}`].length - idx }}
										</span>
										<span class="text-ink-gray-5">
											{{ attempt.passed_checks }}/{{ attempt.total_checks }}
											({{ attempt.percentage }}%)
										</span>
										<span
											v-if="attempt.name === bestByDay[`Day ${day.num}`]?.name"
											class="text-xs bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded"
										>
											Best
										</span>
									</div>
									<div class="flex items-center gap-3">
										<span class="text-xs text-ink-gray-4">
											{{ formatDate(attempt.checked_at) }}
										</span>
										<ChevronDown
											class="w-3.5 h-3.5 text-ink-gray-4 transition-transform"
											:class="{ 'rotate-180': openAttempts[attempt.name] }"
										/>
									</div>
								</button>

								<div
									v-if="openAttempts[attempt.name]"
									class="border-t border-outline-gray-1"
								>
									<div
										v-for="section in parsedSections(attempt)"
										:key="section.name"
										class="border-b border-outline-gray-1 last:border-b-0"
									>
										<div class="flex items-center justify-between px-5 py-2.5 bg-surface-gray-2 text-sm">
											<div class="flex items-center gap-2">
												<CheckCircle2
													v-if="section.passed === section.total"
													class="w-4 h-4 text-green-500"
												/>
												<XCircle v-else class="w-4 h-4 text-red-500" />
												<span class="font-medium text-ink-gray-7">
													{{ section.name }}
												</span>
											</div>
											<span class="text-ink-gray-5">
												{{ section.passed }}/{{ section.total }}
											</span>
										</div>
										<table class="w-full text-sm">
											<tbody>
												<tr
													v-for="(check, cidx) in section.checks"
													:key="cidx"
													:class="check.status === 'Fail' ? 'bg-red-50' : ''"
													class="border-t border-outline-gray-1"
												>
													<td class="px-5 py-2 w-6 text-center">
														<CheckCircle2
															v-if="check.status === 'Pass'"
															class="w-4 h-4 text-green-500"
														/>
														<XCircle v-else class="w-4 h-4 text-red-500" />
													</td>
													<td class="py-2 text-ink-gray-9">
														{{ check.check }}
													</td>
													<td class="px-5 py-2 text-right text-ink-gray-5 text-xs">
														<template v-if="check.status === 'Fail'">
															Expected: {{ check.expected || "—" }}
															| Got: {{ check.actual || "—" }}
														</template>
													</td>
												</tr>
											</tbody>
										</table>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
			</template>
		</div>
	</AppLayout>
</template>

<script setup>
import { computed, reactive } from "vue"
import { createResource } from "frappe-ui"
import { usersStore } from "@/stores/user"
import { useSiteStore } from "@/stores/site"
import { CheckCircle2, XCircle, ChevronDown } from "lucide-vue-next"
import AppLayout from "@/components/AppLayout.vue"

const { portalStatus } = usersStore()
const siteStore = useSiteStore()

const myResults = createResource({
	url: "erpnext_assignment_portal.api.get_my_results",
	cache: "MyResults",
	auto: true,
})

const attemptsByDay = computed(() => {
	const map = {}
	if (myResults.data) {
		for (const r of myResults.data) {
			if (!map[r.day]) map[r.day] = []
			map[r.day].push(r)
		}
	}
	return map
})

const bestByDay = computed(() => {
	const map = {}
	for (const [day, attempts] of Object.entries(attemptsByDay.value)) {
		let best = attempts[0]
		for (const a of attempts) {
			if (a.percentage > best.percentage) best = a
		}
		map[day] = best
	}
	return map
})

const days = [
	{
		num: 1,
		title: "Master Data Setup",
		desc: "Company, Customers, Suppliers, Items, Warehouses, Users, Chart of Accounts",
	},
	{
		num: 2,
		title: "Sales & Purchase",
		desc: "Sales Order, Delivery Note, Payment Entry, Purchase Order, Purchase Receipt, Stock Transfer",
	},
	{
		num: 3,
		title: "Accounting & Manufacturing",
		desc: "Budget, Accounting Dimensions, Journal Entries, BOM",
	},
]

const openDays = reactive({})
const openAttempts = reactive({})

function toggleDay(day) {
	openDays[day] = !openDays[day]
}

function toggleAttempt(name) {
	openAttempts[name] = !openAttempts[name]
}

function parsedSections(result) {
	if (!result?.result_json) return []
	try {
		const data = JSON.parse(result.result_json)
		if (!data?.results) return []
		const map = {}
		const order = []
		for (const c of data.results) {
			if (!map[c.section]) {
				map[c.section] = {
					name: c.section,
					checks: [],
					passed: 0,
					total: 0,
				}
				order.push(c.section)
			}
			map[c.section].checks.push(c)
			map[c.section].total++
			if (c.status === "Pass") map[c.section].passed++
		}
		return order.map((s) => map[s])
	} catch {
		return []
	}
}

function scoreColor(pct) {
	if (pct >= 80) return "text-green-600"
	if (pct >= 50) return "text-yellow-600"
	return "text-red-600"
}

function barColor(pct) {
	if (pct >= 80) return "bg-green-500"
	if (pct >= 50) return "bg-yellow-500"
	return "bg-red-500"
}

function formatDate(dt) {
	if (!dt) return ""
	return new Date(dt).toLocaleString()
}
</script>
