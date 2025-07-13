"""Network protocol definitions"""

from enum import Enum
from typing import Protocol as TypingProtocol, Optional, Callable, Any
from abc import abstractmethod
import asyncio


class ProtocolType(Enum):
    """Types of network protocols"""
    TCP = "tcp"
    UDP = "udp"


class Protocol(TypingProtocol):
    """Protocol interface for network communication"""
    
    @abstractmethod
    async def connect(self, host: str, port: int) -> bool:
        """Connect to a server"""
        ...
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from server"""
        ...
    
    @abstractmethod
    async def send(self, data: bytes) -> bool:
        """Send data"""
        ...
    
    @abstractmethod
    async def receive(self) -> Optional[bytes]:
        """Receive data"""
        ...
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected"""
        ...
    
    @abstractmethod
    def get_latency(self) -> float:
        """Get current latency in milliseconds"""
        ...


class TCPProtocol:
    """TCP protocol implementation"""
    
    def __init__(self):
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._connected = False
        self._latency = 0.0
    
    async def connect(self, host: str, port: int) -> bool:
        """Connect via TCP"""
        try:
            self.reader, self.writer = await asyncio.open_connection(host, port)
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect TCP connection"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        self._connected = False
        self.reader = None
        self.writer = None
    
    async def send(self, data: bytes) -> bool:
        """Send data via TCP"""
        if not self._connected or not self.writer:
            return False
        try:
            self.writer.write(len(data).to_bytes(4, 'big'))
            self.writer.write(data)
            await self.writer.drain()
            return True
        except Exception:
            self._connected = False
            return False
    
    async def receive(self) -> Optional[bytes]:
        """Receive data via TCP"""
        if not self._connected or not self.reader:
            return None
        try:
            length_bytes = await self.reader.read(4)
            if not length_bytes:
                self._connected = False
                return None
            length = int.from_bytes(length_bytes, 'big')
            data = await self.reader.read(length)
            return data if data else None
        except Exception:
            self._connected = False
            return None
    
    def is_connected(self) -> bool:
        """Check TCP connection status"""
        return self._connected
    
    def get_latency(self) -> float:
        """Get TCP latency"""
        return self._latency


class UDPProtocol:
    """UDP protocol implementation"""
    
    def __init__(self):
        self.transport: Optional[asyncio.DatagramTransport] = None
        self.protocol: Optional[asyncio.DatagramProtocol] = None
        self._connected = False
        self._latency = 0.0
        self._receive_queue: asyncio.Queue = asyncio.Queue()
        self._remote_addr: Optional[tuple] = None
    
    async def connect(self, host: str, port: int) -> bool:
        """Connect via UDP"""
        try:
            loop = asyncio.get_event_loop()
            
            class UDPClientProtocol(asyncio.DatagramProtocol):
                def __init__(self, queue):
                    self.queue = queue
                
                def datagram_received(self, data, addr):
                    self.queue.put_nowait(data)
            
            self.transport, self.protocol = await loop.create_datagram_endpoint(
                lambda: UDPClientProtocol(self._receive_queue),
                remote_addr=(host, port)
            )
            self._remote_addr = (host, port)
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect UDP connection"""
        if self.transport:
            self.transport.close()
        self._connected = False
        self.transport = None
        self.protocol = None
        self._remote_addr = None
    
    async def send(self, data: bytes) -> bool:
        """Send data via UDP"""
        if not self._connected or not self.transport:
            return False
        try:
            self.transport.sendto(data)
            return True
        except Exception:
            self._connected = False
            return False
    
    async def receive(self) -> Optional[bytes]:
        """Receive data via UDP"""
        if not self._connected:
            return None
        try:
            data = await asyncio.wait_for(self._receive_queue.get(), timeout=0.1)
            return data
        except asyncio.TimeoutError:
            return None
        except Exception:
            self._connected = False
            return None
    
    def is_connected(self) -> bool:
        """Check UDP connection status"""
        return self._connected
    
    def get_latency(self) -> float:
        """Get UDP latency"""
        return self._latency