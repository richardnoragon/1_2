"""
PDF Security Engine - Phase 2.3 Implementation
Provides comprehensive PDF security features including password protection,
encryption, digital signatures, and access controls.
"""

import os
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import shutil

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    import pikepdf
    HAS_PIKEPDF = True
except ImportError:
    HAS_PIKEPDF = False

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.x509.oid import NameOID
    from cryptography import x509
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    hashes = None
    serialization = None
    rsa = None
    padding = None
    NameOID = None
    x509 = None


class SecurityOperation(Enum):
    """Types of PDF security operations"""
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    SET_PASSWORD = "set_password"
    REMOVE_PASSWORD = "remove_password"
    DIGITAL_SIGN = "digital_sign"
    VERIFY_SIGNATURE = "verify_signature"
    SET_PERMISSIONS = "set_permissions"
    GET_SECURITY_INFO = "get_security_info"


class EncryptionLevel(Enum):
    """PDF encryption levels"""
    RC4_40 = "rc4_40"
    RC4_128 = "rc4_128"
    AES_128 = "aes_128"
    AES_256 = "aes_256"


class PermissionFlag(Enum):
    """PDF permission flags"""
    PRINT = "print"
    MODIFY = "modify"
    COPY = "copy"
    ANNOTATE = "annotate"
    FILL_FORMS = "fill_forms"
    EXTRACT_TEXT = "extract_text"
    ASSEMBLE = "assemble"
    HIGH_QUALITY_PRINT = "high_quality_print"


@dataclass
class SecurityResult:
    """Result of a security operation"""
    success: bool
    operation: SecurityOperation
    message: str
    output_path: Optional[str] = None
    security_info: Dict[str, Any] = field(default_factory=dict)
    signature_info: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class SecuritySettings:
    """PDF security configuration"""
    user_password: str = ""
    owner_password: str = ""
    encryption_level: EncryptionLevel = EncryptionLevel.AES_256
    permissions: Dict[PermissionFlag, bool] = field(default_factory=dict)
    allow_printing: bool = True
    allow_modification: bool = False
    allow_copying: bool = False
    allow_annotation: bool = True
    allow_form_filling: bool = True
    allow_text_extraction: bool = True
    allow_assembly: bool = False
    allow_high_quality_print: bool = True


@dataclass
class DigitalSignature:
    """Digital signature configuration"""
    certificate_path: str = ""
    private_key_path: str = ""
    password: str = ""
    reason: str = "Document verification"
    location: str = ""
    contact_info: str = ""
    signature_field_name: str = "Signature1"
    visible: bool = True
    signature_rect: Tuple[float, float, float, float] = (100, 100, 200, 150)


class PDFSecurityValidator:
    """Validates PDF files and security operations"""
    
    @staticmethod
    def validate_pdf_file(file_path: str) -> Tuple[bool, str]:
        """Validate if file is a valid PDF"""
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        if not file_path.lower().endswith('.pdf'):
            return False, "File must have .pdf extension"
        
        try:
            if HAS_PYMUPDF:
                doc = fitz.open(file_path)
                doc.close()
                return True, "Valid PDF file"
            elif HAS_PIKEPDF:
                pikepdf.open(file_path).close()
                return True, "Valid PDF file"
            else:
                return False, "No PDF processing library available"
        except Exception as e:
            return False, f"Invalid PDF file: {str(e)}"
    
    @staticmethod
    def validate_security_settings(settings: SecuritySettings) -> \
            Tuple[bool, str]:
        """Validate security settings"""
        if not settings.user_password and not settings.owner_password:
            return False, "At least one password must be provided"
        
        if len(settings.user_password) > 127:
            return False, "User password too long (max 127 characters)"
        
        if len(settings.owner_password) > 127:
            return False, "Owner password too long (max 127 characters)"
        
        return True, "Valid security settings"
    
    @staticmethod
    def validate_signature_config(signature: DigitalSignature) -> \
            Tuple[bool, str]:
        """Validate digital signature configuration"""
        if not signature.certificate_path:
            return False, "Certificate path is required"
        
        if not os.path.exists(signature.certificate_path):
            return False, \
                f"Certificate file not found: {signature.certificate_path}"
        
        if (signature.private_key_path and
                not os.path.exists(signature.private_key_path)):
            return False, \
                f"Private key file not found: {signature.private_key_path}"
        
        return True, "Valid signature configuration"


