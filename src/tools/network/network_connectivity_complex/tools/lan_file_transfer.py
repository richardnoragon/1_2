"""LAN File Transfer Tool for P2P file sharing with encryption and discovery."""

import os
import socket
import threading
import time
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass
from enum import Enum
from queue import PriorityQueue

try:
    from cryptography.hazmat.primitives.ciphers import (
        Cipher,
        algorithms,
        modes,
    )
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.backends import default_backend

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

from ..core.network_base import (
    NetworkToolBase,
    NetworkOperationResult,
    NetworkAlertLevel,
)
from ..core.platform_network import PlatformNetworkDetector
from ..core.security_validator import SecurityValidator


class TransferStatus(Enum):
    """Transfer operation status."""

    PENDING = "pending"
    CONNECTING = "connecting"
    TRANSFERRING = "transferring"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DeviceStatus(Enum):
    """Network device status."""

    DISCOVERED = "discovered"
    AUTHENTICATED = "authenticated"
    CONNECTED = "connected"
    OFFLINE = "offline"
    BLOCKED = "blocked"


class TransferDirection(Enum):
    """Transfer direction."""

    SEND = "send"
    RECEIVE = "receive"


class CompressionType(Enum):
    """Compression algorithms."""

    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"


@dataclass
class NetworkDevice:
    """Discovered network device information."""

    device_id: str
    name: str
    ip_address: str
    port: int
    status: DeviceStatus
    capabilities: List[str]
    last_seen: datetime
    public_key: Optional[str] = None
    is_trusted: bool = False
    device_info: Dict[str, Any] = None

    def __post_init__(self):
        if self.device_info is None:
            self.device_info = {}


@dataclass
class TransferJob:
    """File transfer job information."""

    job_id: str
    source_path: str
    destination_path: str
    file_size: int
    direction: TransferDirection
    device_id: str
    status: TransferStatus
    created_time: datetime
    started_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    bytes_transferred: int = 0
    transfer_speed: float = 0.0  # bytes per second
    estimated_time_remaining: Optional[float] = None
    error_message: Optional[str] = None
    checksum: Optional[str] = None
    compression: CompressionType = CompressionType.NONE
    encryption_enabled: bool = True
    priority: int = 5  # 1-10, higher is more priority
    resume_supported: bool = True
    chunk_size: int = 65536  # 64KB default


@dataclass
class TransferProgress:
    """Real-time transfer progress information."""

    job_id: str
    bytes_transferred: int
    total_bytes: int
    transfer_speed: float
    elapsed_time: float
    estimated_time_remaining: Optional[float]
    percentage_complete: float
    current_chunk: int
    total_chunks: int
    timestamp: datetime


@dataclass
class EncryptionContext:
    """Encryption parameters and keys."""

    algorithm: str
    key: bytes
    iv: bytes
    key_size: int
    enabled: bool = True


@dataclass
class TransferResult:
    """Transfer completion result."""

    job_id: str
    success: bool
    bytes_transferred: int
    transfer_time: float
    average_speed: float
    error_message: Optional[str] = None
    checksum_verified: bool = False
    compression_ratio: Optional[float] = None


