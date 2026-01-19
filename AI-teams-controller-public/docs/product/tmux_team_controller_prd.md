# TMUX Team Controller PRD

## Overview

This document defines the Product Requirements for the TMUX Team
Controller system that allows the user to interact with multiple
tmux-based AI-assisted teams through a unified text-first interface.
Voice interaction will be added in later versions.

## Product Vision

Enable the user to work in a hybrid mode---sometimes typing at a
computer, sometimes walking outdoors while issuing commands
verbally---by providing a centralized UI to communicate with individual
tmux roles.

## Core Principles

-   Text-first interaction (voice out of scope for v1).
-   Direct communication with tmux panes (no AI processing in the web
    layer).
-   Real-time refresh after sending commands.
-   Multi-team, multi-role structure.

## System Scope (v1)

-   Detect tmux sessions running on the home PC via backend (FastAPI).
-   Expose endpoints to:
    -   List teams (tmux sessions)
    -   List roles (tmux panes)
    -   Send command text to specific pane
    -   Fetch latest pane output

## Key Behaviors

### 1. Tab-to-Role Binding

-   User selects a team on the left.
-   User selects a role (tab) on the right.
-   Tab corresponds directly to one tmux pane.

### 2. Messaging Flow

-   User types a message.
-   Backend sends that message directly to the tmux pane.
-   Backend waits `N` seconds (default 5, configurable).
-   After waiting, backend fetches updated pane content and returns it.

### 3. Refresh Behavior

-   Manual refresh button reloads pane state immediately.

## Non-Goals (v1)

-   No boss terminal inside this product.
-   No AI reasoning layer in the UI.
-   No cross-machine tmux registration.
-   No voice support (scoped out).

## Future Scope

-   Add voice input/output.
-   Add multi-machine registry.
-   Add role-level automation logic.
