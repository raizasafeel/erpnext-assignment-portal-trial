<template>
	<AppLayout>
		<div class="p-8 max-w-5xl">
			<h2 class="text-2xl font-bold text-ink-gray-9 mb-1">
				Dashboard
			</h2>
			<p class="text-ink-gray-5 mb-8">
				Overview of student submissions.
			</p>

			<div v-if="dashboard.loading" class="text-sm text-ink-gray-5">
				Loading...
			</div>

			<template v-else-if="dashboard.data">
				<!-- Stats -->
				<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
					<div class="p-5 bg-surface-white rounded-lg border">
						<div class="text-sm text-ink-gray-5 mb-1">
							Total Students
						</div>
						<div class="text-2xl font-bold text-ink-gray-9">
							{{ dashboard.data.total_students }}
						</div>
					</div>
					<div class="p-5 bg-surface-white rounded-lg border">
						<div class="text-sm text-ink-gray-5 mb-1">
							With Submissions
						</div>
						<div class="text-2xl font-bold text-ink-gray-9">
							{{ dashboard.data.with_submissions }}
							<span
								class="text-sm font-normal text-ink-gray-4"
							>
								/ {{ dashboard.data.total_students }}
							</span>
						</div>
					</div>
					<div class="p-5 bg-surface-white rounded-lg border">
						<div class="text-sm text-ink-gray-5 mb-1">
							Overall Avg. Score
						</div>
						<div
							class="text-2xl font-bold"
							:class="
								scoreColor(
									dashboard.data.overall_average,
								)
							"
						>
							{{ dashboard.data.overall_average }}%
						</div>
					</div>
				</div>

				<!-- Search -->
				<div class="mb-4">
					<input
						v-model="searchQuery"
						type="text"
						placeholder="Search by name or email..."
						class="w-full max-w-md border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
					/>
				</div>

				<!-- Submissions table -->
				<div
					v-if="filteredSubmissions.length"
					class="bg-surface-white rounded-lg border overflow-hidden"
				>
					<table class="w-full text-sm">
						<thead>
							<tr
								class="bg-surface-gray-2 text-ink-gray-5 border-b"
							>
								<th class="px-4 py-3 text-left">
									Student
								</th>
								<th class="px-4 py-3 text-center">
									Avg. Score
								</th>
								<th class="px-4 py-3 text-center">
									Days Completed
								</th>
								<th class="px-4 py-3 text-center">
									Last Activity
								</th>
								<th class="px-4 py-3 text-right">
									Actions
								</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="s in filteredSubmissions"
								:key="s.student"
								class="border-t hover:bg-surface-gray-2 cursor-pointer"
								@click="goToStudent(s.student)"
							>
								<td class="px-4 py-3">
									<div
										class="flex items-center gap-2.5"
									>
										<div
											class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-medium text-ink-gray-5"
										>
											{{
												initials(
													s.full_name ||
														s.student,
												)
											}}
										</div>
										<div>
											<div
												class="font-medium text-ink-gray-9"
											>
												{{
													s.full_name ||
													s.student
												}}
											</div>
											<div
												class="text-xs text-ink-gray-5"
											>
												{{ s.student }}
											</div>
										</div>
									</div>
								</td>
								<td class="px-4 py-3 text-center">
									<span
										v-if="s.submissions > 0"
										class="font-semibold"
										:class="
											scoreColor(
												s.average_percentage,
											)
										"
									>
										{{ s.average_percentage }}%
									</span>
									<span
										v-else
										class="text-ink-gray-4"
										>--</span
									>
								</td>
								<td class="px-4 py-3 text-center">
									<div
										class="flex items-center justify-center gap-1"
									>
										<span
											v-for="day in [
												'Day 1',
												'Day 2',
												'Day 3',
											]"
											:key="day"
											class="w-6 h-6 rounded text-xs font-medium flex items-center justify-center"
											:class="
												s.days_completed.includes(
													day,
												)
													? 'bg-green-100 text-green-700'
													: 'bg-gray-100 text-ink-gray-4'
											"
											:title="day"
										>
											{{ day.split(" ")[1] }}
										</span>
									</div>
								</td>
								<td
									class="px-4 py-3 text-center text-xs text-ink-gray-5"
								>
									{{
										s.last_checked
											? formatDate(s.last_checked)
											: "--"
									}}
								</td>
								<td class="px-4 py-3 text-right">
									<Button
										size="sm"
										variant="ghost"
										@click.stop="
											goToStudent(s.student)
										"
									>
										View
									</Button>
								</td>
							</tr>
						</tbody>
					</table>
				</div>
				<div
					v-else
					class="p-6 bg-surface-white rounded-lg border border-dashed border-outline-gray-2 text-center"
				>
					<p class="text-ink-gray-5">No submissions found.</p>
				</div>
			</template>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed } from "vue"
import { useRouter } from "vue-router"
import { createResource } from "frappe-ui"
import AppLayout from "@/components/AppLayout.vue"

const router = useRouter()
const searchQuery = ref("")

const dashboard = createResource({
	url: "erpnext_assignment_portal.api.get_dashboard",
	auto: true,
})

const filteredSubmissions = computed(() => {
	if (!dashboard.data?.submissions) return []
	if (!searchQuery.value) return dashboard.data.submissions
	const q = searchQuery.value.toLowerCase()
	return dashboard.data.submissions.filter(
		(s) =>
			(s.full_name || "").toLowerCase().includes(q) ||
			s.student.toLowerCase().includes(q),
	)
})

function goToStudent(student) {
	router.push(`/students/${encodeURIComponent(student)}`)
}

function scoreColor(pct) {
	if (pct >= 80) return "text-green-600"
	if (pct >= 50) return "text-yellow-600"
	return "text-red-600"
}

function initials(name) {
	if (!name) return "?"
	return name
		.split(" ")
		.map((w) => w[0])
		.join("")
		.toUpperCase()
		.slice(0, 2)
}

function formatDate(dt) {
	if (!dt) return ""
	return new Date(dt).toLocaleDateString()
}
</script>