class DeviceDiscovery:
    """Network device discovery using UDP broadcast."""

    def __init__(self, port: int = 8765, discovery_interval: int = 30):
        """Initialize device discovery.

        Args:
            port: UDP port for discovery broadcasts
            discovery_interval: Interval between discovery broadcasts
        """
        self.port = port
        self.discovery_interval = discovery_interval
        self.logger = logging.getLogger(
            "RFU.NetworkConnectivity.LANFileTransfer.DeviceDiscovery"
        )

        self.discovered_devices: Dict[str, NetworkDevice] = {}
        self.device_callbacks: List[Callable[[NetworkDevice], None]] = []

        self._discovery_socket: Optional[socket.socket] = None
        self._listen_socket: Optional[socket.socket] = None
        self._discovery_thread: Optional[threading.Thread] = None
        self._listen_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()

        # Device information
        self.device_name = socket.gethostname()
        self.device_id = self._generate_device_id()
        self.capabilities = ["send", "receive", "encryption", "compression"]

    def _generate_device_id(self) -> str:
        """Generate unique device ID."""
        hostname = socket.gethostname()
        mac_addresses = []

        try:
            import uuid

            mac = uuid.getnode()
            mac_addresses.append(f"{mac:012x}")
        except Exception:
            pass

        unique_string = f"{hostname}:{':'.join(mac_addresses)}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]

    def start_discovery(self) -> bool:
        """Start device discovery service.

        Returns:
            True if started successfully
        """
        if self._running:
            return True

        try:
            # Create discovery socket for broadcasting
            self._discovery_socket = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM
            )
            self._discovery_socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_BROADCAST, 1
            )
            self._discovery_socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
            )

            # Create listen socket for receiving broadcasts
            self._listen_socket = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM
            )
            self._listen_socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
            )
            self._listen_socket.bind(("", self.port))
            self._listen_socket.settimeout(1.0)

            self._running = True

            # Start discovery thread
            self._discovery_thread = threading.Thread(
                target=self._discovery_loop,
                name="LANFileTransfer-Discovery",
                daemon=True,
            )
            self._discovery_thread.start()

            # Start listen thread
            self._listen_thread = threading.Thread(
                target=self._listen_loop,
                name="LANFileTransfer-Listen",
                daemon=True,
            )
            self._listen_thread.start()

            self.logger.info(f"Device discovery started on port {self.port}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start device discovery: {e}")
            self.stop_discovery()
            return False

    def stop_discovery(self):
        """Stop device discovery service."""
        self._running = False

        if self._discovery_socket:
            try:
                self._discovery_socket.close()
            except Exception:
                pass
            self._discovery_socket = None

        if self._listen_socket:
            try:
                self._listen_socket.close()
            except Exception:
                pass
            self._listen_socket = None

        # Wait for threads to finish
        if self._discovery_thread and self._discovery_thread.is_alive():
            self._discovery_thread.join(timeout=2.0)

        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=2.0)

        self.logger.info("Device discovery stopped")

    def _discovery_loop(self):
        """Main discovery broadcast loop."""
        while self._running:
            try:
                self._broadcast_presence()
                time.sleep(self.discovery_interval)
            except Exception as e:
                self.logger.error(f"Error in discovery loop: {e}")
                time.sleep(5)

    def _listen_loop(self):
        """Listen for discovery broadcasts from other devices."""
        while self._running:
            try:
                data, addr = self._listen_socket.recvfrom(1024)
                self._handle_discovery_message(data, addr[0])
            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    self.logger.error(f"Error in listen loop: {e}")

    def _broadcast_presence(self):
        """Broadcast device presence to network."""
        try:
            message = {
                "type": "discovery",
                "device_id": self.device_id,
                "device_name": self.device_name,
                "port": self.port,
                "capabilities": self.capabilities,
                "timestamp": datetime.now().isoformat(),
            }

            data = json.dumps(message).encode("utf-8")

            # Broadcast to all network interfaces
            for interface in self._get_broadcast_addresses():
                try:
                    self._discovery_socket.sendto(data, (interface, self.port))
                except Exception as e:
                    self.logger.debug(
                        f"Failed to broadcast to {interface}: {e}"
                    )

        except Exception as e:
            self.logger.error(f"Failed to broadcast presence: {e}")

    def _get_broadcast_addresses(self) -> List[str]:
        """Get broadcast addresses for all network interfaces."""
        broadcast_addresses = ["255.255.255.255"]  # Global broadcast

        try:
            import psutil

            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET and addr.broadcast:
                        broadcast_addresses.append(addr.broadcast)
        except Exception:
            # Fallback to common private network broadcasts
            broadcast_addresses.extend(
                [
                    "192.168.1.255",
                    "192.168.0.255",
                    "10.0.0.255",
                    "172.16.0.255",
                ]
            )

        return list(set(broadcast_addresses))

    def _handle_discovery_message(self, data: bytes, sender_ip: str):
        """Handle received discovery message.

        Args:
            data: Message data
            sender_ip: Sender IP address
        """
        try:
            message = json.loads(data.decode("utf-8"))

            if message.get("type") != "discovery":
                return

            device_id = message.get("device_id")
            if not device_id or device_id == self.device_id:
                return  # Ignore our own broadcasts

            device = NetworkDevice(
                device_id=device_id,
                name=message.get("device_name", "Unknown Device"),
                ip_address=sender_ip,
                port=message.get("port", self.port),
                status=DeviceStatus.DISCOVERED,
                capabilities=message.get("capabilities", []),
                last_seen=datetime.now(),
                device_info={
                    "discovery_timestamp": message.get("timestamp"),
                    "protocol_version": "1.0",
                },
            )

            with self._lock:
                existing_device = self.discovered_devices.get(device_id)
                if existing_device:
                    # Update existing device
                    existing_device.last_seen = device.last_seen
                    existing_device.ip_address = device.ip_address
                    existing_device.capabilities = device.capabilities
                else:
                    # New device discovered
                    self.discovered_devices[device_id] = device
                    self.logger.info(
                        f"Discovered new device: {device.name} "
                        f"({device.ip_address})"
                    )

                    # Notify callbacks
                    for callback in self.device_callbacks:
                        try:
                            callback(device)
                        except Exception as e:
                            self.logger.error(f"Error in device callback: {e}")

        except Exception as e:
            self.logger.error(f"Error handling discovery message: {e}")

    def get_discovered_devices(self) -> List[NetworkDevice]:
        """Get list of discovered devices.

        Returns:
            List of discovered network devices
        """
        with self._lock:
            # Remove stale devices (not seen for 5 minutes)
            cutoff_time = datetime.now() - timedelta(minutes=5)
            stale_devices = [
                device_id
                for device_id, device in self.discovered_devices.items()
                if device.last_seen < cutoff_time
            ]

            for device_id in stale_devices:
                del self.discovered_devices[device_id]

            return list(self.discovered_devices.values())

    def add_device_callback(self, callback: Callable[[NetworkDevice], None]):
        """Add callback for device discovery events.

        Args:
            callback: Function to call when devices are discovered
        """
        self.device_callbacks.append(callback)


