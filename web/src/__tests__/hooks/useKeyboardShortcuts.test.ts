import { describe, it, expect, vi, afterEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useKeyboardShortcuts, SHORTCUTS } from '@/hooks/useKeyboardShortcuts'

describe('useKeyboardShortcuts', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('calls onSearch when / is pressed', () => {
    const onSearch = vi.fn()
    renderHook(() => useKeyboardShortcuts({ onSearch }))
    
    document.dispatchEvent(new KeyboardEvent('keydown', { key: '/' }))
    
    expect(onSearch).toHaveBeenCalledTimes(1)
  })

  it('calls onClearFilters when Escape is pressed', () => {
    const onClearFilters = vi.fn()
    renderHook(() => useKeyboardShortcuts({ onClearFilters }))
    
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    
    expect(onClearFilters).toHaveBeenCalledTimes(1)
  })

  it('calls onCopyAll when c is pressed', () => {
    const onCopyAll = vi.fn()
    renderHook(() => useKeyboardShortcuts({ onCopyAll }))
    
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'c' }))
    
    expect(onCopyAll).toHaveBeenCalledTimes(1)
  })

  it('calls onToggleHelp when ? is pressed', () => {
    const onToggleHelp = vi.fn()
    renderHook(() => useKeyboardShortcuts({ onToggleHelp }))
    
    document.dispatchEvent(new KeyboardEvent('keydown', { key: '?' }))
    
    expect(onToggleHelp).toHaveBeenCalledTimes(1)
  })

  it('calls onToggleFilters when f is pressed', () => {
    const onToggleFilters = vi.fn()
    renderHook(() => useKeyboardShortcuts({ onToggleFilters }))
    
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'f' }))
    
    expect(onToggleFilters).toHaveBeenCalledTimes(1)
  })

  it('ignores shortcuts when modifier keys are pressed', () => {
    const onSearch = vi.fn()
    renderHook(() => useKeyboardShortcuts({ onSearch }))
    
    document.dispatchEvent(new KeyboardEvent('keydown', { key: '/', metaKey: true }))
    document.dispatchEvent(new KeyboardEvent('keydown', { key: '/', ctrlKey: true }))
    document.dispatchEvent(new KeyboardEvent('keydown', { key: '/', altKey: true }))
    
    expect(onSearch).not.toHaveBeenCalled()
  })

  it('does not call handlers for unrelated keys', () => {
    const onSearch = vi.fn()
    const onClearFilters = vi.fn()
    renderHook(() => useKeyboardShortcuts({ onSearch, onClearFilters }))
    
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'x' }))
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }))
    
    expect(onSearch).not.toHaveBeenCalled()
    expect(onClearFilters).not.toHaveBeenCalled()
  })
})

describe('SHORTCUTS constant', () => {
  it('contains all expected shortcuts', () => {
    expect(SHORTCUTS).toHaveLength(5)
    
    const keys = SHORTCUTS.map(s => s.key)
    expect(keys).toContain('/')
    expect(keys).toContain('f')
    expect(keys).toContain('c')
    expect(keys).toContain('Esc')
    expect(keys).toContain('?')
  })

  it('has descriptions for all shortcuts', () => {
    SHORTCUTS.forEach(shortcut => {
      expect(shortcut.description).toBeTruthy()
      expect(typeof shortcut.description).toBe('string')
    })
  })
})
