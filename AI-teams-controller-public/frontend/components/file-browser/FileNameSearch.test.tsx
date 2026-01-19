/**
 * FileNameSearch Component Tests (Story 2 REVISED: Filename Search)
 * TDD Approach: Write tests FIRST, then implement component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { FileNameSearch } from './FileNameSearch'

// Hoist mocks to ensure proper initialization order
const { mockSearch, mockUseFileListCache } = vi.hoisted(() => {
  return {
    mockSearch: vi.fn(),
    mockUseFileListCache: vi.fn()
  }
})

// Mock uFuzzy
vi.mock('@leeoniya/ufuzzy', () => {
  return {
    default: class MockUFuzzy {
      search = mockSearch
    }
  }
})

// Mock useFileListCache hook
vi.mock('@/hooks/useFileListCache', () => ({
  useFileListCache: (teamId: string) => mockUseFileListCache(teamId)
}))

describe('FileNameSearch', () => {
  const mockOnFileSelect = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    mockUseFileListCache.mockReturnValue({
      files: [],
      isLoading: false,
      isStale: false,
      refetch: vi.fn()
    })
    mockSearch.mockReturnValue(null)
  })

  describe('Search input', () => {
    it('should render search input with placeholder', () => {
      render(<FileNameSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search files/i)
      expect(input).toBeInTheDocument()
    })

    it('should render search icon', () => {
      render(<FileNameSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const searchIcon = document.querySelector('.lucide-search')
      expect(searchIcon).toBeInTheDocument()
    })

    it('should update query on typing', () => {
      render(<FileNameSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search files/i)
      fireEvent.change(input, { target: { value: 'test' } })

      expect(input).toHaveValue('test')
    })

    it('should show clear button when query is not empty', () => {
      render(<FileNameSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search files/i)

      // Initially no clear button
      expect(screen.queryByRole('button', { name: /clear/i })).not.toBeInTheDocument()

      // Type something
      fireEvent.change(input, { target: { value: 'test' } })

      // Clear button should appear
      expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument()
    })

    it('should clear input when clear button clicked', () => {
      render(<FileNameSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search files/i) as HTMLInputElement
      fireEvent.change(input, { target: { value: 'test' } })

      const clearButton = screen.getByRole('button', { name: /clear/i })
      fireEvent.click(clearButton)

      expect(input.value).toBe('')
    })
  })

  describe('Search results with fuzzy matching', () => {
    it('should display fuzzy search results', () => {
      mockUseFileListCache.mockReturnValue({
        files: ['src/app.tsx', 'lib/utils.ts', 'components/Button.tsx'],
        isLoading: false,
        isStale: false,
        refetch: vi.fn()
      })

      // Mock uFuzzy returning indexes [0, 2] (app.tsx, Button.tsx)
      mockSearch.mockReturnValue([[0, 2], null, null])

      render(<FileNameSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search files/i)
      fireEvent.change(input, { target: { value: 'app' } })

      // Should show matching results
      expect(screen.getByText('src/app.tsx')).toBeInTheDocument()
      expect(screen.getByText('components/Button.tsx')).toBeInTheDocument()
      expect(screen.queryByText('lib/utils.ts')).not.toBeInTheDocument()
    })

    it('should call onFileSelect when result is clicked', () => {
      mockUseFileListCache.mockReturnValue({
        files: ['src/app.tsx'],
        isLoading: false,
        isStale: false,
        refetch: vi.fn()
      })

      mockSearch.mockReturnValue([[0], null, null])

      render(<FileNameSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search files/i)
      fireEvent.change(input, { target: { value: 'app' } })

      const result = screen.getByText('src/app.tsx')
      fireEvent.click(result)

      expect(mockOnFileSelect).toHaveBeenCalledWith('src/app.tsx')
    })

    it('should clear query after clicking result', () => {
      mockUseFileListCache.mockReturnValue({
        files: ['src/app.tsx'],
        isLoading: false,
        isStale: false,
        refetch: vi.fn()
      })

      mockSearch.mockReturnValue([[0], null, null])

      render(<FileNameSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search files/i) as HTMLInputElement
      fireEvent.change(input, { target: { value: 'app' } })

      const result = screen.getByText('src/app.tsx')
      fireEvent.click(result)

      expect(input.value).toBe('')
    })

    it('should show "no results" when search returns empty', () => {
      mockUseFileListCache.mockReturnValue({
        files: ['src/app.tsx'],
        isLoading: false,
        isStale: false,
        refetch: vi.fn()
      })

      mockSearch.mockReturnValue(null)

      render(<FileNameSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search files/i)
      fireEvent.change(input, { target: { value: 'nonexistent' } })

      expect(screen.getByText(/no files found/i)).toBeInTheDocument()
    })

    it('should hide results when query is cleared', () => {
      mockUseFileListCache.mockReturnValue({
        files: ['src/app.tsx'],
        isLoading: false,
        isStale: false,
        refetch: vi.fn()
      })

      mockSearch.mockReturnValue([[0], null, null])

      render(<FileNameSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search files/i)
      fireEvent.change(input, { target: { value: 'app' } })

      // Result visible
      expect(screen.getByText('src/app.tsx')).toBeInTheDocument()

      // Clear query
      fireEvent.change(input, { target: { value: '' } })

      // Results should be hidden
      expect(screen.queryByText('src/app.tsx')).not.toBeInTheDocument()
    })
  })

  describe('Loading state', () => {
    it('should show loading state when fetching files', () => {
      mockUseFileListCache.mockReturnValue({
        files: [],
        isLoading: true,
        isStale: false,
        refetch: vi.fn()
      })

      render(<FileNameSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search files/i)
      fireEvent.change(input, { target: { value: 'test' } })

      expect(screen.getByText(/loading/i)).toBeInTheDocument()
    })
  })

  describe('Integration with useFileListCache', () => {
    it('should pass teamId to useFileListCache', () => {
      render(<FileNameSearch teamId="my-team-123" onFileSelect={mockOnFileSelect} />)

      expect(mockUseFileListCache).toHaveBeenCalledWith('my-team-123')
    })

    it('should use files from useFileListCache for search', () => {
      const mockFiles = ['file1.ts', 'file2.ts', 'file3.ts']
      mockUseFileListCache.mockReturnValue({
        files: mockFiles,
        isLoading: false,
        isStale: false,
        refetch: vi.fn()
      })

      render(<FileNameSearch teamId="test-team" onFileSelect={mockOnFileSelect} />)

      const input = screen.getByPlaceholderText(/search files/i)
      fireEvent.change(input, { target: { value: 'file' } })

      // Should call uFuzzy search with file list
      expect(mockSearch).toHaveBeenCalledWith(mockFiles, 'file')
    })
  })
})