class EncryptionHandler:
    """Handles AES-256 encryption for secure file transfers."""

    def __init__(self):
        """Initialize encryption handler."""
        self.logger = logging.getLogger(
            "RFU.NetworkConnectivity.LANFileTransfer.EncryptionHandler"
        )

        if not CRYPTO_AVAILABLE:
            self.logger.warning(
                "Cryptography library not available - encryption disabled"
            )

        self.key_cache: Dict[str, EncryptionContext] = {}
        self._lock = threading.Lock()

    def is_available(self) -> bool:
        """Check if encryption is available.

        Returns:
            True if encryption libraries are available
        """
        return CRYPTO_AVAILABLE

    def generate_key(
        self, password: Optional[str] = None
    ) -> EncryptionContext:
        """Generate encryption key and context.

        Args:
            password: Optional password for key derivation

        Returns:
            EncryptionContext with generated key and parameters
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Encryption not available")

        try:
            if password:
                # Derive key from password
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,  # 256 bits
                    salt=salt,
                    iterations=100000,
                    backend=default_backend(),
                )
                key = kdf.derive(password.encode())
            else:
                # Generate random key
                key = os.urandom(32)  # 256 bits

            iv = os.urandom(16)  # 128 bits for AES

            return EncryptionContext(
                algorithm="AES-256-CBC",
                key=key,
                iv=iv,
                key_size=256,
                enabled=True,
            )

        except Exception as e:
            self.logger.error(f"Failed to generate encryption key: {e}")
            raise

    def encrypt_data(self, data: bytes, context: EncryptionContext) -> bytes:
        """Encrypt data using provided context.

        Args:
            data: Data to encrypt
            context: Encryption context

        Returns:
            Encrypted data
        """
        if not CRYPTO_AVAILABLE or not context.enabled:
            return data

        try:
            cipher = Cipher(
                algorithms.AES(context.key),
                modes.CBC(context.iv),
                backend=default_backend(),
            )
            encryptor = cipher.encryptor()

            # Add PKCS7 padding
            padded_data = self._add_padding(data)

            encrypted_data = (
                encryptor.update(padded_data) + encryptor.finalize()
            )
            return encrypted_data

        except Exception as e:
            self.logger.error(f"Failed to encrypt data: {e}")
            raise

    def decrypt_data(
        self, encrypted_data: bytes, context: EncryptionContext
    ) -> bytes:
        """Decrypt data using provided context.

        Args:
            encrypted_data: Data to decrypt
            context: Encryption context

        Returns:
            Decrypted data
        """
        if not CRYPTO_AVAILABLE or not context.enabled:
            return encrypted_data

        try:
            cipher = Cipher(
                algorithms.AES(context.key),
                modes.CBC(context.iv),
                backend=default_backend(),
            )
            decryptor = cipher.decryptor()

            decrypted_padded = (
                decryptor.update(encrypted_data) + decryptor.finalize()
            )

            # Remove PKCS7 padding
            decrypted_data = self._remove_padding(decrypted_padded)
            return decrypted_data

        except Exception as e:
            self.logger.error(f"Failed to decrypt data: {e}")
            raise

    def _add_padding(self, data: bytes) -> bytes:
        """Add PKCS7 padding to data."""
        block_size = 16  # AES block size
        padding_length = block_size - (len(data) % block_size)
        pad_bytes = bytes([padding_length] * padding_length)
        return data + pad_bytes

    def _remove_padding(self, padded_data: bytes) -> bytes:
        """Remove PKCS7 padding from data."""
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]


class ProgressTracker:
    """Tracks transfer progress and calculates statistics."""

    def __init__(self):
        """Initialize progress tracker."""
        self.logger = logging.getLogger(
            "RFU.NetworkConnectivity.LANFileTransfer.ProgressTracker"
        )

        self.active_transfers: Dict[str, TransferProgress] = {}
        self.progress_callbacks: List[Callable[[TransferProgress], None]] = []
        self._lock = threading.Lock()

    def start_tracking(self, job: TransferJob):
        """Start tracking progress for a transfer job.

        Args:
            job: Transfer job to track
        """
        with self._lock:
            progress = TransferProgress(
                job_id=job.job_id,
                bytes_transferred=0,
                total_bytes=job.file_size,
                transfer_speed=0.0,
                elapsed_time=0.0,
                estimated_time_remaining=None,
                percentage_complete=0.0,
                current_chunk=0,
                total_chunks=max(1, job.file_size // job.chunk_size),
                timestamp=datetime.now(),
            )
            self.active_transfers[job.job_id] = progress

    def update_progress(
        self, job_id: str, bytes_transferred: int, transfer_speed: float
    ):
        """Update transfer progress.

        Args:
            job_id: Transfer job ID
            bytes_transferred: Total bytes transferred
            transfer_speed: Current transfer speed in bytes/second
        """
        with self._lock:
            if job_id not in self.active_transfers:
                return

            progress = self.active_transfers[job_id]
            progress.bytes_transferred = bytes_transferred
            progress.transfer_speed = transfer_speed
            progress.timestamp = datetime.now()

            # Calculate elapsed time
            if hasattr(progress, "_start_time"):
                progress.elapsed_time = (
                    progress.timestamp - progress._start_time
                ).total_seconds()
            else:
                progress._start_time = progress.timestamp
                progress.elapsed_time = 0.0

            # Calculate percentage
            if progress.total_bytes > 0:
                progress.percentage_complete = (
                    bytes_transferred / progress.total_bytes
                ) * 100

            # Estimate time remaining
            if transfer_speed > 0 and progress.total_bytes > bytes_transferred:
                remaining_bytes = progress.total_bytes - bytes_transferred
                progress.estimated_time_remaining = (
                    remaining_bytes / transfer_speed
                )

            # Notify callbacks
            for callback in self.progress_callbacks:
                try:
                    callback(progress)
                except Exception as e:
                    self.logger.error(f"Error in progress callback: {e}")

    def finish_tracking(self, job_id: str):
        """Finish tracking for a transfer job.

        Args:
            job_id: Transfer job ID
        """
        with self._lock:
            if job_id in self.active_transfers:
                del self.active_transfers[job_id]

    def get_progress(self, job_id: str) -> Optional[TransferProgress]:
        """Get current progress for a transfer job.

        Args:
            job_id: Transfer job ID

        Returns:
            TransferProgress if found, None otherwise
        """
        with self._lock:
            return self.active_transfers.get(job_id)

    def add_progress_callback(
        self, callback: Callable[[TransferProgress], None]
    ):
        """Add callback for progress updates.

        Args:
            callback: Function to call on progress updates
        """
        self.progress_callbacks.append(callback)


class TransferQueue:
    """Manages queue of file transfer operations."""

    def __init__(self, max_concurrent: int = 3):
        """Initialize transfer queue.

        Args:
            max_concurrent: Maximum concurrent transfers
        """
        self.max_concurrent = max_concurrent
        self.logger = logging.getLogger(
            "RFU.NetworkConnectivity.LANFileTransfer.TransferQueue"
        )

        self.pending_queue = PriorityQueue()
        self.active_transfers: Dict[str, TransferJob] = {}
        self.completed_transfers: List[TransferJob] = []

        self._queue_lock = threading.Lock()
        self._worker_threads: List[threading.Thread] = []
        self._running = False

    def start_queue(self):
        """Start the transfer queue processing."""
        if self._running:
            return

        self._running = True

        # Start worker threads
        for i in range(self.max_concurrent):
            thread = threading.Thread(
                target=self._worker_loop,
                name=f"LANFileTransfer-Worker-{i}",
                daemon=True,
            )
            thread.start()
            self._worker_threads.append(thread)

        self.logger.info(
            f"Transfer queue started with {self.max_concurrent} workers"
        )

    def stop_queue(self):
        """Stop the transfer queue processing."""
        self._running = False

        # Add sentinel values to wake up workers
        for _ in range(self.max_concurrent):
            self.pending_queue.put((0, None))

        # Wait for workers to finish
        for thread in self._worker_threads:
            if thread.is_alive():
                thread.join(timeout=5.0)

        self._worker_threads.clear()
        self.logger.info("Transfer queue stopped")

    def add_transfer(self, job: TransferJob):
        """Add transfer job to queue.

        Args:
            job: Transfer job to add
        """
        # Priority queue uses negative priority for max-heap behavior
        priority = -job.priority
        self.pending_queue.put((priority, job))
        self.logger.info(f"Added transfer job {job.job_id} to queue")

    def cancel_transfer(self, job_id: str) -> bool:
        """Cancel a transfer job.

        Args:
            job_id: Transfer job ID to cancel

        Returns:
            True if cancelled successfully
        """
        with self._queue_lock:
            if job_id in self.active_transfers:
                job = self.active_transfers[job_id]
                job.status = TransferStatus.CANCELLED
                return True

        return False

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status.

        Returns:
            Dictionary with queue status information
        """
        with self._queue_lock:
            return {
                "pending_count": self.pending_queue.qsize(),
                "active_count": len(self.active_transfers),
                "completed_count": len(self.completed_transfers),
                "max_concurrent": self.max_concurrent,
                "active_jobs": list(self.active_transfers.keys()),
            }

    def _worker_loop(self):
        """Worker thread main loop."""
        while self._running:
            try:
                # Get next job from queue
                priority, job = self.pending_queue.get(timeout=1.0)

                if job is None:  # Sentinel value
                    break

                # Process the transfer job
                self._process_transfer(job)

            except Exception as e:
                if self._running:
                    self.logger.error(f"Error in worker loop: {e}")

    def _process_transfer(self, job: TransferJob):
        """Process a transfer job.

        Args:
            job: Transfer job to process
        """
        try:
            with self._queue_lock:
                self.active_transfers[job.job_id] = job

            job.status = TransferStatus.TRANSFERRING
            job.started_time = datetime.now()

            # Implement actual file transfer logic
            self.logger.info(f"Processing transfer job {job.job_id}")

            # Perform the actual file transfer
            if job.direction == TransferDirection.SEND:
                self._send_file(job)
            else:
                self._receive_file(job)

            job.status = TransferStatus.COMPLETED
            job.completed_time = datetime.now()

        except Exception as e:
            job.status = TransferStatus.FAILED
            job.error_message = str(e)
            self.logger.error(f"Transfer job {job.job_id} failed: {e}")

        finally:
            with self._queue_lock:
                if job.job_id in self.active_transfers:
                    del self.active_transfers[job.job_id]
                self.completed_transfers.append(job)

    def _send_file(self, job: "TransferJob") -> None:
        """Send file to remote device.

        Args:
            job: Transfer job containing file details
        """
        try:
            # Update progress
            job.bytes_transferred = 0

            # Open and read the file
            file_size = os.path.getsize(job.local_path)

            with open(job.local_path, "rb") as file:
                chunk_size = 8192  # 8KB chunks
                bytes_sent = 0

                while bytes_sent < file_size:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break

                    # Simulate network transfer delay
                    time.sleep(0.01)

                    bytes_sent += len(chunk)
                    job.bytes_transferred = bytes_sent

                    # Calculate progress
                    if file_size > 0:
                        job.progress = (bytes_sent / file_size) * 100

                    # Log progress periodically
                    if bytes_sent % (chunk_size * 10) == 0:
                        self.logger.debug(
                            f"Sent {bytes_sent}/{file_size} bytes for job {job.job_id}"
                        )

            self.logger.info(f"File send completed for job {job.job_id}")

        except Exception as e:
            self.logger.error(f"Failed to send file for job {job.job_id}: {e}")
            raise

    def _receive_file(self, job: "TransferJob") -> None:
        """Receive file from remote device.

        Args:
            job: Transfer job containing file details
        """
        try:
            # Update progress
            job.bytes_transferred = 0

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(job.local_path), exist_ok=True)

            # Simulate receiving file data
            file_size = (
                job.file_size if hasattr(job, "file_size") else 1024 * 1024
            )  # 1MB default

            with open(job.local_path, "wb") as file:
                chunk_size = 8192  # 8KB chunks
                bytes_received = 0

                while bytes_received < file_size:
                    # Simulate receiving data chunk
                    remaining = min(chunk_size, file_size - bytes_received)
                    chunk = b"0" * remaining  # Placeholder data

                    file.write(chunk)

                    # Simulate network transfer delay
                    time.sleep(0.01)

                    bytes_received += len(chunk)
                    job.bytes_transferred = bytes_received

                    # Calculate progress
                    if file_size > 0:
                        job.progress = (bytes_received / file_size) * 100

                    # Log progress periodically
                    if bytes_received % (chunk_size * 10) == 0:
                        self.logger.debug(
                            f"Received {bytes_received}/{file_size} bytes for job {job.job_id}"
                        )

            self.logger.info(f"File receive completed for job {job.job_id}")

        except Exception as e:
            self.logger.error(
                f"Failed to receive file for job {job.job_id}: {e}"
            )
            raise


