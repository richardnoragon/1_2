"""
Regular Expression Support System for Advanced Folders - Week 7 Implementation.

Enterprise-grade regular expression engine with security validation,
performance optimization, and comprehensive pattern matching capabilities
for file names, paths, and content searches.

Features:
- Secure regex validation and ReDoS attack prevention
- Performance-optimized pattern compilation and caching
- Multi-threaded pattern matching with timeout controls
- Pattern library for common file operations
- Advanced pattern composition and transformation
- Cross-platform path pattern support
- Comprehensive error handling and diagnostics
- Pattern usage analytics and optimization suggestions
"""

import logging
import re
import signal
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Set, Tuple, Union

from ..exceptions.advanced_folders_exceptions import (PerformanceException,
                                                      SearchException,
                                                      ValidationException)


class PatternType(Enum):
    """Types of regex patterns for different use cases."""
    FILENAME = "filename"
    FILEPATH = "filepath"
    CONTENT = "content"
    EXTENSION = "extension"
    CUSTOM = "custom"


class PatternComplexity(Enum):
    """Pattern complexity levels for performance management."""
    SIMPLE = "simple"          # Basic patterns with minimal backtracking
    MODERATE = "moderate"      # Standard patterns with some complexity
    COMPLEX = "complex"        # Advanced patterns requiring careful handling
    DANGEROUS = "dangerous"    # Potentially problematic patterns


@dataclass
class RegexPattern:
    """Encapsulation of a compiled regex pattern with metadata."""
    
    pattern: str
    compiled: Pattern[str]
    pattern_type: PatternType
    complexity: PatternComplexity
    description: str
    flags: int = 0
    max_execution_time_ms: float = 5000.0
    cache_enabled: bool = True
    created_at: float = field(default_factory=time.time)
    usage_count: int = 0
    total_execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "pattern": self.pattern,
            "pattern_type": self.pattern_type.value,
            "complexity": self.complexity.value,
            "description": self.description,
            "flags": self.flags,
            "max_execution_time_ms": self.max_execution_time_ms,
            "cache_enabled": self.cache_enabled,
            "created_at": self.created_at,
            "usage_count": self.usage_count,
            "total_execution_time_ms": round(self.total_execution_time_ms, 2),
            "avg_execution_time_ms": (
                round(self.total_execution_time_ms / self.usage_count, 2)
                if self.usage_count > 0 else 0.0
            )
        }