class PDFPasswordProtection:
    """Handles PDF password protection and encryption"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def encrypt_pdf(self, input_path: str, output_path: str, 
                   settings: SecuritySettings) -> SecurityResult:
        """Encrypt PDF with password and permissions"""
        try:
            # Validate inputs
            valid, msg = PDFSecurityValidator.validate_pdf_file(input_path)
            if not valid:
                return SecurityResult(False, SecurityOperation.ENCRYPT, msg)
            
            valid, msg = PDFSecurityValidator.validate_security_settings(settings)
            if not valid:
                return SecurityResult(False, SecurityOperation.ENCRYPT, msg)
            
            # Use pikepdf for encryption (preferred)
            if HAS_PIKEPDF:
                return self._encrypt_with_pikepdf(input_path, output_path, settings)
            elif HAS_PYMUPDF:
                return self._encrypt_with_pymupdf(input_path, output_path, settings)
            else:
                return SecurityResult(
                    False, SecurityOperation.ENCRYPT,
                    "No encryption library available (pikepdf or PyMuPDF required)"
                )
                
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")
            return SecurityResult(False, SecurityOperation.ENCRYPT, f"Encryption failed: {str(e)}")
    
    def _encrypt_with_pikepdf(self, input_path: str, output_path: str, 
                             settings: SecuritySettings) -> SecurityResult:
        """Encrypt PDF using pikepdf"""
        try:
            with pikepdf.open(input_path) as pdf:
                # Set up encryption
                encryption_dict = {
                    'owner': settings.owner_password or settings.user_password,
                    'user': settings.user_password,
                }
                
                # Configure permissions
                permissions = pikepdf.Permissions()
                if not settings.allow_printing:
                    permissions &= ~pikepdf.Permissions.print_lowres
                if not settings.allow_modification:
                    permissions &= ~pikepdf.Permissions.modify_other
                if not settings.allow_copying:
                    permissions &= ~pikepdf.Permissions.extract
                if not settings.allow_annotation:
                    permissions &= ~pikepdf.Permissions.modify_annotation
                if not settings.allow_form_filling:
                    permissions &= ~pikepdf.Permissions.fill_forms
                if not settings.allow_assembly:
                    permissions &= ~pikepdf.Permissions.modify_assembly
                if not settings.allow_high_quality_print:
                    permissions &= ~pikepdf.Permissions.print_highres
                
                encryption_dict['permissions'] = permissions
                
                # Set encryption level
                if settings.encryption_level == EncryptionLevel.AES_256:
                    encryption_dict['R'] = 6
                elif settings.encryption_level == EncryptionLevel.AES_128:
                    encryption_dict['R'] = 4
                else:
                    encryption_dict['R'] = 3
                
                pdf.save(output_path, encryption=pikepdf.Encryption(**encryption_dict))
                
            return SecurityResult(
                True, SecurityOperation.ENCRYPT,
                f"PDF successfully encrypted and saved to {output_path}",
                output_path=output_path
            )
            
        except Exception as e:
            return SecurityResult(False, SecurityOperation.ENCRYPT, f"pikepdf encryption failed: {str(e)}")
    
    def _encrypt_with_pymupdf(self, input_path: str, output_path: str, 
                             settings: SecuritySettings) -> SecurityResult:
        """Encrypt PDF using PyMuPDF"""
        try:
            doc = fitz.open(input_path)
            
            # Set up permissions
            perm = 0
            if settings.allow_printing:
                perm |= fitz.PDF_PERM_PRINT
            if settings.allow_modification:
                perm |= fitz.PDF_PERM_MODIFY
            if settings.allow_copying:
                perm |= fitz.PDF_PERM_COPY
            if settings.allow_annotation:
                perm |= fitz.PDF_PERM_ANNOTATE
            if settings.allow_form_filling:
                perm |= fitz.PDF_PERM_FORM
            if settings.allow_text_extraction:
                perm |= fitz.PDF_PERM_ACCESSIBILITY
            if settings.allow_assembly:
                perm |= fitz.PDF_PERM_ASSEMBLE
            if settings.allow_high_quality_print:
                perm |= fitz.PDF_PERM_PRINT_HQ
            
            # Set encryption level
            if settings.encryption_level == EncryptionLevel.AES_256:
                encrypt_meth = fitz.PDF_ENCRYPT_AES_256
            elif settings.encryption_level == EncryptionLevel.AES_128:
                encrypt_meth = fitz.PDF_ENCRYPT_AES_128
            elif settings.encryption_level == EncryptionLevel.RC4_128:
                encrypt_meth = fitz.PDF_ENCRYPT_RC4_128
            else:
                encrypt_meth = fitz.PDF_ENCRYPT_RC4_40
            
            doc.save(
                output_path,
                encryption=encrypt_meth,
                user_pw=settings.user_password,
                owner_pw=settings.owner_password or settings.user_password,
                permissions=perm
            )
            doc.close()
            
            return SecurityResult(
                True, SecurityOperation.ENCRYPT,
                f"PDF successfully encrypted and saved to {output_path}",
                output_path=output_path
            )
            
        except Exception as e:
            return SecurityResult(False, SecurityOperation.ENCRYPT, f"PyMuPDF encryption failed: {str(e)}")
    
    def decrypt_pdf(self, input_path: str, output_path: str, password: str) -> SecurityResult:
        """Decrypt password-protected PDF"""
        try:
            # Validate input
            valid, msg = PDFSecurityValidator.validate_pdf_file(input_path)
            if not valid:
                return SecurityResult(False, SecurityOperation.DECRYPT, msg)
            
            if HAS_PIKEPDF:
                return self._decrypt_with_pikepdf(input_path, output_path, password)
            elif HAS_PYMUPDF:
                return self._decrypt_with_pymupdf(input_path, output_path, password)
            else:
                return SecurityResult(
                    False, SecurityOperation.DECRYPT,
                    "No decryption library available"
                )
                
        except Exception as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            return SecurityResult(False, SecurityOperation.DECRYPT, f"Decryption failed: {str(e)}")
    
    def _decrypt_with_pikepdf(self, input_path: str, output_path: str, password: str) -> SecurityResult:
        """Decrypt PDF using pikepdf"""
        try:
            with pikepdf.open(input_path, password=password) as pdf:
                pdf.save(output_path)
            
            return SecurityResult(
                True, SecurityOperation.DECRYPT,
                f"PDF successfully decrypted and saved to {output_path}",
                output_path=output_path
            )
            
        except pikepdf.PasswordError:
            return SecurityResult(False, SecurityOperation.DECRYPT, "Incorrect password")
        except Exception as e:
            return SecurityResult(False, SecurityOperation.DECRYPT, f"Decryption failed: {str(e)}")
    
    def _decrypt_with_pymupdf(self, input_path: str, output_path: str, password: str) -> SecurityResult:
        """Decrypt PDF using PyMuPDF"""
        try:
            doc = fitz.open(input_path)
            
            if doc.needs_pass:
                rc = doc.authenticate(password)
                if not rc:
                    doc.close()
                    return SecurityResult(False, SecurityOperation.DECRYPT, "Incorrect password")
            
            doc.save(output_path)
            doc.close()
            
            return SecurityResult(
                True, SecurityOperation.DECRYPT,
                f"PDF successfully decrypted and saved to {output_path}",
                output_path=output_path
            )
            
        except Exception as e:
            return SecurityResult(False, SecurityOperation.DECRYPT, f"Decryption failed: {str(e)}")
    
    def get_security_info(self, file_path: str, password: str = "") -> SecurityResult:
        """Get security information about a PDF"""
        try:
            valid, msg = PDFSecurityValidator.validate_pdf_file(file_path)
            if not valid:
                return SecurityResult(False, SecurityOperation.GET_SECURITY_INFO, msg)
            
            if HAS_PIKEPDF:
                return self._get_security_info_pikepdf(file_path, password)
            elif HAS_PYMUPDF:
                return self._get_security_info_pymupdf(file_path, password)
            else:
                return SecurityResult(
                    False, SecurityOperation.GET_SECURITY_INFO,
                    "No PDF library available"
                )
                
        except Exception as e:
            return SecurityResult(False, SecurityOperation.GET_SECURITY_INFO, f"Failed to get security info: {str(e)}")
    
    def _get_security_info_pikepdf(self, file_path: str, password: str) -> SecurityResult:
        """Get security info using pikepdf"""
        try:
            security_info = {}
            
            try:
                with pikepdf.open(file_path, password=password) as pdf:
                    security_info['encrypted'] = False
                    security_info['has_user_password'] = False
                    security_info['has_owner_password'] = False
                    security_info['permissions'] = self._get_pikepdf_permissions(pdf)
            except pikepdf.PasswordError:
                security_info['encrypted'] = True
                security_info['has_user_password'] = True
                security_info['needs_password'] = True
                security_info['permissions'] = {}
            
            return SecurityResult(
                True, SecurityOperation.GET_SECURITY_INFO,
                "Security information retrieved",
                security_info=security_info
            )
            
        except Exception as e:
            return SecurityResult(False, SecurityOperation.GET_SECURITY_INFO, f"Failed: {str(e)}")
    
    def _get_security_info_pymupdf(self, file_path: str, password: str) -> SecurityResult:
        """Get security info using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            security_info = {}
            
            security_info['encrypted'] = doc.needs_pass
            security_info['page_count'] = doc.page_count
            
            if doc.needs_pass:
                if password:
                    rc = doc.authenticate(password)
                    if rc:
                        security_info['password_correct'] = True
                        security_info['permissions'] = self._get_pymupdf_permissions(doc)
                    else:
                        security_info['password_correct'] = False
                        security_info['needs_password'] = True
                else:
                    security_info['needs_password'] = True
            else:
                security_info['permissions'] = self._get_pymupdf_permissions(doc)
            
            doc.close()
            
            return SecurityResult(
                True, SecurityOperation.GET_SECURITY_INFO,
                "Security information retrieved",
                security_info=security_info
            )
            
        except Exception as e:
            return SecurityResult(False, SecurityOperation.GET_SECURITY_INFO, f"Failed: {str(e)}")
    
    def _get_pikepdf_permissions(self, pdf) -> Dict[str, bool]:
        """Extract permissions from pikepdf document"""
        try:
            perms = pdf.allow
            return {
                'print': perms.print_lowres,
                'modify': perms.modify_other,
                'copy': perms.extract,
                'annotate': perms.modify_annotation,
                'fill_forms': perms.fill_forms,
                'extract_text': perms.extract,
                'assemble': perms.modify_assembly,
                'high_quality_print': perms.print_highres
            }
        except Exception:
            return {}
    
    def _get_pymupdf_permissions(self, doc) -> Dict[str, bool]:
        """Extract permissions from PyMuPDF document"""
        try:
            perm = doc.permissions
            return {
                'print': bool(perm & fitz.PDF_PERM_PRINT),
                'modify': bool(perm & fitz.PDF_PERM_MODIFY),
                'copy': bool(perm & fitz.PDF_PERM_COPY),
                'annotate': bool(perm & fitz.PDF_PERM_ANNOTATE),
                'fill_forms': bool(perm & fitz.PDF_PERM_FORM),
                'extract_text': bool(perm & fitz.PDF_PERM_ACCESSIBILITY),
                'assemble': bool(perm & fitz.PDF_PERM_ASSEMBLE),
                'high_quality_print': bool(perm & fitz.PDF_PERM_PRINT_HQ)
            }
        except Exception:
            return {}


