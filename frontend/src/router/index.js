import { createRouter, createWebHistory } from 'vue-router'

import GlossaryView from '../views/GlossaryView.vue'
import RuleIndexView from '../views/RuleIndexView.vue'
import RuleListView from '../views/RuleListView.vue'
import WorkBuddyView from '../views/WorkBuddyView.vue'


const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'rules-home', component: RuleIndexView },
    { path: '/rules', name: 'rules-list', component: RuleListView },
    { path: '/glossary', name: 'glossary', component: GlossaryView },
    { path: '/workbuddy', name: 'workbuddy', component: WorkBuddyView }
  ]
})

export default router
