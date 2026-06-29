import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ShortcutsHelp } from '@/components/ui/shortcuts-help'
import { SHORTCUTS } from '@/hooks/useKeyboardShortcuts'

describe('ShortcutsHelp', () => {
  it('renders keyboard shortcuts when open', () => {
    render(<ShortcutsHelp open onClose={vi.fn()} />)

    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Keyboard Shortcuts' })).toBeInTheDocument()

    SHORTCUTS.forEach((shortcut) => {
      const row = screen.getByText(shortcut.description).closest('div')
      expect(row).not.toBeNull()
      expect(row).toHaveTextContent(shortcut.key)
    })
  })

  it('calls onClose when the dialog is dismissed', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()

    render(<ShortcutsHelp open onClose={onClose} />)

    await user.keyboard('{Escape}')

    expect(onClose).toHaveBeenCalled()
  })

  it('does not render dialog content when closed', () => {
    render(<ShortcutsHelp open={false} onClose={vi.fn()} />)

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })
})