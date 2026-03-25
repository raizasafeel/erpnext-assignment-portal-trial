<template>
  <AppLayout>
    <div class="p-8 max-w-4xl">
      <div class="mb-6">
        <router-link to="/dashboard" class="text-sm text-ink-gray-5 hover:text-ink-gray-7 mb-2 inline-block">&larr; Back to Dashboard</router-link>
        <h2 class="text-2xl font-bold text-ink-gray-9">{{ studentEmail }}</h2>
        <p class="text-ink-gray-5">Student check results</p>
      </div>

      <div v-if="results.loading" class="text-sm text-ink-gray-5">Loading results...</div>

      <div v-else-if="results.data?.length" class="space-y-4">
        <div
          v-for="r in results.data"
          :key="r.name"
          class="bg-surface-white rounded-lg border overflow-hidden"
        >
          <div class="flex items-center justify-between px-5 py-4">
            <div>
              <h3 class="font-semibold text-ink-gray-9">{{ r.day }}</h3>
              <p class="text-xs text-ink-gray-5 mt-0.5">Checked {{ formatDate(r.checked_at) }}</p>
            </div>
            <span
              class="text-lg font-bold"
              :class="scoreColor(r.percentage)"
            >
              {{ r.passed_checks }}/{{ r.total_checks }} ({{ r.percentage }}%)
            </span>
          </div>

          <div class="px-5 pb-4">
            <div class="w-full bg-gray-100 rounded-full h-2">
              <div
                class="h-2 rounded-full transition-all"
                :class="barColor(r.percentage)"
                :style="{ width: `${r.percentage}%` }"
              />
            </div>
          </div>

          <div class="border-t">
            <button
              class="w-full flex items-center justify-between px-5 py-3 text-sm text-ink-gray-5 hover:bg-surface-gray-2"
              @click="toggleDay(r.day)"
            >
              <span>{{ openDays[r.day] ? "Hide" : "Show" }} details</span>
              <ChevronDown class="w-4 h-4 transition-transform" :class="{ 'rotate-180': openDays[r.day] }" />
            </button>

            <div v-if="openDays[r.day] && parsedResults(r)" class="border-t">
              <div
                v-for="section in parsedSections(r)"
                :key="section.name"
                class="border-b last:border-b-0"
              >
                <div class="flex items-center justify-between px-5 py-2.5 bg-surface-gray-2 text-sm">
                  <span class="font-medium text-ink-gray-7">{{ section.name }}</span>
                  <span class="text-ink-gray-5">{{ section.passed }}/{{ section.total }}</span>
                </div>
                <table class="w-full text-sm">
                  <tbody>
                    <tr
                      v-for="(check, idx) in section.checks"
                      :key="idx"
                      :class="check.status === 'Fail' ? 'bg-red-50' : ''"
                      class="border-t"
                    >
                      <td class="px-5 py-2 w-6 text-center">
                        <CheckCircle2 v-if="check.status === 'Pass'" class="w-4 h-4 text-green-500" />
                        <XCircle v-else class="w-4 h-4 text-red-500" />
                      </td>
                      <td class="py-2 text-ink-gray-9">{{ check.check }}</td>
                      <td class="px-5 py-2 text-right text-ink-gray-5 text-xs">
                        <template v-if="check.status === 'Fail'">
                          Expected: {{ check.expected || "—" }} | Got: {{ check.actual || "—" }}
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

      <div v-else class="p-6 bg-surface-white rounded-lg border border-dashed border-outline-gray-2 text-center">
        <p class="text-ink-gray-5">No results found for this student.</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, reactive } from "vue"
import { useRoute } from "vue-router"
import { createResource } from "frappe-ui"
import { CheckCircle2, XCircle, ChevronDown } from "lucide-vue-next"
import AppLayout from "@/components/AppLayout.vue"

const route = useRoute()
const studentEmail = computed(() => route.params.student)

const results = createResource({
  url: "erpnext_assignment_portal.api.get_student_results",
  params: { student: studentEmail.value },
  auto: true,
})

const openDays = reactive({})

function toggleDay(day) {
  openDays[day] = !openDays[day]
}

function parsedResults(r) {
  try {
    return JSON.parse(r.result_json)
  } catch {
    return null
  }
}

function parsedSections(r) {
  const data = parsedResults(r)
  if (!data?.results) return []
  const map = {}
  const order = []
  for (const c of data.results) {
    if (!map[c.section]) {
      map[c.section] = { name: c.section, checks: [], passed: 0, total: 0 }
      order.push(c.section)
    }
    map[c.section].checks.push(c)
    map[c.section].total++
    if (c.status === "Pass") map[c.section].passed++
  }
  return order.map((s) => map[s])
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
