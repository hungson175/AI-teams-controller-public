import * as React from "react"

const DESKTOP_BREAKPOINT = 1024

/**
 * Hook to detect if viewport is desktop-sized (1024px+)
 * Used for file browser responsive layout
 */
export function useIsDesktop() {
  const [isDesktop, setIsDesktop] = React.useState<boolean | undefined>(undefined)

  React.useEffect(() => {
    const mql = window.matchMedia(`(min-width: ${DESKTOP_BREAKPOINT}px)`)
    const onChange = () => {
      setIsDesktop(window.innerWidth >= DESKTOP_BREAKPOINT)
    }
    mql.addEventListener("change", onChange)
    setIsDesktop(window.innerWidth >= DESKTOP_BREAKPOINT)
    return () => mql.removeEventListener("change", onChange)
  }, [])

  return !!isDesktop
}