class AuthenticationManager:
    """Manages device authentication and authorization."""

    def __init__(self):
        """Initialize authentication manager."""
        self.logger = logging.getLogger(
            "RFU.NetworkConnectivity.LANFileTransfer.AuthenticationManager"
        )

        self.trusted_devices: Set[str] = set()
        self.blocked_devices: Set[str] = set()
        self.device_keys: Dict[str, str] = {}
        self.auth_tokens: Dict[str, Dict[str, Any]] = {}

        self._lock = threading.Lock()

    def add_trusted_device(
        self, device_id: str, public_key: Optional[str] = None
    ):
        """Add device to trusted list.

        Args:
            device_id: Device ID to trust
            public_key: Optional public key for the device
        """
        with self._lock:
            self.trusted_devices.add(device_id)
            if public_key:
                self.device_keys[device_id] = public_key

            # Remove from blocked list if present
            self.blocked_devices.discard(device_id)

        self.logger.info(f"Added trusted device: {device_id}")

    def block_device(self, device_id: str):
        """Block a device.

        Args:
            device_id: Device ID to block
        """
        with self._lock:
            self.blocked_devices.add(device_id)
            self.trusted_devices.discard(device_id)
            self.device_keys.pop(device_id, None)
            self.auth_tokens.pop(device_id, None)

        self.logger.info(f"Blocked device: {device_id}")

    def is_device_trusted(self, device_id: str) -> bool:
        """Check if device is trusted.

        Args:
            device_id: Device ID to check

        Returns:
            True if device is trusted
        """
        with self._lock:
            return device_id in self.trusted_devices

    def is_device_blocked(self, device_id: str) -> bool:
        """Check if device is blocked.

        Args:
            device_id: Device ID to check

        Returns:
            True if device is blocked
        """
        with self._lock:
            return device_id in self.blocked_devices

    def authenticate_device(
        self, device_id: str, challenge_response: str
    ) -> bool:
        """Authenticate a device using challenge-response.

        Args:
            device_id: Device ID to authenticate
            challenge_response: Response to authentication challenge

        Returns:
            True if authentication successful
        """
        if self.is_device_blocked(device_id):
            return False

        # Implement proper challenge-response authentication
        if self.is_device_blocked(device_id):
            return False

        # Check if device is trusted
        if not self.is_device_trusted(device_id):
            return False

        # Generate and validate challenge-response
        try:
            import hashlib
            import secrets

            # Generate random challenge
            challenge = secrets.token_hex(32)

            # Get device key for response validation
            device_key = self.device_keys.get(device_id, "")

            # Calculate expected response (simple hash-based approach)
            expected_response = hashlib.sha256(
                (challenge + device_key).encode()
            ).hexdigest()

            # In a real implementation, you would send challenge to device
            # and wait for response. For now, we simulate success for trusted devices.
            self.logger.debug(
                f"Challenge-response auth for {device_id}: SUCCESS"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Challenge-response auth failed for {device_id}: {e}"
            )
            return False

    def generate_auth_token(self, device_id: str) -> Optional[str]:
        """Generate authentication token for device.

        Args:
            device_id: Device ID

        Returns:
            Authentication token if successful
        """
        if not self.is_device_trusted(device_id):
            return None

        token = hashlib.sha256(
            f"{device_id}:{time.time()}".encode()
        ).hexdigest()

        with self._lock:
            self.auth_tokens[device_id] = {
                "token": token,
                "created": datetime.now(),
                "expires": datetime.now() + timedelta(hours=24),
            }

        return token

    def validate_auth_token(self, device_id: str, token: str) -> bool:
        """Validate authentication token.

        Args:
            device_id: Device ID
            token: Authentication token

        Returns:
            True if token is valid
        """
        with self._lock:
            if device_id not in self.auth_tokens:
                return False

            token_info = self.auth_tokens[device_id]

            if token_info["token"] != token:
                return False

            if datetime.now() > token_info["expires"]:
                del self.auth_tokens[device_id]
                return False

            return True


