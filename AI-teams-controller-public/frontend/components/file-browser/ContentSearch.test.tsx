/**
 * ContentSearch Component Tests (Story 2: Word Search in File Browser)
 * TDD Approach: Write tests FIRST, then implement component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ContentSearch } from './ContentSearch'

// Mock useContentSearch hook
const mockUseContentSearch = vi.fn()
vi.mock('@/hooks/useContentSearch', () => ({
  useContentSearch: (teamId: string, query: string) => mockUseContentSearch(teamId, query)
}))

describe('ContentSearch', () => {
  const mockOnFileSelect = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    mockUseContentSearch.mockReturnValue({
      results: [],
      isLoading: false,
      error: null
    })
  })

  describe('Search input', () => {
    it('should render search input with placeholder', () => {
      render(<ContentSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search in files/i)
      expect(input).toBeInTheDocument()
    })

    it('should render search icon', () => {
      render(<ContentSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      // Search icon should be visible
      const searchIcon = document.querySelector('.lucide-search')
      expect(searchIcon).toBeInTheDocument()
    })

    it('should update query on typing', () => {
      render(<ContentSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search in files/i)
      fireEvent.change(input, { target: { value: 'test query' } })

      expect(input).toHaveValue('test query')
    })

    it('should show clear button when query is not empty', () => {
      render(<ContentSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search in files/i)

      // Initially no clear button
      expect(screen.queryByRole('button', { name: /clear/i })).not.toBeInTheDocument()

      // Type something
      fireEvent.change(input, { target: { value: 'test' } })

      // Clear button should appear
      expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument()
    })

    it('should clear input when clear button clicked', () => {
      render(<ContentSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search in files/i) as HTMLInputElement
      fireEvent.change(input, { target: { value: 'test' } })

      const clearButton = screen.getByRole('button', { name: /clear/i })
      fireEvent.click(clearButton)

      expect(input.value).toBe('')
    })
  })

  describe('Search results', () => {
    it('should display search results with file paths and match counts', () => {
      mockUseContentSearch.mockReturnValue({
        results: [
          { path: 'src/app.tsx', match_count: 5 },
          { path: 'lib/utils.ts', match_count: 2 }
        ],
        isLoading: false,
        error: null
      })

      render(<ContentSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      // Type to trigger search
      const input = screen.getByPlaceholderText(/search in files/i)
      fireEvent.change(input, { target: { value: 'import' } })

      // Results should be visible
      expect(screen.getByText('src/app.tsx')).toBeInTheDocument()
      expect(screen.getByText(/5 matches/i)).toBeInTheDocument()
      expect(screen.getByText('lib/utils.ts')).toBeInTheDocument()
      expect(screen.getByText(/2 matches/i)).toBeInTheDocument()
    })

    it('should show loading state', () => {
      mockUseContentSearch.mockReturnValue({
        results: [],
        isLoading: true,
        error: null
      })

      render(<ContentSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search in files/i)
      fireEvent.change(input, { target: { value: 'test' } })

      expect(screen.getByText(/searching/i)).toBeInTheDocument()
    })

    it('should show "no results" message when empty', () => {
      mockUseContentSearch.mockReturnValue({
        results: [],
        isLoading: false,
        error: null
      })

      render(<ContentSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search in files/i)
      fireEvent.change(input, { target: { value: 'nonexistent' } })

      // Wait for debounce and check for message
      // Hook returns empty results, component should show "No results"
      expect(screen.getByText(/no results/i)).toBeInTheDocument()
    })

    it('should show error message on search failure', () => {
      mockUseContentSearch.mockReturnValue({
        results: [],
        isLoading: false,
        error: 'Search failed: 500'
      })

      render(<ContentSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search in files/i)
      fireEvent.change(input, { target: { value: 'test' } })

      expect(screen.getByText(/search failed/i)).toBeInTheDocument()
    })

    it('should call onFileSelect when result is clicked', () => {
      mockUseContentSearch.mockReturnValue({
        results: [
          { path: 'src/app.tsx', match_count: 5 }
        ],
        isLoading: false,
        error: null
      })

      render(<ContentSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search in files/i)
      fireEvent.change(input, { target: { value: 'import' } })

      // Click on result
      const result = screen.getByText('src/app.tsx')
      fireEvent.click(result)

      expect(mockOnFileSelect).toHaveBeenCalledWith('src/app.tsx')
    })

    it('should clear results when query is empty', () => {
      mockUseContentSearch.mockReturnValue({
        results: [
          { path: 'src/app.tsx', match_count: 5 }
        ],
        isLoading: false,
        error: null
      })

      const { rerender } = render(<ContentSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search in files/i)
      fireEvent.change(input, { target: { value: 'import' } })

      // Result visible
      expect(screen.getByText('src/app.tsx')).toBeInTheDocument()

      // Update mock to return empty results
      mockUseContentSearch.mockReturnValue({
        results: [],
        isLoading: false,
        error: null
      })

      // Clear input
      fireEvent.change(input, { target: { value: '' } })
      rerender(<ContentSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      // Results should be cleared
      expect(screen.queryByText('src/app.tsx')).not.toBeInTheDocument()
    })
  })

  describe('Integration with useContentSearch hook', () => {
    it('should pass teamId and query to useContentSearch hook', () => {
      render(<ContentSearch teamId="test-team-123" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search in files/i)
      fireEvent.change(input, { target: { value: 'my query' } })

      expect(mockUseContentSearch).toHaveBeenCalledWith('test-team-123', 'my query')
    })

    it('should handle query updates reactively', () => {
      render(<ContentSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search in files/i)

      fireEvent.change(input, { target: { value: 'first' } })
      expect(mockUseContentSearch).toHaveBeenCalledWith('test-team', 'first')

      fireEvent.change(input, { target: { value: 'second' } })
      expect(mockUseContentSearch).toHaveBeenCalledWith('test-team', 'second')
    })
  })
})
