
### ✅ Keybindings Implementation Checklist

#### 🔧 Core Functionality
- [ ] Implement hybrid keybinding system using:
  - [ ] `QShortcut`
  - [ ] `keyPressEvent`
  - [ ] `QAction`
- [ ] Define sensible default keybindings
- [ ] Allow users to:
  - [ ] Customize keybindings
  - [ ] Save keybindings
  - [ ] Export keybindings
  - [ ] Import keybindings
- [ ] Detect platform (Windows/macOS/Linux)
  - [ ] Warn user if importing keybindings from a different platform
- [ ] Add toggle to:
  - [ ] Show keybindings in UI and menu items
  - [ ] Hide keybindings for cleaner interface

#### 🌟 Optional Enhancements
- [ ] Support multiple keybinding profiles or modes:
  - [ ] Default
  - [ ] Power-user
  - [ ] Custom
- [ ] Detect and warn about conflicting keybindings
- [ ] Provide live preview of updated keybindings in UI
- [ ] Ensure accessibility compatibility:
  - [ ] Avoid conflicts with screen readers
  - [ ] Respect system-level accessibility shortcuts


