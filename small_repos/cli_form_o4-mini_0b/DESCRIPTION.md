# cli_form

## Purpose and Motivation
An interactive command-line form builder that simplifies gathering structured user input in terminal applications. Built on `curses` (or plain `input` fallback), it lets developers define forms with fields, validation rules, default values, and conditional flows, without reinventing screen management. This library aims to reduce boilerplate in text-based wizards, installers, or interactive scripts.  
Common use cases include survey scripts, onboarding CLI tools, and interactive configuration flows.  
Extension points: custom field types (password, date), pluggable renderers, or themeable layouts.

## Core Functionality
- Define forms as sequences of fields with labels, types, default values, and validators  
- Support for primitive field types: text, integer, choice lists, yes/no toggles  
- Navigation controls: forward/backward between fields, skip logic based on previous answers  
- Fallback to line-by-line prompts if `curses` is unavailable  
- Hooks for on-change callbacks and real-time validation feedback  
- Export completed form data as a dict or JSON string

