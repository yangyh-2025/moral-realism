/**
 * CINC数据查询API
 * 提供CINC（Composite Index of National Capability）数据库的查询接口
 */
import request from './index'

export function getCincCountries() {
  return request({ url: '/cinc/countries', method: 'get' })
}

export function getCincYears() {
  return request({ url: '/cinc/years', method: 'get' })
}

export function getCincData(countryCode, year) {
  return request({
    url: '/cinc/data',
    method: 'get',
    params: { country_code: countryCode, year }
  })
}

export function getCincByYear(year) {
  return request({ url: `/cinc/by-year/${year}`, method: 'get' })
}
