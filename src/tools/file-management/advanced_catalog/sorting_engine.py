"""Sorting engine for the Advanced File Catalog Generator.

This module provides comprehensive sorting algorithms with color assignment
for different categorization methods.
"""

from typing import List, Callable, Any
from .catalog_data_model import (
    FileEntry, SortCriteria, SizeCategory, DateCategory, 
    AlphabeticalCategory, FileType
)


class SortingEngine:
    """Handles all sorting operations with color assignment."""
    
    @staticmethod
    def sort_entries(entries: List[FileEntry], 
                    criteria: SortCriteria,
                    reverse: bool = False) -> List[FileEntry]:
        """Sort entries by the specified criteria."""
        if criteria == SortCriteria.ALPHABETICAL:
            return SortingEngine.sort_alphabetical(entries, reverse)
        elif criteria == SortCriteria.SIZE:
            return SortingEngine.sort_by_size(entries, reverse)
        elif criteria == SortCriteria.TYPE:
            return SortingEngine.sort_by_type(entries, reverse)
        elif criteria == SortCriteria.CREATED_DATE:
            return SortingEngine.sort_by_date(entries, 'created', reverse)
        elif criteria == SortCriteria.MODIFIED_DATE:
            return SortingEngine.sort_by_date(entries, 'modified', reverse)
        elif criteria == SortCriteria.ACCESSED_DATE:
            return SortingEngine.sort_by_date(entries, 'accessed', reverse)
        else:
            return entries.copy()

    @staticmethod
    def sort_alphabetical(entries: List[FileEntry], 
                         reverse: bool = False) -> List[FileEntry]:
        """Sort by name with A-Z color ranges."""
        sorted_entries = sorted(entries, 
                               key=lambda e: e.name.lower(), 
                               reverse=reverse)
        
        # Assign sort keys for color coding
        for entry in sorted_entries:
            entry.sort_key = entry.get_alphabetical_category().value
        
        return sorted_entries

    @staticmethod
    def sort_by_size(entries: List[FileEntry], 
                    reverse: bool = False) -> List[FileEntry]:
        """Sort by size with small/medium/large categories."""
        sorted_entries = sorted(entries, 
                               key=lambda e: e.size, 
                               reverse=reverse)
        
        # Assign sort keys for color coding
        for entry in sorted_entries:
            entry.sort_key = entry.get_size_category().value
        
        return sorted_entries

    @staticmethod
    def sort_by_type(entries: List[FileEntry], 
                    reverse: bool = False) -> List[FileEntry]:
        """Sort by file type with category colors."""
        # Define type order for consistent sorting
        type_order = {
            FileType.DOCUMENT: 1,
            FileType.IMAGE: 2,
            FileType.VIDEO: 3,
            FileType.AUDIO: 4,
            FileType.ARCHIVE: 5,
            FileType.EXECUTABLE: 6,
            FileType.CODE: 7,
            FileType.DATA: 8,
            FileType.OTHER: 9
        }
        
        sorted_entries = sorted(entries, 
                               key=lambda e: (type_order.get(e.file_type, 99), 
                                            e.name.lower()), 
                               reverse=reverse)
        
        # Assign sort keys for color coding
        for entry in sorted_entries:
            entry.sort_key = entry.file_type.value
        
        return sorted_entries

    @staticmethod
    def sort_by_date(entries: List[FileEntry], 
                    date_type: str = 'modified',
                    reverse: bool = False) -> List[FileEntry]:
        """Sort by date with recent/moderate/old categories."""
        # Get the appropriate date field
        if date_type == 'created':
            date_key = lambda e: e.created_date
        elif date_type == 'accessed':
            date_key = lambda e: e.accessed_date
        else:
            date_key = lambda e: e.modified_date
        
        sorted_entries = sorted(entries, 
                               key=date_key, 
                               reverse=reverse)
        
        # Assign sort keys for color coding
        for entry in sorted_entries:
            entry.sort_key = entry.get_date_category(date_type).value
        
        return sorted_entries

    @staticmethod
    def sort_multi_criteria(entries: List[FileEntry], 
                           criteria_list: List[tuple]) -> List[FileEntry]:
        """Sort by multiple criteria with priority.
        
        Args:
            entries: List of file entries to sort
            criteria_list: List of (SortCriteria, reverse) tuples in priority order
        """
        if not criteria_list:
            return entries.copy()
        
        # Build composite sort key
        def multi_key(entry: FileEntry) -> tuple:
            keys = []
            for criteria, reverse in criteria_list:
                if criteria == SortCriteria.ALPHABETICAL:
                    key = entry.name.lower()
                elif criteria == SortCriteria.SIZE:
                    key = entry.size
                elif criteria == SortCriteria.TYPE:
                    type_order = {
                        FileType.DOCUMENT: 1, FileType.IMAGE: 2,
                        FileType.VIDEO: 3, FileType.AUDIO: 4,
                        FileType.ARCHIVE: 5, FileType.EXECUTABLE: 6,
                        FileType.CODE: 7, FileType.DATA: 8,
                        FileType.OTHER: 9
                    }
                    key = type_order.get(entry.file_type, 99)
                elif criteria == SortCriteria.CREATED_DATE:
                    key = entry.created_date
                elif criteria == SortCriteria.MODIFIED_DATE:
                    key = entry.modified_date
                elif criteria == SortCriteria.ACCESSED_DATE:
                    key = entry.accessed_date
                else:
                    key = 0
                
                # Apply reverse if needed
                if reverse and isinstance(key, (int, float)):
                    key = -key
                elif reverse and hasattr(key, '__lt__'):
                    # For strings and dates, we'll handle reverse in the sort
                    pass
                
                keys.append(key)
            
            return tuple(keys)
        
        sorted_entries = sorted(entries, key=multi_key)
        
        # Assign sort keys based on primary criteria
        primary_criteria = criteria_list[0][0]
        if primary_criteria == SortCriteria.ALPHABETICAL:
            for entry in sorted_entries:
                entry.sort_key = entry.get_alphabetical_category().value
        elif primary_criteria == SortCriteria.SIZE:
            for entry in sorted_entries:
                entry.sort_key = entry.get_size_category().value
        elif primary_criteria == SortCriteria.TYPE:
            for entry in sorted_entries:
                entry.sort_key = entry.file_type.value
        else:  # Date-based
            date_type = 'modified'
            if primary_criteria == SortCriteria.CREATED_DATE:
                date_type = 'created'
            elif primary_criteria == SortCriteria.ACCESSED_DATE:
                date_type = 'accessed'
            
            for entry in sorted_entries:
                entry.sort_key = entry.get_date_category(date_type).value
        
        return sorted_entries

    @staticmethod
    def group_by_category(entries: List[FileEntry], 
                         criteria: SortCriteria) -> dict:
        """Group entries by their category for the given criteria."""
        groups = {}
        
        for entry in entries:
            if criteria == SortCriteria.ALPHABETICAL:
                category = entry.get_alphabetical_category().value
            elif criteria == SortCriteria.SIZE:
                category = entry.get_size_category().value
            elif criteria == SortCriteria.TYPE:
                category = entry.file_type.value
            else:  # Date-based
                date_type = 'modified'
                if criteria == SortCriteria.CREATED_DATE:
                    date_type = 'created'
                elif criteria == SortCriteria.ACCESSED_DATE:
                    date_type = 'accessed'
                category = entry.get_date_category(date_type).value
            
            if category not in groups:
                groups[category] = []
            groups[category].append(entry)
        
        return groups

    @staticmethod
    def get_category_stats(entries: List[FileEntry], 
                          criteria: SortCriteria) -> dict:
        """Get statistics for each category in the given criteria."""
        groups = SortingEngine.group_by_category(entries, criteria)
        stats = {}
        
        for category, group_entries in groups.items():
            total_size = sum(entry.size for entry in group_entries)
            stats[category] = {
                'count': len(group_entries),
                'total_size': total_size,
                'avg_size': total_size / len(group_entries) if group_entries else 0,
                'largest_file': max(group_entries, key=lambda e: e.size) if group_entries else None,
                'smallest_file': min(group_entries, key=lambda e: e.size) if group_entries else None
            }
        
        return stats

    @staticmethod
    def filter_entries(entries: List[FileEntry], 
                      filter_func: Callable[[FileEntry], bool]) -> List[FileEntry]:
        """Filter entries using a custom function."""
        return [entry for entry in entries if filter_func(entry)]

    @staticmethod
    def search_entries(entries: List[FileEntry], 
                      search_term: str,
                      search_in_path: bool = True) -> List[FileEntry]:
        """Search entries by name or path."""
        search_term = search_term.lower()
        results = []
        
        for entry in entries:
            if search_term in entry.name.lower():
                results.append(entry)
            elif search_in_path and search_term in str(entry.path).lower():
                results.append(entry)
        
        return results

    @staticmethod
    def get_sort_key_for_criteria(entry: FileEntry, 
                                 criteria: SortCriteria) -> Any:
        """Get the sort key for an entry based on criteria."""
        if criteria == SortCriteria.ALPHABETICAL:
            return entry.name.lower()
        elif criteria == SortCriteria.SIZE:
            return entry.size
        elif criteria == SortCriteria.TYPE:
            type_order = {
                FileType.DOCUMENT: 1, FileType.IMAGE: 2,
                FileType.VIDEO: 3, FileType.AUDIO: 4,
                FileType.ARCHIVE: 5, FileType.EXECUTABLE: 6,
                FileType.CODE: 7, FileType.DATA: 8,
                FileType.OTHER: 9
            }
            return type_order.get(entry.file_type, 99)
        elif criteria == SortCriteria.CREATED_DATE:
            return entry.created_date
        elif criteria == SortCriteria.MODIFIED_DATE:
            return entry.modified_date
        elif criteria == SortCriteria.ACCESSED_DATE:
            return entry.accessed_date
        else:
            return 0