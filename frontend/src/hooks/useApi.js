import { useState, useEffect, useCallback, useRef } from 'react'

export function useApi(apiFn, deps = []) {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)
  const mountedRef = useRef(true)

  useEffect(() => { mountedRef.current = true; return () => { mountedRef.current = false } }, [])

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiFn()
      if (mountedRef.current) setData(result)
    } catch (err) {
      if (mountedRef.current)
        setError(err.response?.data?.detail || err.response?.data?.error || err.message || 'Request failed')
    } finally {
      if (mountedRef.current) setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => { fetch() }, [fetch])

  return { data, loading, error, refetch: fetch }
}
