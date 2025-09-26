V Mt Phase2_Theme_Security_Specification_Complete.md RFU_Hub_Preferences_Security_Implementation_Plan
CodeRabbit . Missing imports & undefined symbols render sample code non-executable [Ln 90-102]
CodeRabbit . Sanitisation drops unprocessed keys - potential silent data loss [Ln 285-306]
CodeRabbit . SecureThemeSettingsWidget references undefined self.logger [Ln 364-371]
CodeRabbit . Cache metadata counters never increase [Ln 556-574]
CodeRabbit . _evict_oldest_entry may leak metadata [Ln 600-606]
V Mt Phase3_Directory_Security_Complete.md RFU_Hub_Preferences_Security_Implementation_Plan
CodeRabbit . Integrity-check & decryption flow contains multiple security gaps [Ln 6-51]
CodeRabbit . Key-derivation parameters are underspecified & may be weak [Ln 53-67]
CodeRabbit . Missing import and predictable HMAC key [Ln 69-80]
CodeRabbit . Undefined helper methods break permission checking [Ln 141-170]
CodeRabbit . Expiration path invokes non-existent_expire_permission [Ln 298-321]
CodeRabbit . show_security_violation_dialog implementation is truncated [Ln 821-828]
M+ Phase3_Directory_Security_Specification.md RFU_Hub_Preferences_Security_Implementation_Plan
CodeRabbit . Undefined classes referenced in _init
CodeRabbit . Helper methods are not specified
CodeRabbit . Missing _get_encrypted_directory implementation
CodeRabbit . Undefined validation API
CodeRabbit . Traversal validation needs consolidation [Ln 350-381]
CodeRabbit . Undeclared cryptographic helpers
CodeRabbit . decrypt_directory_path definition incomplete
V M+ RFU_Hub_Preferences_Security_Implementation_Plan.md RFU_Hub_Preferences_Security_Implementation_Plan
CodeRabbit . Encryption algorithm definition contradicts the code snippet
v M+ RFU_Hub_Security_Implementation_Summary.md RFU_Hub_Preferences_Security_Implementation_Plan
CodeRabbit . Replace PBKDF2-HMAC with Argon2id or significantly increase iteration count
CodeRabbit . Specify log-signature algorithm and key custody
man.py
CodeRabbit . Race condition in track_tool_usage method [Ln 115-144]
database_manager.py src\rfu\core
CodeRabbit . Reconsider UNIQUE constraint on file_path. [Ln 153-154]
CodeRabbit . Avoid silently swallowing exceptions. [Ln 376-386]
CodeRabbit . Add validation for retention settings. [Ln 512-513]
CodeRabbit . Avoid relying on del for cleanup. [Ln 629-635]
database_models.py src\rfu\core
CodeRabbit . Include timestamp field in to_dict() method. [Ln 103-115]
CodeRabbit . Include timestamp fields in to_dict() method. [Ln 163-172]
enhanced_config_manager.py src\rfu\core
CodeRabbit . Fix migration logic - missing file existence check. [Ln 69-74]
CodeRabbit . Potential AttributeError when checking file existence. [Ln 89-92]
CodeRabbit . Potential undefined variable access in migration. [Ln 179-207]
CodeRabbit . Consider failing fast on migration errors. [Ln 192-200]
CodeRabbit . Potential infinite recursion when setting auto_save_config. [Ln 306-330]
log_manager.py src\rfu\core
CodeRabbit . Critical issue: Redundant import inside method causes potential issues. [Ln 91-105]
migration_base.py src\rfu\core\migrations
CodeRabbit . Security issue in checksum generation [Ln 155-172]
migration_manager.py src\rfu\core\migrations
CodeRabbit . Potential infinite recursion in acquire lock method [Ln 32-80]
CodeRabbit . Inconsistent timestamp handling [Ln 44-56]
CodeRabbit . Database connection not properly managed in_initialize_migration_tables [Ln 132-202]
CodeRabbit . Incomplete implementation of _get_pending_migrations [Ln 434-447]
migration_001_initial_schema.py src\rfu\core\migrations\migrations
CodeRabbit . Add CHECK constraint for value_type column [Ln 31-45]
CodeRabbit . Validate all expected indexes, not just count [Ln 144-148]
? migration_002_add_encryption_support.py src\rfu\core\migrations\migrations
CodeRabbit . Migration history table assumed to exist without validation [Ln 193-201]
rollback_manager.py src\rfu\core\migrations 
CodeRabbit . Incomplete rollback implementation [Ln 440-449]
schema_validator.py src\rfu\core\migrations
CodeRabbit . Hardcoded required tables may not match actual schema [Ln 51-60]
CodeRabbit . Validation queries reference non-existent tables [Ln 195-209]
CodeRabbit . Timestamp validation assumes updated at column exists [Ln 451-463]
theme_encryption.py src\rfu\core\theme_security
I CodeRabbit . Incorrect encryption algorithm documentation [Ln 2-6]
I CodeRabbit . Missing datetime import [Ln 8-20]
I CodeRabbit . Inconsistent key generation between keyring and file-based storage [Ln 92-111]
CodeRabbit . Fix key length validation [Ln 286-288]
security_preferences_dialog.py src\rfu\gui
I CodeRabbit . Fragile path manipulation for imports [Ln 21-22]
CodeRabbit . Silent failure in status check methods [Ln 951-962]
bookmark_manager.py src\utilities\network
I CodeRabbit . Improve error handling beyond console printing [Ln 111-112]
CodeRabbit . Add URL validation for security [Ln 181-192]
CodeRabbit . Add defensive programming for CSV export [Ln 493-499]
I CodeRabbit . Potential date parsing issue [Ln 788-789]
CodeRabbit . Provide feedback on skipped bookmarks during import [Ln 924-928]
network_transfer.py src\utilities\network
CodeRabbit . Unused SSL import [Ln 22]
CodeRabbit . Critical security issue: XOR encryption is not suitable for production [Ln 91-99]
I CodeRabbit . SecurityManager is not used for authentication or encryption [Ln 202]
CodeRabbit . Security: No authentication or encryption [Ln 250-262]
I CodeRabbit . File descriptor becomes invalid after context manager exits [Ln 355-369]
CodeRabbit . Inefficient hex encoding doubles network traffic [Ln 446-450]
CodeRabbit . Path traversal in file selection [Ln 914-915]
CodeRabbit . Ensure robust, case-insensitive path normalization on Windows [Ln 957-983]
CodeRabbit . Add recursion depth limit to prevent stack overflow [Ln 1116-1143]
standalone_database_manager.py
I CodeRabbit . Avoid string interpolation in SQL queries. [Ln 265-267]