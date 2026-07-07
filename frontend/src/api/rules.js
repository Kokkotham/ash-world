import api from './index'


export function listRuleCategories(params = {}) {
  return api.get('/rule-categories/', { params })
}

export function listRules(params = {}) {
  return api.get('/rules/', { params })
}
