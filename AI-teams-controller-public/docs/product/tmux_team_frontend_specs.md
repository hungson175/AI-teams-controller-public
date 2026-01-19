# TMUX Team Frontend Specs

## Overview

Describes UI/UX design for the TMUX Team Controller web application.
This is the text-based version (v1) without voice.

## Layout

### Left Panel: Team List

-   Displays all tmux sessions.
-   Each item selectable.
-   When selected, loads roles for that team.

### Right Panel: Role Tabs

-   Each role (pane) becomes one tab.
-   When a tab is active:
    -   Terminal-like output area shows latest pane state.
    -   Input box at bottom allows sending a message.

## Core Interactions

### 1. Sending Messages

-   User types text into input box.
-   On send:
    -   Call backend endpoint: `/send/{team}/{role}`
    -   Input is forwarded directly to tmux pane.
    -   UI enters "pending" state for configurable delay (default 5
        seconds).
    -   After delay, UI fetches updated pane output.

### 2. Refresh Button

-   Present in each tab.
-   Calls backend `/state/{team}/{role}` immediately.

### 3. Configurable Delay

-   UI settings panel lets user configure delay (3--10 seconds
    recommended).
-   Stored locally per browser session.

## Data Rendering

-   Terminal output styled in monospace.
-   Line wrapping enabled.
-   Auto-scroll to bottom on new content.

## Tab Structure

-   Roles displayed in this order:
    1.  PM
    2.  Researcher
    3.  Engineer / Developer
    4.  Code Reviewer
-   Future versions may support drag-and-drop reorder.

## Responsiveness

-   Mobile layout:
    -   Team list becomes collapsible.
    -   Tabs convert to horizontal scroll or dropdown.
    -   Input area fixed at bottom.

## Future Additions

-   Voice button (disabled for v1).
-   Real-time streaming logs.