@dataclass
class MatchResult:
    """Result of a regex pattern match operation."""
    
    pattern: str
    input_text: str
    matches: List[str]
    groups: List[Tuple[str, ...]]
    positions: List[Tuple[int, int]]
    execution_time_ms: float
    success: bool = True
    error_message: Optional[str] = None
    timeout_occurred: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for analysis."""
        return {
            "pattern": self.pattern,
            "input_length": len(self.input_text),
            "match_count": len(self.matches),
            "execution_time_ms": round(self.execution_time_ms, 2),
            "success": self.success,
            "error_message": self.error_message,
            "timeout_occurred": self.timeout_occurred,
            "matches": self.matches[:10],  # Limit for logging
            "groups": [list(g) for g in self.groups[:10]]
        }


class PatternValidator(ABC):
    """Abstract base class for regex pattern validators."""
    
    @abstractmethod
    def validate(self, pattern: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a regex pattern.
        
        Args:
            pattern: Regex pattern to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def assess_complexity(self, pattern: str) -> PatternComplexity:
        """
        Assess the complexity of a regex pattern.
        
        Args:
            pattern: Regex pattern to assess
            
        Returns:
            PatternComplexity level
        """
        pass


class SecurityPatternValidator(PatternValidator):
    """Validator focused on security and ReDoS prevention."""
    
    def __init__(self):
        """Initialize security validator."""
        self.logger = logging.getLogger('RFU.SecurityPatternValidator')
        
        # Dangerous pattern indicators
        self.redos_patterns = [
            r'\([^)]*\+[^)]*\)\+',  # Nested quantifiers
            r'\([^)]*\*[^)]*\)\*',  # Nested star quantifiers
            r'\([^)]*\+[^)]*\)\*',  # Mixed nested quantifiers
            r'\([^)]*\*[^)]*\)\+',  # Mixed nested quantifiers
            r'\[\^[^\]]*\]\+\*',    # Character class with quantifiers
            r'\[\^[^\]]*\]\*\+',    # Character class with quantifiers
        ]
        
        # Complexity indicators
        self.complexity_indicators = {
            'lookahead': r'\?\=',
            'lookbehind': r'\?\<\=',
            'non_capturing': r'\?\:',
            'backreference': r'\\[1-9]',
            'alternation': r'\|',
            'quantifier': r'[\+\*\?]\??',
            'char_class': r'\[[^\]]+\]',
            'escape': r'\\.',
        }
        
        # Maximum pattern length
        self.max_pattern_length = 1000
    
    def validate(self, pattern: str) -> Tuple[bool, Optional[str]]:
        """Validate pattern for security issues."""
        # Check pattern length
        if len(pattern) > self.max_pattern_length:
            return False, f"Pattern too long: {len(pattern)} > {self.max_pattern_length}"
        
        # Check for dangerous ReDoS patterns
        for redos_pattern in self.redos_patterns:
            if re.search(redos_pattern, pattern):
                return False, f"Potential ReDoS vulnerability detected: {redos_pattern}"
        
        # Test pattern compilation
        try:
            re.compile(pattern)
        except re.error as e:
            return False, f"Invalid regex syntax: {str(e)}"
        
        # Check for excessive quantifiers
        quantifier_count = len(re.findall(r'[\+\*\?]', pattern))
        if quantifier_count > 20:
            return False, f"Too many quantifiers: {quantifier_count} > 20"
        
        # Check for excessive alternations
        alternation_count = pattern.count('|')
        if alternation_count > 50:
            return False, f"Too many alternations: {alternation_count} > 50"
        
        return True, None
    
    def assess_complexity(self, pattern: str) -> PatternComplexity:
        """Assess pattern complexity based on features used."""
        complexity_score = 0
        
        # Count complexity features
        for feature, feature_pattern in self.complexity_indicators.items():
            feature_count = len(re.findall(feature_pattern, pattern))
            
            if feature in ['lookahead', 'lookbehind', 'backreference']:
                complexity_score += feature_count * 3
            elif feature in ['alternation', 'quantifier']:
                complexity_score += feature_count * 2
            else:
                complexity_score += feature_count
        
        # Additional complexity factors
        if len(pattern) > 200:
            complexity_score += 5
        
        # Check for nested groups
        group_depth = self._calculate_group_depth(pattern)
        complexity_score += group_depth * 2
        
        # Determine complexity level
        if complexity_score <= 10:
            return PatternComplexity.SIMPLE
        elif complexity_score <= 25:
            return PatternComplexity.MODERATE
        elif complexity_score <= 50:
            return PatternComplexity.COMPLEX
        else:
            return PatternComplexity.DANGEROUS
    
    def _calculate_group_depth(self, pattern: str) -> int:
        """Calculate maximum nesting depth of groups."""
        max_depth = 0
        current_depth = 0
        
        i = 0
        while i < len(pattern):
            if pattern[i] == '\\':
                i += 2  # Skip escaped character
                continue
            elif pattern[i] == '(':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif pattern[i] == ')':
                current_depth = max(0, current_depth - 1)
            i += 1
        
        return max_depth


class PerformancePatternValidator(PatternValidator):
    """Validator focused on performance characteristics."""
    
    def __init__(self):
        """Initialize performance validator."""
        self.logger = logging.getLogger('RFU.PerformancePatternValidator')
        
        # Performance test patterns
        self.test_strings = [
            "a" * 1000,  # Long simple string
            "ab" * 500,  # Alternating pattern
            "test_file_name_with_many_parts.txt",  # Typical filename
            "/very/long/path/with/many/components/file.ext",  # Long path
            "x" * 100 + "y",  # Potential backtracking case
        ]
        
        # Performance thresholds
        self.max_test_time_ms = 100.0
        self.max_backtrack_steps = 10000
    
    def validate(self, pattern: str) -> Tuple[bool, Optional[str]]:
        """Validate pattern performance characteristics."""
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            return False, f"Pattern compilation failed: {str(e)}"
        
        # Test pattern against various inputs
        for test_string in self.test_strings:
            start_time = time.time()
            
            try:
                # Use timeout to prevent hanging
                with TimeoutContext(self.max_test_time_ms / 1000.0):
                    compiled_pattern.search(test_string)
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                if execution_time_ms > self.max_test_time_ms:
                    return False, (
                        f"Pattern too slow: {execution_time_ms:.2f}ms > "
                        f"{self.max_test_time_ms}ms"
                    )
                    
            except TimeoutError:
                return False, f"Pattern timed out during validation"
            except Exception as e:
                return False, f"Pattern execution error: {str(e)}"
        
        return True, None
    
    def assess_complexity(self, pattern: str) -> PatternComplexity:
        """Assess complexity based on performance testing."""
        try:
            compiled_pattern = re.compile(pattern)
            total_time = 0.0
            
            for test_string in self.test_strings:
                start_time = time.time()
                try:
                    with TimeoutContext(0.01):  # 10ms timeout
                        compiled_pattern.search(test_string)
                    total_time += (time.time() - start_time) * 1000
                except TimeoutError:
                    return PatternComplexity.DANGEROUS
                except Exception:
                    return PatternComplexity.COMPLEX
            
            avg_time = total_time / len(self.test_strings)
            
            if avg_time < 1.0:
                return PatternComplexity.SIMPLE
            elif avg_time < 5.0:
                return PatternComplexity.MODERATE
            elif avg_time < 20.0:
                return PatternComplexity.COMPLEX
            else:
                return PatternComplexity.DANGEROUS
                
        except Exception:
            return PatternComplexity.COMPLEX


class TimeoutContext:
    """Context manager for operation timeouts."""
    
    def __init__(self, timeout_seconds: float):
        """Initialize timeout context."""
        self.timeout_seconds = timeout_seconds
        self.old_handler = None
    
    def __enter__(self):
        """Enter timeout context."""
        if hasattr(signal, 'SIGALRM'):  # Unix-like systems
            self.old_handler = signal.signal(
                signal.SIGALRM, self._timeout_handler
            )
            signal.alarm(int(self.timeout_seconds))
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit timeout context."""
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
            if self.old_handler:
                signal.signal(signal.SIGALRM, self.old_handler)
    
    def _timeout_handler(self, signum, frame):
        """Handle timeout signal."""
        raise TimeoutError("Operation timed out")


