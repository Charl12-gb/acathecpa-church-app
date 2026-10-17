import { createRouter, createMemoryHistory, type RouteRecordRaw } from 'vue-router'
import { defineComponent } from 'vue'

const Stub = defineComponent({ template: '<div />' })

/** In-memory router with the student routes the components link to. */
export async function makeRouter(component: any, routes: Array<Omit<RouteRecordRaw, 'component'>>, start: string) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      ...routes.map(r => ({ ...r, component } as RouteRecordRaw)),
      { path: '/course/:id', component: Stub },
      { path: '/:rest(.*)*', component: Stub },
    ],
  })
  router.push(start)
  await router.isReady()
  return router
}