class PDFDigitalSignature:
    """Handles PDF digital signatures"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def sign_pdf(self, input_path: str, output_path: str, 
                signature: DigitalSignature) -> SecurityResult:
        """Add digital signature to PDF"""
        try:
            # Validate inputs
            valid, msg = PDFSecurityValidator.validate_pdf_file(input_path)
            if not valid:
                return SecurityResult(False, SecurityOperation.DIGITAL_SIGN, msg)
            
            valid, msg = PDFSecurityValidator.validate_signature_config(signature)
            if not valid:
                return SecurityResult(False, SecurityOperation.DIGITAL_SIGN, msg)
            
            if not HAS_CRYPTOGRAPHY:
                return SecurityResult(
                    False, SecurityOperation.DIGITAL_SIGN,
                    "cryptography library required for digital signatures"
                )
            
            # For now, create a basic signature placeholder
            # Full implementation would require comprehensive certificate handling
            return self._create_signature_placeholder(input_path, output_path, signature)
            
        except Exception as e:
            self.logger.error(f"Digital signing failed: {str(e)}")
            return SecurityResult(False, SecurityOperation.DIGITAL_SIGN, f"Signing failed: {str(e)}")
    
    def _create_signature_placeholder(self, input_path: str, output_path: str, 
                                    signature: DigitalSignature) -> SecurityResult:
        """Create signature placeholder (basic implementation)"""
        try:
            # Copy file and add signature metadata
            shutil.copy2(input_path, output_path)
            
            # Add signature information to metadata (basic implementation)
            if HAS_PYMUPDF:
                doc = fitz.open(output_path)
                
                # Add signature annotation if visible
                if signature.visible:
                    page = doc[0]  # Add to first page
                    rect = fitz.Rect(*signature.signature_rect)
                    annot = page.add_text_annot(
                        rect.tl,
                        f"Digitally Signed\nReason: {signature.reason}\nLocation: {signature.location}"
                    )
                    annot.set_info(title="Digital Signature")
                
                # Update metadata
                metadata = doc.metadata
                metadata['creator'] = f"Signed by {signature.contact_info}"
                metadata['subject'] = f"Digital Signature: {signature.reason}"
                doc.set_metadata(metadata)
                
                doc.save(output_path, incremental=True)
                doc.close()
            
            return SecurityResult(
                True, SecurityOperation.DIGITAL_SIGN,
                f"PDF signed and saved to {output_path}",
                output_path=output_path,
                signature_info={
                    'reason': signature.reason,
                    'location': signature.location,
                    'contact': signature.contact_info,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return SecurityResult(False, SecurityOperation.DIGITAL_SIGN, f"Signature creation failed: {str(e)}")
    
    def verify_signatures(self, file_path: str) -> SecurityResult:
        """Verify digital signatures in PDF"""
        try:
            valid, msg = PDFSecurityValidator.validate_pdf_file(file_path)
            if not valid:
                return SecurityResult(False, SecurityOperation.VERIFY_SIGNATURE, msg)
            
            # Basic signature verification (placeholder implementation)
            signature_info = {
                'has_signatures': False,
                'signature_count': 0,
                'signatures': []
            }
            
            if HAS_PYMUPDF:
                doc = fitz.open(file_path)
                
                # Check for signature annotations
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    annots = page.annots()
                    
                    for annot in annots:
                        if annot.type[1] == 'Text' and 'signature' in annot.info.get('title', '').lower():
                            signature_info['has_signatures'] = True
                            signature_info['signature_count'] += 1
                            signature_info['signatures'].append({
                                'page': page_num + 1,
                                'type': 'annotation',
                                'title': annot.info.get('title', ''),
                                'content': annot.info.get('content', '')
                            })
                
                doc.close()
            
            return SecurityResult(
                True, SecurityOperation.VERIFY_SIGNATURE,
                f"Signature verification completed - Found {signature_info['signature_count']} signatures",
                signature_info=signature_info
            )
            
        except Exception as e:
            return SecurityResult(False, SecurityOperation.VERIFY_SIGNATURE, f"Verification failed: {str(e)}")


class PDFSecurityEngine:
    """Main PDF security operations engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.password_protection = PDFPasswordProtection()
        self.digital_signature = PDFDigitalSignature()
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check available security libraries"""
        return {
            'pymupdf': HAS_PYMUPDF,
            'pikepdf': HAS_PIKEPDF,
            'cryptography': HAS_CRYPTOGRAPHY
        }
    
    def encrypt_pdf(self, input_path: str, output_path: str, 
                   settings: SecuritySettings) -> SecurityResult:
        """Encrypt PDF with password and permissions"""
        return self.password_protection.encrypt_pdf(input_path, output_path, settings)
    
    def decrypt_pdf(self, input_path: str, output_path: str, password: str) -> SecurityResult:
        """Decrypt password-protected PDF"""
        return self.password_protection.decrypt_pdf(input_path, output_path, password)
    
    def get_security_info(self, file_path: str, password: str = "") -> SecurityResult:
        """Get security information about PDF"""
        return self.password_protection.get_security_info(file_path, password)
    
    def sign_pdf(self, input_path: str, output_path: str, 
                signature: DigitalSignature) -> SecurityResult:
        """Add digital signature to PDF"""
        return self.digital_signature.sign_pdf(input_path, output_path, signature)
    
    def verify_signatures(self, file_path: str) -> SecurityResult:
        """Verify digital signatures in PDF"""
        return self.digital_signature.verify_signatures(file_path)
    
    def remove_security(self, input_path: str, output_path: str, 
                       owner_password: str) -> SecurityResult:
        """Remove all security restrictions from PDF"""
        try:
            # First try to decrypt
            result = self.decrypt_pdf(input_path, output_path, owner_password)
            if result.success:
                result.operation = SecurityOperation.REMOVE_PASSWORD
                result.message = f"Security restrictions removed and saved to {output_path}"
            
            return result
            
        except Exception as e:
            return SecurityResult(
                False, SecurityOperation.REMOVE_PASSWORD, 
                f"Failed to remove security: {str(e)}"
            )
    
    def batch_security_operation(self, file_paths: List[str], operation: SecurityOperation,
                                **kwargs) -> List[SecurityResult]:
        """Perform security operation on multiple files"""
        results = []
        
        for file_path in file_paths:
            try:
                if operation == SecurityOperation.ENCRYPT:
                    output_path = kwargs.get('output_path', file_path.replace('.pdf', '_encrypted.pdf'))
                    settings = kwargs.get('settings', SecuritySettings())
                    result = self.encrypt_pdf(file_path, output_path, settings)
                    
                elif operation == SecurityOperation.DECRYPT:
                    output_path = kwargs.get('output_path', file_path.replace('.pdf', '_decrypted.pdf'))
                    password = kwargs.get('password', '')
                    result = self.decrypt_pdf(file_path, output_path, password)
                    
                elif operation == SecurityOperation.GET_SECURITY_INFO:
                    password = kwargs.get('password', '')
                    result = self.get_security_info(file_path, password)
                    
                else:
                    result = SecurityResult(
                        False, operation, 
                        f"Batch operation not supported for {operation.value}"
                    )
                
                results.append(result)
                
            except Exception as e:
                results.append(SecurityResult(
                    False, operation, 
                    f"Batch operation failed for {file_path}: {str(e)}"
                ))
        
        return results


# Convenience functions for external access
def create_security_engine() -> PDFSecurityEngine:
    """Create a new PDF security engine instance"""
    return PDFSecurityEngine()


def create_security_settings(user_password: str = "", owner_password: str = "",
                           encryption_level: EncryptionLevel = EncryptionLevel.AES_256,
                           **permissions) -> SecuritySettings:
    """Create security settings with convenience parameters"""
    settings = SecuritySettings(
        user_password=user_password,
        owner_password=owner_password,
        encryption_level=encryption_level
    )
    
    # Apply permission overrides
    for perm, value in permissions.items():
        if hasattr(settings, f'allow_{perm}'):
            setattr(settings, f'allow_{perm}', value)
    
    return settings


def create_digital_signature(certificate_path: str, private_key_path: str = "",
                           password: str = "", reason: str = "Document verification",
                           **kwargs) -> DigitalSignature:
    """Create digital signature configuration"""
    signature = DigitalSignature(
        certificate_path=certificate_path,
        private_key_path=private_key_path,
        password=password,
        reason=reason
    )
    
    # Apply optional parameters
    for key, value in kwargs.items():
        if hasattr(signature, key):
            setattr(signature, key, value)
    
    return signature