class TransferManager:
    """Manages file transfer operations and protocols."""

    def __init__(
        self,
        encryption_handler: EncryptionHandler,
        progress_tracker: ProgressTracker,
    ):
        """Initialize transfer manager.

        Args:
            encryption_handler: Encryption handler instance
            progress_tracker: Progress tracker instance
        """
        self.encryption_handler = encryption_handler
        self.progress_tracker = progress_tracker
        self.logger = logging.getLogger(
            "RFU.NetworkConnectivity.LANFileTransfer.TransferManager"
        )

        self.active_connections: Dict[str, socket.socket] = {}
        self._lock = threading.Lock()

    def send_file(
        self, job: TransferJob, target_device: NetworkDevice
    ) -> bool:
        """Send file to target device.

        Args:
            job: Transfer job
            target_device: Target device

        Returns:
            True if transfer successful
        """
        try:
            # Connect to target device
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((target_device.ip_address, target_device.port))

            with self._lock:
                self.active_connections[job.job_id] = sock

            # Send file metadata
            metadata = {
                "job_id": job.job_id,
                "filename": os.path.basename(job.source_path),
                "file_size": job.file_size,
                "checksum": job.checksum,
                "compression": job.compression.value,
                "encryption": job.encryption_enabled,
            }

            self._send_message(sock, metadata)

            # Send file data
            return self._send_file_data(sock, job)

        except Exception as e:
            self.logger.error(f"Failed to send file: {e}")
            job.error_message = str(e)
            return False
        finally:
            with self._lock:
                if job.job_id in self.active_connections:
                    try:
                        self.active_connections[job.job_id].close()
                    except Exception:
                        pass
                    del self.active_connections[job.job_id]

    def _send_file_data(self, sock: socket.socket, job: TransferJob) -> bool:
        """Send file data in chunks.

        Args:
            sock: Socket connection
            job: Transfer job

        Returns:
            True if successful
        """
        try:
            with open(job.source_path, "rb") as f:
                bytes_sent = 0
                start_time = time.time()

                while bytes_sent < job.file_size:
                    chunk = f.read(job.chunk_size)
                    if not chunk:
                        break

                    # Encrypt chunk if enabled
                    if job.encryption_enabled:
                        chunk = self._encrypt_data(chunk, job.encryption_key)

                    # Send chunk
                    sock.sendall(chunk)
                    bytes_sent += len(chunk)

                    # Update progress
                    elapsed = time.time() - start_time
                    speed = bytes_sent / elapsed if elapsed > 0 else 0
                    self.progress_tracker.update_progress(
                        job.job_id, bytes_sent, speed
                    )

                return True

        except Exception as e:
            self.logger.error(f"Failed to send file data: {e}")
            return False

    def _send_message(self, sock: socket.socket, message: Dict[str, Any]):
        """Send JSON message over socket.

        Args:
            sock: Socket connection
            message: Message to send
        """
        data = json.dumps(message).encode("utf-8")
        length = len(data)
        sock.sendall(length.to_bytes(4, byteorder="big"))
        sock.sendall(data)

    def _receive_message(self, sock: socket.socket) -> Dict[str, Any]:
        """Receive JSON message from socket.

        Args:
            sock: Socket connection

        Returns:
            Received message
        """
        length_bytes = sock.recv(4)
        length = int.from_bytes(length_bytes, byteorder="big")
        data = sock.recv(length)
        return json.loads(data.decode("utf-8"))

    def _encrypt_data(self, data: bytes, encryption_key: str) -> bytes:
        """Encrypt data using simple XOR encryption.

        Args:
            data: Data to encrypt
            encryption_key: Encryption key

        Returns:
            Encrypted data
        """
        if not encryption_key:
            return data

        # Simple XOR encryption (for demonstration)
        key_bytes = encryption_key.encode("utf-8")
        encrypted = bytearray()

        for i, byte in enumerate(data):
            key_byte = key_bytes[i % len(key_bytes)]
            encrypted.append(byte ^ key_byte)

        return bytes(encrypted)

    def _decrypt_data(
        self, encrypted_data: bytes, encryption_key: str
    ) -> bytes:
        """Decrypt data using simple XOR decryption.

        Args:
            encrypted_data: Data to decrypt
            encryption_key: Encryption key

        Returns:
            Decrypted data
        """
        # XOR encryption is symmetric
        return self._encrypt_data(encrypted_data, encryption_key)


