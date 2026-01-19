import createFuzzySearch from '@nozbe/microfuzz'

/**
 * Create a fuzzy search function for a list of command strings
 *
 * @param commands - List of commands to search
 * @returns Search function that takes query and limit
 */
export function createCommandSearch(commands: string[]) {
  const search = createFuzzySearch(commands)

  return (query: string, limit: number = 5): string[] => {
    if (!query || query.length < 1) return []

    const results = search(query)
    return results
      .slice(0, limit)
      .map(result => result.item)
  }
}

/**
 * Fuzzy search result with highlighting
 */
export interface FuzzySearchResult {
  item: string
  highlighted: string
}

/**
 * Fuzzy search with highlighting support
 * Returns matches with highlighted characters marked with <mark> tags
 *
 * @param items - List of items to search
 * @param query - Search query
 * @param limit - Maximum results to return
 * @returns Array of results with item and highlighted string
 */
export function fuzzySearchWithHighlight(
  items: string[],
  query: string,
  limit: number = 5
): FuzzySearchResult[] {
  if (!query || query.length < 1) return []

  // getText must return an array of strings
  const search = createFuzzySearch(items, { getText: (item: string) => [item] })
  const results = search(query)

  return results.slice(0, limit).map(result => {
    // matches is Array<HighlightRanges | null>, we use first element for single string items
    const matchRanges = result.matches[0] ?? []
    return {
      item: result.item,
      highlighted: highlightMatches(result.item, matchRanges)
    }
  })
}

/**
 * Highlight matched character ranges with <mark> tags
 *
 * @param text - Original text
 * @param matches - Array of [start, end] tuples for matched ranges
 * @returns HTML string with <mark> tags around matched characters
 */
function highlightMatches(text: string, matches: [number, number][] | undefined): string {
  if (!matches || matches.length === 0) return text

  let result = ''
  let lastIndex = 0

  for (const [start, end] of matches) {
    result += text.slice(lastIndex, start)
    result += `<mark>${text.slice(start, end + 1)}</mark>`
    lastIndex = end + 1
  }
  result += text.slice(lastIndex)

  return result
}
