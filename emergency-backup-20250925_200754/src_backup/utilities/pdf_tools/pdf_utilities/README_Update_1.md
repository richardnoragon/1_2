# Project Checklist: Suggestions for Python/PyQt Projects

## 1. README & Documentation
- [ ] **Specify License**: Choose an open-source license (e.g., MIT, GPLv3, Apache 2.0) and add a generic empty `LICENSE` file as place holder.
- [ ] Update the `[Specify License]` link in the README.
- [ ] **Contribution Guidelines**: Create a `CONTRIBUTING.md` file outlining how to report bugs, suggest features, and submit pull requests. add generic empty file as place holder.
- [ ] Update the `[Contribution Guidelines]` link in the README.
- [ ] **Screenshots/GIFs**: Add screenshots of the main interface and key feature dialogues. Create a short GIF demonstrating workflows.
- [ ] **Key Dependencies**: Mention core PDF libraries directly in the README (e.g., PyMuPDF, ReportLab, Camelot/Tabula).
- [ ] **Badges**: Add badges (e.g., build status, license, Python version support) using shields.io.
- [ ] **Detailed Usage**: Explain the main window layout and how to access different tools within the GUI.

## 2. Code Structure & Maintainability
- [ ] **Modular Design**:
  - [ ] Separate UI code (`.ui` files) from core PDF processing logic.
  - [ ] Group related functions into utility modules/packages.
  - [ ] Use a central entry point (`main.py`) for setting up the application and event loop.
- [ ] **Configuration Management**: Use a configuration file (e.g., INI, JSON, YAML) or Qt's `QSettings` for default paths, settings, etc. - please create a central configuration file.  different modules can have different settings but same file edit settings.
- [ ] please make sure **Error Handling**: Provide robust error handling using `try...except`. Display informative error messages via GUI dialogs (`QMessageBox`). is involked in all modules
- [-] **Logging**: Implement logging with Python's `logging` module for debugging and issue tracking.
- [ ] **Dependency Management**: Pin specific versions in `requirements.txt` for reproducible builds.
- [ ] **Code Style**: Use tools like `flake8` and `black` to enforce consistent coding style (PEP 8).

## 3. User Experience (GUI)
- [ ] **Responsiveness / Background Threads**: Use `QThread` to run long tasks in separate threads. Communicate progress/results back to the GUI.
- [x] **Progress Indication**: Use `QProgressBar` or status messages for long tasks.
- [x] **Clear Feedback**: Inform users about success, errors, or actions via dialogs (`QMessageBox`) or status bar messages.
- [ ] **Consistency**: Ensure consistent layout, naming, and workflow across modules.
- [ ] **File Dialog Defaults**: Remember the last used directory in file dialogs (`QFileDialog`).
- [-] **Drag and Drop**: Add drag-and-drop support for uploading files.

## 4. Features & Functionality
- [x] **Batch Processing**: Enable operations (e.g., Convert to Images, Compress, Watermark) for multiple files or folders.
- [x] **Page Management**: Add features like deleting, reordering, and rotating pages.
	combine 2 or more pdfs to a single one. user can choose the order.
	split pdf user can shoosce between number of pages, sections or capitals
	reorder the pages, can give a order of the pages
	rotate pages, user can coose one or more pages to rotate, either clokwise 90 counterclockwise 90 or 180
	delete pages, user can choose 1 or more page to be deleted
- [ ] **OCR (Optical Character Recognition)**: Use `pytesseract` for text extraction from image-based PDFs.
- [-] **Preview Pane**: Show a preview of operations like Watermarking or Highlighting on sample pages.
- [x] **Advanced Highlighting/Annotation**: Allow different highlight colors, text annotations, and drawing shapes.
- [x] **Table Extraction Tuning**: Expose tuning parameters for tools like Camelot.

## 5. Testing & Quality Assurance
- [ ] **Unit Tests**: Write unit tests for core logic using `pytest`. Test edge cases (e.g., empty, corrupted, or password-protected files).
- [ ] **Integration Tests**: Test interactions between modules.
- [ ] **GUI Testing**: Perform manual testing and consider frameworks like `pytest-qt`.
- [ ] **Continuous Integration (CI)**: Use tools like GitHub Actions or GitLab CI to automate tests and linting.

## 6. Packaging & Distribution
- [ ] **Executable Creation**: Use `PyInstaller` or `cx_Freeze` to create standalone executables.
- [ ] **Cross-Platform Testing**: Test the application thoroughly on Windows, macOS, and Linux.

## Prioritization (Quick Wins)
- [ ] Specify License and Contribution Docs.
- [ ] Implement background threads for responsive GUI.
- [ ] Add robust error handling and user feedback mechanisms.
- [ ] Improve code structuring by separating UI and logic.
- [ ] Add screenshots/GIFs in README for better understanding.

---

This checklist should help you tackle your Python/PyQt project systematically. Let me know if you'd like further refinements or assistance!