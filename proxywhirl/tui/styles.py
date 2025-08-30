"""TUI styling constants and CSS definitions."""

# Enhanced CSS styles for ProxyWhirl TUI
TUI_STYLES = """
.status-ready {
    color: $success;
    text-style: bold;
}

.status-loading {
    color: $warning;
    text-style: bold italic;
}

/* Enhanced main layout with gradients */
.main-grid {
    grid-size: 3 2;
    grid-gutter: 1;
    height: 1fr;
    background: $surface-lighten-1;
}

.sidebar {
    column-span: 1;
    row-span: 2;
    border: thick $primary;
    padding: 1;
    background: $surface;
    border-radius: 1;
}

.content-area {
    column-span: 2; 
    row-span: 1;
    border: thick $secondary;
    padding: 1;
    background: $surface;
    border-radius: 1;
}

.bottom-panel {
    column-span: 2;
    row-span: 1;
    border: thick $accent;
    padding: 1;
    height: 12;
    background: $surface;
    border-radius: 1;
}

/* Enhanced stats widget styling */
.stats-title {
    text-style: bold;
    color: $primary;
    margin: 0 0 1 0;
    text-align: center;
    background: $primary-lighten-3;
    padding: 1;
    border-radius: 1;
}

/* Progress bar enhancements */
ProgressBar {
    margin: 1 0;
    height: 2;
    border-radius: 1;
}

ProgressBar > .bar--bar {
    background: $success;
    border-radius: 1;
}

ProgressBar > .bar--complete {
    background: $success;
}

/* Sparkline styling with health color coding */
Sparkline {
    height: 3;
    margin: 1 0;
    border: solid $text-muted;
    border-radius: 1;
}

.sparkline-response {
    background: $surface-darken-1;
}

.sparkline-health {
    background: $success;
}

.sparkline-throughput {
    background: $primary;
}

/* Health metrics row styling */
.metrics-row {
    align: center;
    margin: 1 0;
    padding: 1;
    background: $surface-lighten-1;
    border-radius: 1;
}

.metrics-row Static {
    margin: 0 1;
    padding: 1;
    background: $surface;
    border-radius: 1;
    text-style: bold;
}

/* Status indicators with emoji support */
.status-row {
    align: center;
    margin: 1 0;
}

#health-emoji {
    text-style: bold;
    margin: 0 1;
}

#trend-indicator {
    text-style: bold;
    margin: 0 1;
    color: $accent;
}

/* Enhanced button styling with animations */
.action-buttons {
    align: center;
    margin: 1 0;
}

.action-buttons Button {
    margin: 0 0 1 0;
    min-width: 16;
    height: 3;
    border-radius: 1;
    text-style: bold;
}

Button:hover {
    text-style: bold;
    color: $accent;
}

Button:focus {
    border: thick $accent;
}

/* Modal styling with shadows and gradients */
.export-modal, .settings-modal, .health-modal {
    width: 90;
    height: 40;
    background: $surface;
    border: thick $primary;
    border-radius: 2;
    padding: 2;
}

/* Health modal specific styling */
.health-modal {
    width: 95;
    height: 45;
    background: $surface;
}

.health-content {
    padding: 1;
    background: $surface-lighten-1;
    border-radius: 1;
    margin: 1 0;
    line-height: 1.5;
}

.modal-buttons {
    align: center;
    margin: 2 0;
    gap: 2;
}

.modal-title {
    text-style: bold;
    color: $primary;
    text-align: center;
    margin: 0 0 2 0;
    background: $primary-lighten-3;
    padding: 1;
    border-radius: 1;
}

.export-options, .export-buttons, .settings-buttons {
    margin: 2 0;
}

.export-buttons, .settings-buttons {
    align: center;
    gap: 2;
}

.export-action-btn {
    min-width: 12;
    height: 3;
    border-radius: 1;
    text-style: bold;
}

.export-buttons Button, .settings-buttons Button {
    margin: 0 1;
    min-width: 12;
    height: 3;
    border-radius: 1;
}

.format-section, .filter-section {
    width: 50%;
    margin: 0 1;
    padding: 1;
    border: solid $text-muted;
    border-radius: 1;
    background: $surface-lighten-1;
}

.settings-section {
    margin: 1 0 2 0;
    border: solid $text-muted;
    border-radius: 1;
    padding: 2;
    background: $surface-lighten-1;
}

.section-title {
    text-style: bold;
    color: $secondary;
    margin: 0 0 1 0;
    text-align: center;
    background: $secondary-lighten-3;
    padding: 1;
    border-radius: 1;
}

/* Enhanced input styling */
.export-input, .settings-input {
    border: solid $text-muted;
    border-radius: 1;
    padding: 1;
    margin: 1 0;
}

Input:focus {
    border: thick $accent;
}

/* Checkbox enhancements */
.export-checkbox {
    margin: 0 0 1 0;
}

Checkbox:hover {
    background: $surface-lighten-1;
}

/* RadioSet styling */
RadioSet {
    border: solid $text-muted;
    border-radius: 1;
    padding: 1;
    background: $surface;
}

RadioButton {
    margin: 0 0 1 0;
    padding: 1;
    border-radius: 1;
}

RadioButton:hover {
    background: $surface-lighten-1;
}

/* Tab styling enhancements */
TabbedContent {
    height: 1fr;
    border-radius: 1;
}

TabPane {
    padding: 1;
    background: $surface;
    border-radius: 1;
}

/* Enhanced table styling */
DataTable {
    height: 1fr;
    border-radius: 1;
}

DataTable > .datatable--header {
    background: $primary-lighten-3;
    text-style: bold;
    color: $primary;
}

DataTable > .datatable--odd-row {
    background: $surface-lighten-1;
}

DataTable > .datatable--cursor {
    background: $accent-lighten-3;
    color: $accent;
    text-style: bold;
}

/* Enhanced log styling */
Log {
    height: 1fr;
    scrollbar-size-vertical: 1;
    border: solid $text-muted;
    border-radius: 1;
    background: $surface;
    padding: 1;
}

/* Rule styling */
Rule {
    color: $text-muted;
    margin: 1 0;
}

/* Status indicators */
.status-row {
    align: center;
    margin: 1 0;
    gap: 1;
}

/* Collapsible enhancements */
Collapsible {
    border: solid $text-muted;
    border-radius: 1;
    margin: 1 0;
    background: $surface-lighten-1;
}

Collapsible:hover {
    border: solid $secondary;
}

/* Switch styling */
Switch {
    margin: 1 0;
}

Switch:focus {
    border: thick $accent;
}

/* Label enhancements */
Label {
    text-style: bold;
    color: $secondary;
    margin: 0 0 1 0;
}
"""