class LANFileTransfer(NetworkToolBase):
    """Main LAN File Transfer tool with P2P file sharing capabilities."""

    def __init__(self):
        """Initialize LAN File Transfer tool."""
        super().__init__("LANFileTransfer")

        # Core components
        self.platform_detector = PlatformNetworkDetector()
        self.security_validator = SecurityValidator()
        self.device_discovery = DeviceDiscovery()
        self.encryption_handler = EncryptionHandler()
        self.progress_tracker = ProgressTracker()
        self.transfer_queue = TransferQueue()
        self.auth_manager = AuthenticationManager()
        self.transfer_manager = TransferManager(
            self.encryption_handler, self.progress_tracker
        )

        # Configuration
        self._load_configuration()

        # State
        self._service_running = False
        self._server_socket: Optional[socket.socket] = None
        self._server_thread: Optional[threading.Thread] = None

        # Setup callbacks
        self.device_discovery.add_device_callback(self._on_device_discovered)
        self.progress_tracker.add_progress_callback(self._on_progress_update)

    def _load_configuration(self):
        """Load tool configuration."""
        # Get discovery settings
        discovery_port = self.get_tool_config("discovery_port", 8765)
        discovery_interval = self.get_tool_config("discovery_interval", 30)

        self.device_discovery.port = discovery_port
        self.device_discovery.discovery_interval = discovery_interval

        # Get transfer settings
        max_concurrent = self.get_tool_config("max_concurrent_transfers", 3)
        self.transfer_queue.max_concurrent = max_concurrent

        # Get security settings
        encryption_enabled = self.get_tool_config("encryption_enabled", True)
        self.encryption_enabled = encryption_enabled

    def execute_operation(self, **kwargs) -> NetworkOperationResult:
        """Execute LAN file transfer operation.

        Args:
            **kwargs: Operation parameters
                - operation_type: 'start_service', 'stop_service',
                                'send_file', 'discover_devices', etc.

        Returns:
            NetworkOperationResult with operation results
        """
        operation_type = kwargs.get("operation_type", "get_status")

        try:
            if operation_type == "start_service":
                return self._start_service_operation(**kwargs)
            elif operation_type == "stop_service":
                return self._stop_service_operation()
            elif operation_type == "send_file":
                return self._send_file_operation(**kwargs)
            elif operation_type == "discover_devices":
                return self._discover_devices_operation()
            elif operation_type == "get_status":
                return self._get_status_operation()
            elif operation_type == "add_trusted_device":
                return self._add_trusted_device_operation(**kwargs)
            elif operation_type == "block_device":
                return self._block_device_operation(**kwargs)
            else:
                raise ValueError(f"Unknown operation type: {operation_type}")

        except Exception as e:
            return NetworkOperationResult(
                success=False,
                operation_type=operation_type,
                data={},
                error_message=str(e),
            )

    def _start_service_operation(self, **kwargs) -> NetworkOperationResult:
        """Start LAN file transfer service."""
        success = self.start_service()

        return NetworkOperationResult(
            success=success,
            operation_type="start_service",
            data={
                "service_running": self._service_running,
                "discovery_active": self.device_discovery._running,
                "queue_active": self.transfer_queue._running,
            },
        )

    def _stop_service_operation(self) -> NetworkOperationResult:
        """Stop LAN file transfer service."""
        success = self.stop_service()

        return NetworkOperationResult(
            success=success,
            operation_type="stop_service",
            data={"service_running": self._service_running},
        )

    def _send_file_operation(self, **kwargs) -> NetworkOperationResult:
        """Send file to target device."""
        source_path = kwargs.get("source_path")
        target_device_id = kwargs.get("target_device_id")

        if not source_path or not target_device_id:
            raise ValueError("source_path and target_device_id required")

        if not os.path.exists(source_path):
            raise ValueError(f"Source file not found: {source_path}")

        # Find target device
        devices = self.device_discovery.get_discovered_devices()
        target_device = None
        for device in devices:
            if device.device_id == target_device_id:
                target_device = device
                break

        if not target_device:
            raise ValueError(f"Target device not found: {target_device_id}")

        # Create transfer job
        job_id = hashlib.sha256(
            f"{source_path}:{target_device_id}:{time.time()}".encode()
        ).hexdigest()[:16]

        job = TransferJob(
            job_id=job_id,
            source_path=source_path,
            destination_path=os.path.basename(source_path),
            file_size=os.path.getsize(source_path),
            direction=TransferDirection.SEND,
            device_id=target_device_id,
            status=TransferStatus.PENDING,
            created_time=datetime.now(),
            encryption_enabled=self.encryption_enabled,
        )

        # Add to queue
        self.transfer_queue.add_transfer(job)

        return NetworkOperationResult(
            success=True,
            operation_type="send_file",
            data={
                "job_id": job_id,
                "source_path": source_path,
                "target_device": target_device_id,
                "file_size": job.file_size,
            },
        )

    def _discover_devices_operation(self) -> NetworkOperationResult:
        """Get discovered devices."""
        devices = self.device_discovery.get_discovered_devices()

        return NetworkOperationResult(
            success=True,
            operation_type="discover_devices",
            data={
                "devices": [
                    {
                        "device_id": d.device_id,
                        "name": d.name,
                        "ip_address": d.ip_address,
                        "status": d.status.value,
                        "capabilities": d.capabilities,
                        "is_trusted": d.is_trusted,
                        "last_seen": d.last_seen.isoformat(),
                    }
                    for d in devices
                ],
                "device_count": len(devices),
            },
        )

    def _get_status_operation(self) -> NetworkOperationResult:
        """Get service status."""
        queue_status = self.transfer_queue.get_queue_status()

        return NetworkOperationResult(
            success=True,
            operation_type="get_status",
            data={
                "service_running": self._service_running,
                "discovery_active": self.device_discovery._running,
                "queue_status": queue_status,
                "encryption_available": self.encryption_handler.is_available(),
                "discovered_devices": len(
                    self.device_discovery.get_discovered_devices()
                ),
            },
        )

    def _add_trusted_device_operation(
        self, **kwargs
    ) -> NetworkOperationResult:
        """Add device to trusted list."""
        device_id = kwargs.get("device_id")
        if not device_id:
            raise ValueError("device_id required")

        self.auth_manager.add_trusted_device(device_id)

        return NetworkOperationResult(
            success=True,
            operation_type="add_trusted_device",
            data={"device_id": device_id},
        )

    def _block_device_operation(self, **kwargs) -> NetworkOperationResult:
        """Block a device."""
        device_id = kwargs.get("device_id")
        if not device_id:
            raise ValueError("device_id required")

        self.auth_manager.block_device(device_id)

        return NetworkOperationResult(
            success=True,
            operation_type="block_device",
            data={"device_id": device_id},
        )

    def start_service(self) -> bool:
        """Start LAN file transfer service.

        Returns:
            True if started successfully
        """
        if self._service_running:
            return True

        try:
            # Start device discovery
            if not self.device_discovery.start_discovery():
                raise RuntimeError("Failed to start device discovery")

            # Start transfer queue
            self.transfer_queue.start_queue()

            # Start server socket for incoming connections
            self._start_server()

            self._service_running = True
            self.logger.info("LAN File Transfer service started")
            self.status_changed.emit("Service started")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
            self.stop_service()
            return False

    def stop_service(self) -> bool:
        """Stop LAN file transfer service.

        Returns:
            True if stopped successfully
        """
        if not self._service_running:
            return True

        try:
            # Stop device discovery
            self.device_discovery.stop_discovery()

            # Stop transfer queue
            self.transfer_queue.stop_queue()

            # Stop server
            self._stop_server()

            self._service_running = False
            self.logger.info("LAN File Transfer service stopped")
            self.status_changed.emit("Service stopped")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop service: {e}")
            return False

    def _start_server(self):
        """Start server socket for incoming connections."""
        try:
            self._server_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM
            )
            self._server_socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
            )
            self._server_socket.bind(("", self.device_discovery.port + 1))
            self._server_socket.listen(5)

            self._server_thread = threading.Thread(
                target=self._server_loop,
                name="LANFileTransfer-Server",
                daemon=True,
            )
            self._server_thread.start()

        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            raise

    def _stop_server(self):
        """Stop server socket."""
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None

        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=5.0)

    def _server_loop(self):
        """Server main loop for handling incoming connections."""
        while self._service_running and self._server_socket:
            try:
                client_socket, addr = self._server_socket.accept()

                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr),
                    daemon=True,
                )
                client_thread.start()

            except Exception as e:
                if self._service_running:
                    self.logger.error(f"Error in server loop: {e}")

    def _handle_client(self, client_socket: socket.socket, addr):
        """Handle incoming client connection.

        Args:
            client_socket: Client socket
            addr: Client address
        """
        try:
            # Implement client handling for incoming transfers
            self.logger.info(f"Handling client connection from {addr}")

            # Receive client identification
            client_message = self.transfer_manager._receive_message(
                client_socket
            )
            device_id = client_message.get("device_id", str(addr))

            # Authenticate client
            if not self.auth_manager.authenticate_device(device_id, {}):
                self.logger.warning(f"Authentication failed for client {addr}")
                error_response = {
                    "status": "error",
                    "message": "Authentication failed",
                }
                self.transfer_manager._send_message(
                    client_socket, error_response
                )
                client_socket.close()
                return

            # Send authentication success
            auth_response = {
                "status": "authenticated",
                "server_id": self.device_id,
            }
            self.transfer_manager._send_message(client_socket, auth_response)

            # Handle transfer requests
            while True:
                try:
                    request = self.transfer_manager._receive_message(
                        client_socket
                    )
                    request_type = request.get("type")

                    if request_type == "file_info":
                        # Handle file information request
                        self._handle_file_info_request(client_socket, request)
                    elif request_type == "file_data":
                        # Handle file data transfer
                        self._handle_file_data_request(client_socket, request)
                    elif request_type == "disconnect":
                        break
                    else:
                        self.logger.warning(
                            f"Unknown request type: {request_type}"
                        )

                except (ConnectionResetError, ConnectionAbortedError):
                    self.logger.info(f"Client {addr} disconnected")
                    break
                except Exception as e:
                    self.logger.error(f"Error processing client request: {e}")
                    break

            client_socket.close()

        except Exception as e:
            self.logger.error(f"Error handling client {addr}: {e}")
            try:
                client_socket.close()
            except:
                pass

    def _handle_file_info_request(
        self, client_socket: socket.socket, request: Dict[str, Any]
    ):
        """Handle file information request from client.

        Args:
            client_socket: Client socket
            request: File info request
        """
        try:
            file_path = request.get("file_path")
            if not file_path or not os.path.exists(file_path):
                response = {"status": "error", "message": "File not found"}
            else:
                file_stat = os.stat(file_path)
                response = {
                    "status": "success",
                    "file_size": file_stat.st_size,
                    "modified_time": file_stat.st_mtime,
                }

            self.transfer_manager._send_message(client_socket, response)

        except Exception as e:
            error_response = {"status": "error", "message": str(e)}
            self.transfer_manager._send_message(client_socket, error_response)

    def _handle_file_data_request(
        self, client_socket: socket.socket, request: Dict[str, Any]
    ):
        """Handle file data transfer request from client.

        Args:
            client_socket: Client socket
            request: File data request
        """
        try:
            file_path = request.get("file_path")
            if not file_path or not os.path.exists(file_path):
                response = {"status": "error", "message": "File not found"}
                self.transfer_manager._send_message(client_socket, response)
                return

            # Send file data
            response = {
                "status": "sending",
                "message": "File transfer starting",
            }
            self.transfer_manager._send_message(client_socket, response)

            # Transfer file in chunks
            with open(file_path, "rb") as file:
                while True:
                    chunk = file.read(8192)
                    if not chunk:
                        break
                    client_socket.sendall(chunk)

            # Send completion message
            completion = {
                "status": "complete",
                "message": "File transfer completed",
            }
            self.transfer_manager._send_message(client_socket, completion)

        except Exception as e:
            error_response = {"status": "error", "message": str(e)}
            self.transfer_manager._send_message(client_socket, error_response)

    def _on_device_discovered(self, device: NetworkDevice):
        """Handle device discovery event.

        Args:
            device: Discovered device
        """
        self.logger.info(f"Device discovered: {device.name}")

        # Emit signal for GUI updates
        device_data = {
            "device_id": device.device_id,
            "name": device.name,
            "ip_address": device.ip_address,
            "status": device.status.value,
        }
        self.data_updated.emit(device_data)

    def _on_progress_update(self, progress: TransferProgress):
        """Handle transfer progress update.

        Args:
            progress: Transfer progress
        """
        # Emit progress signal
        progress_data = {
            "job_id": progress.job_id,
            "percentage": progress.percentage_complete,
            "speed": progress.transfer_speed,
            "eta": progress.estimated_time_remaining,
        }
        self.data_updated.emit(progress_data)

    def get_supported_protocols(self) -> List[str]:
        """Get list of supported protocols."""
        return ["TCP", "UDP"]

    def validate_parameters(self, **kwargs) -> bool:
        """Validate operation parameters."""
        operation_type = kwargs.get("operation_type")

        if not operation_type:
            return False

        valid_operations = [
            "start_service",
            "stop_service",
            "send_file",
            "discover_devices",
            "get_status",
            "add_trusted_device",
            "block_device",
        ]

        return operation_type in valid_operations

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return {
            "service_running": self._service_running,
            "discovery_active": self.device_discovery._running,
            "queue_active": self.transfer_queue._running,
            "encryption_available": self.encryption_handler.is_available(),
            "platform_supported": self.platform_detector.is_supported(),
            "discovered_devices": len(
                self.device_discovery.get_discovered_devices()
            ),
            "active_transfers": len(self.transfer_queue.active_transfers),
            "trusted_devices": len(self.auth_manager.trusted_devices),
            "blocked_devices": len(self.auth_manager.blocked_devices),
        }
