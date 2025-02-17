<template>
  <div class="entries-list">
    <template v-for="(group, index) in weekGroups" :key="index">
      <div class="week-separator">
        <span>{{ formatWeekRange(group.weekStart) }}</span>
      </div>
      <EntryCard
        v-for="entry in group.entries"
        :key="entry.id"
        :entry="entry"
      />
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import EntryCard from './EntryCard.vue'

const props = defineProps({
  entries: {
    type: Array,
    required: true,
  },
})

const weekGroups = computed(() => {
  const groups = []
  let currentWeekStart = null
  let currentGroup = null

  // Sort entries by date (newest first)
  const sortedEntries = [...props.entries].sort(
    (a, b) => new Date(b.date) - new Date(a.date)
  )

  sortedEntries.forEach((entry) => {
    const entryDate = new Date(entry.date)
    const weekStart = getWeekStart(entryDate)

    if (
      !currentWeekStart ||
      weekStart.getTime() !== currentWeekStart.getTime()
    ) {
      currentWeekStart = weekStart
      currentGroup = {
        weekStart: currentWeekStart,
        entries: [],
      }
      groups.push(currentGroup)
    }

    currentGroup.entries.push(entry)
  })

  return groups
})

function getWeekStart(date) {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  const day = d.getDay()
  d.setDate(d.getDate() - (day === 0 ? 6 : day - 1)) // Set to Monday
  return d
}

function formatWeekRange(weekStart) {
  const weekEnd = new Date(weekStart)
  weekEnd.setDate(weekEnd.getDate() + 6)

  const options = { day: '2-digit', month: '2-digit', year: 'numeric' }
  return `${weekStart.toLocaleDateString(
    'de-DE',
    options
  )} - ${weekEnd.toLocaleDateString('de-DE', options)}`
}
</script>

<style scoped>
.entries-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.week-separator {
  margin: 30px 0 20px;
  text-align: center;
  position: relative;
}

.week-separator::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 100%;
  height: 1px;
  background: var(--border-color);
  z-index: 1;
}

.week-separator span {
  background: var(--background-color);
  padding: 0 20px;
  color: var(--text-color);
  opacity: 0.7;
  position: relative;
  z-index: 2;
  font-size: 0.9rem;
  font-weight: 500;
}
</style>
