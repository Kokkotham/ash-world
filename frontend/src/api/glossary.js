import api from './index'


export function listGlossaryTerms(params = {}) {
  return api.get('/glossary/', { params })
}
