#!/usr/bin/env python3
"""
Script to fix linting issues in search_engine.py systematically.
"""

import re
from pathlib import Path


def fix_linting_issues():
    """Fix all linting issues in search_engine.py"""
    file_path = Path("src/rfu/advanced_folders/core/search_engine.py")
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix trailing whitespace (W291, W293)
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Remove trailing whitespace
        fixed_line = line.rstrip()
        fixed_lines.append(fixed_line)
    
    # Add final newline if missing (W292)
    if fixed_lines and fixed_lines[-1]:
        fixed_lines.append('')
    
    content = '\n'.join(fixed_lines)
    
    # Fix specific long lines by breaking them appropriately
    long_line_fixes = [
        # Database index creation lines
        (r'(\s+)CREATE INDEX IF NOT EXISTS idx_file_extension ON file_index\(extension\);\s+',
         r'\1CREATE INDEX IF NOT EXISTS idx_file_extension\n\1    ON file_index(extension);'),
        (r'(\s+)CREATE INDEX IF NOT EXISTS idx_file_modified ON file_index\(modified_time\);\s+',
         r'\1CREATE INDEX IF NOT EXISTS idx_file_modified\n\1    ON file_index(modified_time);'),
        (r'(\s+)CREATE INDEX IF NOT EXISTS idx_file_type ON file_index\(is_file, is_directory\);\s*',
         r'\1CREATE INDEX IF NOT EXISTS idx_file_type\n\1    ON file_index(is_file, is_directory);'),
         
        # Method signatures
        (r'def _search_by_name_db\(self, conn: sqlite3\.Connection, parameters: SearchParameters\) -> Iterator\[SearchResult\]:',
         r'def _search_by_name_db(\n        self, conn: sqlite3.Connection, parameters: SearchParameters\n    ) -> Iterator[SearchResult]:'),
        (r'def _search_by_content_db\(self, conn: sqlite3\.Connection, parameters: SearchParameters\) -> Iterator\[SearchResult\]:',
         r'def _search_by_content_db(\n        self, conn: sqlite3.Connection, parameters: SearchParameters\n    ) -> Iterator[SearchResult]:'),
        (r'def _search_combined_db\(self, conn: sqlite3\.Connection, parameters: SearchParameters\) -> Iterator\[SearchResult\]:',
         r'def _search_combined_db(\n        self, conn: sqlite3.Connection, parameters: SearchParameters\n    ) -> Iterator[SearchResult]:'),
        (r'def _calculate_relevance_db\(self, file_info: FileInfo, parameters: SearchParameters\) -> float:',
         r'def _calculate_relevance_db(\n        self, file_info: FileInfo, parameters: SearchParameters\n    ) -> float:'),
        (r'def _post_process_results\(self, results: List\[SearchResult\], parameters: SearchParameters\) -> List\[SearchResult\]:',
         r'def _post_process_results(\n        self, results: List[SearchResult], parameters: SearchParameters\n    ) -> List[SearchResult]:'),
        (r'def get_recent_search_metrics\(self, limit: int = 10\) -> List\[Dict\[str, Any\]\]:',
         r'def get_recent_search_metrics(\n        self, limit: int = 10\n    ) -> List[Dict[str, Any]]:'),
         
        # Long assignment lines
        (r'(\s+)placeholders = ",".join\("?" \* len\(parameters\.file_type_filter\.include_extensions\)\)\s*',
         r'\1placeholders = ",".join(\n\1    "?" * len(parameters.file_type_filter.include_extensions)\n\1)'),
        (r'(\s+)sort_order = "DESC" if parameters\.sort_order == SortOrder\.DESC else "ASC"',
         r'\1sort_order = (\n\1    "DESC" if parameters.sort_order == SortOrder.DESC else "ASC"\n\1)'),
        (r'(\s+)relevance_score = self\._calculate_relevance_db\(file_info, parameters\)',
         r'\1relevance_score = self._calculate_relevance_db(\n\1    file_info, parameters\n\1)'),
        (r'(\s+)match_highlights=\[parameters\.query\] if parameters\.query else \[\]',
         r'\1match_highlights=(\n\1    [parameters.query] if parameters.query else []\n\1)'),
         
        # Database operations
        (r'(\s+)file_cursor = conn\.execute\("SELECT \* FROM file_index WHERE path = \?", \(row\[\'path\'\],\)\)',
         r'\1file_cursor = conn.execute(\n\1    "SELECT * FROM file_index WHERE path = ?", (row[\'path\'],)\n\1)'),
        (r'(\s+)conn\.execute\("DELETE FROM file_content_fts WHERE path = \?", \(file_path,\)\)',
         r'\1conn.execute(\n\1    "DELETE FROM file_content_fts WHERE path = ?", (file_path,)\n\1)'),
        (r'(\s+)cursor = conn\.execute\("SELECT COUNT\(\*\) as total_files FROM file_index"\)',
         r'\1cursor = conn.execute(\n\1    "SELECT COUNT(*) as total_files FROM file_index"\n\1)'),
        (r'(\s+)cursor = conn\.execute\("SELECT COUNT\(\*\) as content_entries FROM file_content_fts"\)\s*',
         r'\1cursor = conn.execute(\n\1    "SELECT COUNT(*) as content_entries FROM file_content_fts"\n\1)'),
        (r'(\s+)query = "SELECT \* FROM file_content_fts WHERE file_content_fts MATCH \?"',
         r'\1query = (\n\1    "SELECT * FROM file_content_fts WHERE file_content_fts MATCH ?"\n\1)'),
         
        # Conditional statements
        (r'(\s+)if parameters\.query and parameters\.query\.lower\(\) in file_info\.name\.lower\(\):',
         r'\1if (parameters.query and\n\1        parameters.query.lower() in file_info.name.lower()):'),
        (r'(\s+)db_size_mb = Path\(self\.db_path\)\.stat\(\)\.st_size / \(1024 \* 1024\) if Path\(self\.db_path\)\.exists\(\) else 0',
         r'\1db_size_mb = (\n\1    Path(self.db_path).stat().st_size / (1024 * 1024)\n\1    if Path(self.db_path).exists() else 0\n\1)'),
         
        # Thread pool and indexing strategy checks
        (r'(\s+)with ThreadPoolExecutor\(max_workers=self\.max_workers\) as executor:',
         r'\1with ThreadPoolExecutor(\n\1    max_workers=self.max_workers\n\1) as executor:'),
        (r'(\s+)self\.logger\.info\(f"Search engine initialized with strategy: {indexing_strategy\.value}"\)',
         r'\1self.logger.info(\n\1    f"Search engine initialized with strategy: "\n\1    f"{indexing_strategy.value}"\n\1)'),
        (r'(\s+)if self\.indexing_strategy in \[IndexingStrategy\.MEMORY_ONLY, IndexingStrategy\.HYBRID\]:\s*',
         r'\1if self.indexing_strategy in [\n\1    IndexingStrategy.MEMORY_ONLY, IndexingStrategy.HYBRID\n\1]:'),
        (r'(\s+)self\.memory_index = MemorySearchIndex\(max_files=self\.max_memory_files\)',
         r'\1self.memory_index = MemorySearchIndex(\n\1    max_files=self.max_memory_files\n\1)'),
        (r'(\s+)if self\.indexing_strategy in \[IndexingStrategy\.DISK_BASED, IndexingStrategy\.DATABASE_ONLY, IndexingStrategy\.HYBRID\]:',
         r'\1if self.indexing_strategy in [\n\1    IndexingStrategy.DISK_BASED,\n\1    IndexingStrategy.DATABASE_ONLY,\n\1    IndexingStrategy.HYBRID\n\1]:'),
        (r'(\s+)self\.indexing_strategy in \[IndexingStrategy\.DISK_BASED, IndexingStrategy\.DATABASE_ONLY, IndexingStrategy\.HYBRID\]\):',
         r'\1self.indexing_strategy in [\n\1    IndexingStrategy.DISK_BASED,\n\1    IndexingStrategy.DATABASE_ONLY,\n\1    IndexingStrategy.HYBRID\n\1]):'),
        (r'(\s+)self\.logger\.error\(f"Error indexing file {file_info\.path}: {str\(e\)}"\)',
         r'\1self.logger.error(\n\1    f"Error indexing file {file_info.path}: {str(e)}"\n\1)'),
        (r'(\s+)if self\.memory_index and self\.memory_index\.get_statistics\(\)\[\'total_files\'\] < 10000:\s*',
         r'\1if (self.memory_index and\n\1        self.memory_index.get_statistics()[\'total_files\'] < 10000):'),
        (r'(\s+)def _search_hybrid\(self, parameters: SearchParameters\) -> Iterator\[SearchResult\]:',
         r'\1def _search_hybrid(\n\1    self, parameters: SearchParameters\n\1) -> Iterator[SearchResult]:'),
        (r'(\s+)metrics\.final_results = min\(len\(results\), parameters\.max_results\)',
         r'\1metrics.final_results = min(\n\1    len(results), parameters.max_results\n\1)'),
        (r'(\s+)metrics\.total_search_time_ms = \(datetime\.now\(\) - start_time\)\.total_seconds\(\) \* 1000',
         r'\1metrics.total_search_time_ms = (\n\1    (datetime.now() - start_time).total_seconds() * 1000\n\1)'),
        (r'(\s+)for i, result in enumerate\(results\[parameters\.offset:parameters\.offset \+ parameters\.max_results\]\):',
         r'\1for i, result in enumerate(\n\1    results[parameters.offset:parameters.offset + parameters.max_results]\n\1):'),
        (r'(\s+)return QueryPlan\.PARALLEL  # Content search benefits from database FTS',
         r'\1# Content search benefits from database FTS\n\1return QueryPlan.PARALLEL'),
        (r'(\s+)avg_search_time = sum\(m\.total_search_time_ms for m in recent_metrics\) / len\(recent_metrics\)',
         r'\1avg_search_time = (\n\1    sum(m.total_search_time_ms for m in recent_metrics) /\n\1    len(recent_metrics)\n\1)'),
    ]
    
    # Apply fixes
    for pattern, replacement in long_line_fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Fix file insertion parameters that are too long
    file_insert_pattern = r'(\s+)file_info\.path, file_info\.name, file_info\.extension, file_info\.size_bytes,\s*'
    file_insert_replacement = r'\1file_info.path, file_info.name, file_info.extension,\n\1file_info.size_bytes,'
    content = re.sub(file_insert_pattern, file_insert_replacement, content)
    
    # Fix datetime isoformat line
    datetime_pattern = r'(\s+)file_info\.created_time\.isoformat\(\), file_info\.modified_time\.isoformat\(\),\s*'
    datetime_replacement = r'\1file_info.created_time.isoformat(),\n\1file_info.modified_time.isoformat(),'
    content = re.sub(datetime_pattern, datetime_replacement, content)
    
    # Fix boolean conversion lines
    bool_pattern1 = r'(\s+)1 if file_info\.is_file else 0, 1 if file_info\.is_directory else 0,'
    bool_replacement1 = r'\1(1 if file_info.is_file else 0),\n\1(1 if file_info.is_directory else 0),'
    content = re.sub(bool_pattern1, bool_replacement1, content)
    
    bool_pattern2 = r'(\s+)1 if file_info\.is_symlink else 0, 1 if file_info\.is_hidden else 0,'
    bool_replacement2 = r'\1(1 if file_info.is_symlink else 0),\n\1(1 if file_info.is_hidden else 0),'
    content = re.sub(bool_pattern2, bool_replacement2, content)
    
    # Fix visually indented line issues (E129)
    e129_pattern = r'(\s+)if \(self\.database_index and\n(\s+)self\.indexing_strategy in \['
    e129_replacement = r'\1if (self.database_index and\n\1        self.indexing_strategy in ['
    content = re.sub(e129_pattern, e129_replacement, content)
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed linting issues in {file_path}")

if __name__ == "__main__":
    fix_linting_issues()