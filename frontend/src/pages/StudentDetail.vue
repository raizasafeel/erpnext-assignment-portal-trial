<template>
  <AppLayout>
    <div class="p-6 sm:p-8 w-full">
      <div class="mb-8">
        <router-link to="/dashboard" class="text-sm text-ink-gray-5 hover:text-ink-gray-7 mb-2 inline-block">&larr; Back to Dashboard</router-link>
        <h2 class="text-2xl font-bold text-ink-gray-9">{{ studentEmail }}</h2>
        <p class="mt-1 text-base text-ink-gray-5">Student check results</p>
      </div>

      <div v-if="results.loading" class="text-sm text-ink-gray-5">Loading results...</div>

      <div v-else-if="results.data?.length" class="space-y-4">
        <div
          v-for="day in dayOrder"
          :key="day"
          class="bg-surface-white rounded-lg border border-outline-gray-1 overflow-hidden"
        >
          <div class="flex items-center justify-between px-5 py-4">
            <div>
              <h3 class="font-semibold text-ink-gray-9">{{ day }}</h3>
              <p class="text-xs text-ink-gray-5 mt-0.5">
                {{ attemptsByDay[day].length }}
                {{ attemptsByDay[day].length === 1 ? "attempt" : "attempts" }}
              </p>
            </div>
            <div class="text-right">
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold"
                :class="bestByDay[day].percentage === 100 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
              >
                {{ bestByDay[day].percentage === 100 ? "Passed" : "Failed" }}
              </span>
              <div class="text-lg font-bold mt-1" :class="scoreColor(bestByDay[day].percentage)">
                {{ bestByDay[day].passed_checks }}/{{ bestByDay[day].total_checks }}
              </div>
              <div class="text-xs text-ink-gray-5">Best: {{ bestByDay[day].percentage }}%</div>
            </div>
          </div>

          <div class="px-5 pb-4">
            <div class="w-full bg-gray-100 rounded-full h-2">
              <div
                class="h-2 rounded-full transition-all"
                :class="barColor(bestByDay[day].percentage)"
                :style="{ width: `${bestByDay[day].percentage}%` }"
              />
            </div>
          </div>

          <div class="border-t border-outline-gray-1">
            <button
              class="w-full flex items-center justify-between px-5 py-2.5 text-sm text-ink-gray-5 hover:bg-surface-gray-2"
              @click="toggleDay(day)"
            >
              <span>{{ openDays[day] ? "Hide" : "Show" }} attempts</span>
              <ChevronDown
                class="w-4 h-4 transition-transform"
                :class="{ 'rotate-180': openDays[day] }"
              />
            </button>

            <div v-if="openDays[day]" class="border-t border-outline-gray-1">
              <div
                v-for="(attempt, idx) in attemptsByDay[day]"
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
                      Attempt #{{ attemptsByDay[day].length - idx }}
                    </span>
                    <span class="text-ink-gray-5">
                      {{ attempt.passed_checks }}/{{ attempt.total_checks }}
                      ({{ attempt.percentage }}%)
                    </span>
                    <span
                      v-if="attempt.name === bestByDay[day].name"
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

                <div v-if="openAttempts[attempt.name]" class="border-t border-outline-gray-1">
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
                        <span class="font-medium text-ink-gray-7">{{ section.name }}</span>
                      </div>
                      <span class="text-ink-gray-5">{{ section.passed }}/{{ section.total }}</span>
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

const attemptsByDay = computed(() => {
  const map = {}
  if (results.data) {
    for (const r of results.data) {
      if (!map[r.day]) map[r.day] = []
      map[r.day].push(r)
    }
  }
  return map
})

const dayOrder = computed(() => Object.keys(attemptsByDay.value).sort())

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

const openDays = reactive({})
const openAttempts = reactive({})

function toggleDay(day) {
  openDays[day] = !openDays[day]
}

function toggleAttempt(name) {
  openAttempts[name] = !openAttempts[name]
}

function parsedSections(r) {
  if (!r?.result_json) return []
  try {
    const data = JSON.parse(r.result_json)
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
