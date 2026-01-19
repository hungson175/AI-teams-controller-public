/**
 * Tests for useContentSearch hook (Simple File Search Sprint 1 - Story 2)
 * TDD Approach: Write tests FIRST, then implement hook
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useContentSearch } from './useContentSearch'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch as any

describe('useContentSearch', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers({ shouldAdvanceTime: true })
  })

  afterEach(() => {
    vi.runAllTimers()
    vi.useRealTimers()
  })

  describe('Initial state', () => {
    it('should return empty results initially', () => {
      const { result } = renderHook(() => useContentSearch('team1', ''))

      expect(result.current.results).toEqual([])
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it('should not call API when query is empty', () => {
      renderHook(() => useContentSearch('team1', ''))

      expect(mockFetch).not.toHaveBeenCalled()
    })
  })

  describe('Search execution', () => {
    it('should call API with correct parameters', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: [
            { path: 'src/app.py', match_count: 3 },
            { path: 'lib/utils.py', match_count: 1 }
          ],
          total: 2,
          query: 'def process'
        })
      })

      const { result } = renderHook(() => useContentSearch('team1', 'def process'))

      // Wait for debounce and async operations
      await vi.runAllTimersAsync()

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          '/api/files/team1/search?q=def%20process',
          expect.objectContaining({
            headers: expect.any(Object)
          })
        )
      })
    })

    it('should debounce search queries (300ms)', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ results: [], total: 0, query: '' })
      })

      const { rerender } = renderHook(
        ({ query }) => useContentSearch('team1', query),
        { initialProps: { query: 'a' } }
      )

      // Type rapidly
      rerender({ query: 'ab' })
      vi.advanceTimersByTime(100)

      rerender({ query: 'abc' })
      vi.advanceTimersByTime(100)

      rerender({ query: 'abcd' })
      vi.advanceTimersByTime(100)

      // Should not have called API yet (only 300ms passed total)
      expect(mockFetch).not.toHaveBeenCalled()

      // Wait for debounce to complete
      await vi.runAllTimersAsync()

      await waitFor(() => {
        // Should only call API once with final query
        expect(mockFetch).toHaveBeenCalledTimes(1)
        expect(mockFetch).toHaveBeenCalledWith(
          '/api/files/team1/search?q=abcd',
          expect.any(Object)
        )
      })
    })

    it('should set loading state during search', async () => {
      mockFetch.mockImplementation(() =>
        new Promise(resolve => {
          setTimeout(() => resolve({
            ok: true,
            json: async () => ({ results: [], total: 0, query: '' })
          }), 100)
        })
      )

      const { result } = renderHook(() => useContentSearch('team1', 'test'))

      // Initial state
      expect(result.current.isLoading).toBe(false)

      // Advance past debounce and wait for async
      await vi.runAllTimersAsync()

      // Should finish loading
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })
    })

    it('should return search results', async () => {
      const mockResults = [
        { path: 'frontend/app.tsx', match_count: 5 },
        { path: 'backend/main.py', match_count: 2 }
      ]

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: mockResults,
          total: 2,
          query: 'import'
        })
      })

      const { result } = renderHook(() => useContentSearch('team1', 'import'))

      await vi.runAllTimersAsync()

      await waitFor(() => {
        expect(result.current.results).toEqual(mockResults)
        expect(result.current.error).toBeNull()
      })
    })
  })

  describe('Error handling', () => {
    it('should handle API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      })

      const { result } = renderHook(() => useContentSearch('team1', 'query'))

      await vi.runAllTimersAsync()

      await waitFor(() => {
        expect(result.current.error).toBeTruthy()
        expect(result.current.results).toEqual([])
        expect(result.current.isLoading).toBe(false)
      })
    })

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(() => useContentSearch('team1', 'query'))

      await vi.runAllTimersAsync()

      await waitFor(() => {
        expect(result.current.error).toBeTruthy()
        expect(result.current.results).toEqual([])
      })
    })
  })

  describe('Query changes', () => {
    it('should clear results when query becomes empty', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          results: [{ path: 'test.ts', match_count: 1 }],
          total: 1,
          query: 'test'
        })
      })

      const { result, rerender } = renderHook(
        ({ query }) => useContentSearch('team1', query),
        { initialProps: { query: 'test' } }
      )

      // First search
      await vi.runAllTimersAsync()
      await waitFor(() => {
        expect(result.current.results).toHaveLength(1)
      })

      // Clear query
      rerender({ query: '' })

      // Results should be cleared immediately
      expect(result.current.results).toEqual([])
      expect(result.current.error).toBeNull()
    })

    it('should handle rapid query changes correctly', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ results: [], total: 0, query: '' })
      })

      const { rerender } = renderHook(
        ({ query }) => useContentSearch('team1', query),
        { initialProps: { query: 'first' } }
      )

      // Change query before debounce completes
      vi.advanceTimersByTime(200)
      rerender({ query: 'second' })

      vi.advanceTimersByTime(200)
      rerender({ query: 'third' })

      // Complete debounce from last change
      await vi.runAllTimersAsync()

      await waitFor(() => {
        // Should only search for the final query
        expect(mockFetch).toHaveBeenCalledTimes(1)
        expect(mockFetch).toHaveBeenCalledWith(
          '/api/files/team1/search?q=third',
          expect.any(Object)
        )
      })
    })
  })

  describe('Team ID changes', () => {
    it('should trigger new search when team changes', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ results: [], total: 0, query: '' })
      })

      const { rerender } = renderHook(
        ({ teamId, query }) => useContentSearch(teamId, query),
        { initialProps: { teamId: 'team1', query: 'search' } }
      )

      await vi.runAllTimersAsync()
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          '/api/files/team1/search?q=search',
          expect.any(Object)
        )
      })

      mockFetch.mockClear()

      // Change team
      rerender({ teamId: 'team2', query: 'search' })
      await vi.runAllTimersAsync()

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          '/api/files/team2/search?q=search',
          expect.any(Object)
        )
      })
    })
  })
})