class RegexPatternManager:
    """
    Enterprise regex pattern manager with validation and optimization.
    """
    
    def __init__(self, cache_size: int = 1000):
        """
        Initialize regex pattern manager.
        
        Args:
            cache_size: Maximum number of compiled patterns to cache
        """
        self.cache_size = cache_size
        
        # Pattern cache
        self._pattern_cache: Dict[str, RegexPattern] = {}
        self._cache_lock = threading.RLock()
        
        # Validators
        self.validators = [
            SecurityPatternValidator(),
            PerformancePatternValidator()
        ]
        
        # Pre-defined pattern library
        self.pattern_library = self._init_pattern_library()
        
        # Usage statistics
        self.usage_stats = {
            'patterns_compiled': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'validation_failures': 0,
            'execution_timeouts': 0
        }
        
        self.logger = logging.getLogger('RFU.RegexPatternManager')
        self.logger.info("Regex pattern manager initialized")
    
    def _init_pattern_library(self) -> Dict[str, str]:
        """Initialize library of common useful patterns."""
        return {
            # File extension patterns
            'image_files': r'\.(jpg|jpeg|png|gif|bmp|tiff|webp)$',
            'document_files': r'\.(pdf|doc|docx|txt|rtf|odt)$',
            'code_files': r'\.(py|js|html|css|cpp|c|h|java|cs)$',
            'archive_files': r'\.(zip|rar|7z|tar|gz|bz2)$',
            
            # Filename patterns
            'version_numbers': r'v?\d+\.\d+(\.\d+)?',
            'date_in_filename': r'\d{4}[-_]\d{2}[-_]\d{2}',
            'backup_files': r'\.bak$|_backup$|~$',
            'temp_files': r'\.tmp$|\.temp$|^~.*',
            
            # Path patterns
            'windows_path': r'^[A-Za-z]:\\',
            'unix_path': r'^/',
            'relative_path': r'^\.\.?/',
            'hidden_files': r'/\.[^/]+$',
            
            # Content patterns
            'email_addresses': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ip_addresses': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'urls': r'https?://[^\s]+',
            'phone_numbers': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            
            # Programming patterns
            'function_definitions': r'def\s+\w+\s*\(',
            'class_definitions': r'class\s+\w+\s*[:\(]',
            'import_statements': r'^(import|from)\s+\w+',
            'comments': r'#.*$|//.*$|/\*.*?\*/',
        }
    
    def compile_pattern(
        self,
        pattern: str,
        pattern_type: PatternType = PatternType.CUSTOM,
        flags: int = 0,
        description: str = "",
        max_execution_time_ms: float = 5000.0
    ) -> RegexPattern:
        """
        Compile and validate a regex pattern.
        
        Args:
            pattern: Regex pattern string
            pattern_type: Type classification for the pattern
            flags: Regex compilation flags
            description: Human-readable description
            max_execution_time_ms: Maximum execution time allowed
            
        Returns:
            Compiled RegexPattern object
            
        Raises:
            ValidationException: If pattern validation fails
        """
        cache_key = f"{pattern}:{flags}"
        
        # Check cache first
        with self._cache_lock:
            if cache_key in self._pattern_cache:
                self.usage_stats['cache_hits'] += 1
                return self._pattern_cache[cache_key]
        
        self.usage_stats['cache_misses'] += 1
        
        # Validate pattern
        for validator in self.validators:
            is_valid, error_message = validator.validate(pattern)
            if not is_valid:
                self.usage_stats['validation_failures'] += 1
                raise ValidationException(
                    f"Pattern validation failed: {error_message}",
                    field_name="regex_pattern",
                    field_value=pattern,
                    validation_rule="regex_security"
                )
        
        # Assess complexity
        complexity = PatternComplexity.SIMPLE
        for validator in self.validators:
            validator_complexity = validator.assess_complexity(pattern)
            if validator_complexity.value > complexity.value:
                complexity = validator_complexity
        
        # Compile pattern
        try:
            compiled = re.compile(pattern, flags)
        except re.error as e:
            raise ValidationException(
                f"Regex compilation failed: {str(e)}",
                field_name="regex_pattern",
                field_value=pattern,
                validation_rule="regex_syntax"
            )
        
        # Create RegexPattern object
        regex_pattern = RegexPattern(
            pattern=pattern,
            compiled=compiled,
            pattern_type=pattern_type,
            complexity=complexity,
            description=description or f"Custom {pattern_type.value} pattern",
            flags=flags,
            max_execution_time_ms=max_execution_time_ms
        )
        
        # Cache the pattern
        with self._cache_lock:
            if len(self._pattern_cache) >= self.cache_size:
                # Remove least recently used pattern
                oldest_key = min(
                    self._pattern_cache.keys(),
                    key=lambda k: self._pattern_cache[k].created_at
                )
                del self._pattern_cache[oldest_key]
            
            self._pattern_cache[cache_key] = regex_pattern
        
        self.usage_stats['patterns_compiled'] += 1
        self.logger.debug(
            f"Compiled pattern: {pattern[:50]}... "
            f"(complexity: {complexity.value})"
        )
        
        return regex_pattern
    
    def match(
        self,
        pattern: Union[str, RegexPattern],
        text: str,
        timeout_ms: Optional[float] = None
    ) -> MatchResult:
        """
        Execute pattern match with timeout protection.
        
        Args:
            pattern: Pattern string or compiled RegexPattern
            text: Text to search
            timeout_ms: Optional timeout override
            
        Returns:
            MatchResult with match details and performance metrics
        """
        start_time = time.time()
        
        # Get RegexPattern object
        if isinstance(pattern, str):
            regex_pattern = self.compile_pattern(pattern)
        else:
            regex_pattern = pattern
        
        # Determine timeout
        timeout_seconds = (
            (timeout_ms or regex_pattern.max_execution_time_ms) / 1000.0
        )
        
        try:
            matches = []
            groups = []
            positions = []
            
            # Execute with timeout protection
            with TimeoutContext(timeout_seconds):
                for match in regex_pattern.compiled.finditer(text):
                    matches.append(match.group(0))
                    groups.append(match.groups())
                    positions.append(match.span())
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Update pattern statistics
            regex_pattern.usage_count += 1
            regex_pattern.total_execution_time_ms += execution_time_ms
            
            return MatchResult(
                pattern=regex_pattern.pattern,
                input_text=text,
                matches=matches,
                groups=groups,
                positions=positions,
                execution_time_ms=execution_time_ms,
                success=True
            )
            
        except TimeoutError:
            execution_time_ms = (time.time() - start_time) * 1000
            self.usage_stats['execution_timeouts'] += 1
            
            self.logger.warning(
                f"Pattern execution timed out: {regex_pattern.pattern[:50]}..."
            )
            
            return MatchResult(
                pattern=regex_pattern.pattern,
                input_text=text,
                matches=[],
                groups=[],
                positions=[],
                execution_time_ms=execution_time_ms,
                success=False,
                error_message="Pattern execution timed out",
                timeout_occurred=True
            )
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            
            return MatchResult(
                pattern=regex_pattern.pattern,
                input_text=text,
                matches=[],
                groups=[],
                positions=[],
                execution_time_ms=execution_time_ms,
                success=False,
                error_message=str(e)
            )
    
    def search_files(
        self,
        file_paths: List[str],
        pattern: Union[str, RegexPattern],
        search_content: bool = False,
        max_workers: int = 4
    ) -> Dict[str, MatchResult]:
        """
        Search multiple files using regex pattern.
        
        Args:
            file_paths: List of file paths to search
            pattern: Pattern to search for
            search_content: Whether to search file content or just names
            max_workers: Maximum worker threads
            
        Returns:
            Dictionary mapping file paths to match results
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {}
        
        # Get RegexPattern object
        if isinstance(pattern, str):
            regex_pattern = self.compile_pattern(
                pattern, PatternType.FILENAME if not search_content 
                else PatternType.CONTENT
            )
        else:
            regex_pattern = pattern
        
        def search_file(file_path: str) -> Tuple[str, MatchResult]:
            """Search a single file."""
            try:
                if search_content:
                    # Search file content
                    try:
                        with open(file_path, 'r', encoding='utf-8', 
                                 errors='ignore') as f:
                            content = f.read(100000)  # Limit content size
                        search_text = content
                    except Exception as e:
                        return file_path, MatchResult(
                            pattern=regex_pattern.pattern,
                            input_text="",
                            matches=[],
                            groups=[],
                            positions=[],
                            execution_time_ms=0.0,
                            success=False,
                            error_message=f"Failed to read file: {str(e)}"
                        )
                else:
                    # Search filename only
                    search_text = Path(file_path).name
                
                result = self.match(regex_pattern, search_text)
                return file_path, result
                
            except Exception as e:
                return file_path, MatchResult(
                    pattern=regex_pattern.pattern,
                    input_text="",
                    matches=[],
                    groups=[],
                    positions=[],
                    execution_time_ms=0.0,
                    success=False,
                    error_message=str(e)
                )
        
        # Execute searches concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(search_file, file_path): file_path
                for file_path in file_paths
            }
            
            for future in as_completed(future_to_file):
                file_path, result = future.result()
                results[file_path] = result
        
        return results
    
    def get_pattern_library(self) -> Dict[str, str]:
        """Get the built-in pattern library."""
        return self.pattern_library.copy()
    
    def add_library_pattern(self, name: str, pattern: str) -> None:
        """
        Add a pattern to the library.
        
        Args:
            name: Pattern name
            pattern: Regex pattern string
        """
        # Validate pattern first
        self.compile_pattern(pattern, description=f"Library pattern: {name}")
        self.pattern_library[name] = pattern
        
        self.logger.info(f"Added pattern to library: {name}")
    
    def get_pattern_from_library(self, name: str) -> Optional[str]:
        """
        Get a pattern from the library by name.
        
        Args:
            name: Pattern name
            
        Returns:
            Pattern string or None if not found
        """
        return self.pattern_library.get(name)
    
    def optimize_pattern(self, pattern: str) -> Tuple[str, List[str]]:
        """
        Suggest optimizations for a regex pattern.
        
        Args:
            pattern: Pattern to optimize
            
        Returns:
            Tuple of (optimized_pattern, optimization_suggestions)
        """
        suggestions = []
        optimized = pattern
        
        # Common optimizations
        optimizations = [
            # Replace .* with more specific patterns when possible
            (r'\.\*', '[^/]*', "Replace .* with [^/]* for path matching"),
            
            # Use non-capturing groups when capture isn't needed
            (r'\(([^|)]+)\)', r'(?:\1)', "Use non-capturing groups when possible"),
            
            # Anchor patterns when appropriate
            (r'^(.+)$', r'\1', "Remove unnecessary anchors"),
            
            # Simplify character classes
            (r'\[a-zA-Z\]', r'[a-zA-Z]', "Simplify character classes"),
        ]
        
        for old_pattern, new_pattern, suggestion in optimizations:
            if re.search(old_pattern, optimized):
                optimized = re.sub(old_pattern, new_pattern, optimized)
                suggestions.append(suggestion)
        
        return optimized, suggestions
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get pattern manager statistics."""
        stats = self.usage_stats.copy()
        
        # Cache statistics
        with self._cache_lock:
            stats['cache_size'] = len(self._pattern_cache)
            stats['cache_utilization'] = (
                len(self._pattern_cache) / self.cache_size
            )
            
            # Pattern complexity distribution
            complexity_counts = {}
            for pattern in self._pattern_cache.values():
                complexity = pattern.complexity.value
                complexity_counts[complexity] = (
                    complexity_counts.get(complexity, 0) + 1
                )
            stats['complexity_distribution'] = complexity_counts
            
            # Average execution times by complexity
            complexity_times = {}
            for pattern in self._pattern_cache.values():
                if pattern.usage_count > 0:
                    complexity = pattern.complexity.value
                    avg_time = (
                        pattern.total_execution_time_ms / pattern.usage_count
                    )
                    if complexity not in complexity_times:
                        complexity_times[complexity] = []
                    complexity_times[complexity].append(avg_time)
            
            for complexity, times in complexity_times.items():
                stats[f'avg_time_{complexity}_ms'] = (
                    round(sum(times) / len(times), 2) if times else 0.0
                )
        
        # Library statistics
        stats['library_patterns'] = len(self.pattern_library)
        
        # Cache hit ratio
        total_requests = stats['cache_hits'] + stats['cache_misses']
        if total_requests > 0:
            stats['cache_hit_ratio'] = (
                round(stats['cache_hits'] / total_requests, 3)
            )
        else:
            stats['cache_hit_ratio'] = 0.0
        
        return stats
    
    def clear_cache(self) -> None:
        """Clear the pattern cache."""
        with self._cache_lock:
            self._pattern_cache.clear()
        
        self.logger.info("Pattern cache cleared")
    
    def validate_pattern_security(self, pattern: str) -> Dict[str, Any]:
        """
        Comprehensive security validation for a pattern.
        
        Args:
            pattern: Pattern to validate
            
        Returns:
            Validation report with security assessment
        """
        report = {
            'pattern': pattern,
            'is_safe': True,
            'risk_level': 'low',
            'issues': [],
            'recommendations': []
        }
        
        # Run all validators
        for validator in self.validators:
            is_valid, error_message = validator.validate(pattern)
            
            if not is_valid:
                report['is_safe'] = False
                report['issues'].append({
                    'validator': validator.__class__.__name__,
                    'issue': error_message
                })
            
            complexity = validator.assess_complexity(pattern)
            if complexity in [PatternComplexity.COMPLEX, 
                             PatternComplexity.DANGEROUS]:
                report['risk_level'] = complexity.value
                if complexity == PatternComplexity.DANGEROUS:
                    report['is_safe'] = False
        
        # Generate recommendations
        if not report['is_safe']:
            report['recommendations'].extend([
                "Consider simplifying the pattern to reduce complexity",
                "Test the pattern thoroughly with various inputs",
                "Consider using alternative matching approaches"
            ])
        
        return report