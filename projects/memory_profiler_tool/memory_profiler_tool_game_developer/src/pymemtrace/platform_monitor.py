"""Platform-specific memory monitoring for games."""

import os
import sys
import platform
import psutil
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, List, Any, Callable
import threading
import time


class GamePlatform(Enum):
    """Supported game platforms."""
    PC_WINDOWS = "pc_windows"
    PC_LINUX = "pc_linux"
    PC_MAC = "pc_mac"
    MOBILE_IOS = "mobile_ios"
    MOBILE_ANDROID = "mobile_android"
    CONSOLE_PLAYSTATION = "console_playstation"
    CONSOLE_XBOX = "console_xbox"
    CONSOLE_SWITCH = "console_switch"
    WEB = "web"
    UNKNOWN = "unknown"


@dataclass
class PlatformMemoryLimits:
    """Memory limits for a specific platform."""
    platform: GamePlatform
    total_memory: int  # Total available memory in bytes
    recommended_limit: int  # Recommended memory usage limit
    critical_limit: int  # Critical memory limit before crashes
    reserved_system: int  # Memory reserved by system
    memory_banks: Optional[Dict[str, int]] = None  # Console memory banks


@dataclass
class PlatformMemoryStatus:
    """Current memory status for the platform."""
    platform: GamePlatform
    process_memory: int
    available_memory: int
    total_memory: int
    memory_percentage: float
    is_critical: bool
    recommendations: List[str]


class PlatformMemoryMonitor:
    """Monitors platform-specific memory constraints and usage."""
    
    # Platform memory configurations (in MB)
    PLATFORM_CONFIGS = {
        GamePlatform.PC_WINDOWS: {
            "min_memory": 2048,
            "recommended": 4096,
            "system_reserve": 1024
        },
        GamePlatform.PC_LINUX: {
            "min_memory": 2048,
            "recommended": 4096,
            "system_reserve": 512
        },
        GamePlatform.PC_MAC: {
            "min_memory": 4096,
            "recommended": 8192,
            "system_reserve": 2048
        },
        GamePlatform.MOBILE_IOS: {
            "min_memory": 512,
            "recommended": 1024,
            "system_reserve": 256,
            "crash_threshold": 0.85  # iOS kills apps at ~85% memory
        },
        GamePlatform.MOBILE_ANDROID: {
            "min_memory": 512,
            "recommended": 2048,
            "system_reserve": 512,
            "crash_threshold": 0.90
        },
        GamePlatform.CONSOLE_PLAYSTATION: {
            "min_memory": 4096,
            "recommended": 6144,
            "system_reserve": 2048,
            "memory_banks": {
                "main": 4096,
                "video": 2048
            }
        },
        GamePlatform.CONSOLE_XBOX: {
            "min_memory": 4096,
            "recommended": 6144,
            "system_reserve": 2048,
            "memory_banks": {
                "main": 4096,
                "shared": 2048
            }
        },
        GamePlatform.CONSOLE_SWITCH: {
            "min_memory": 2048,
            "recommended": 3072,
            "system_reserve": 1024
        },
        GamePlatform.WEB: {
            "min_memory": 256,
            "recommended": 512,
            "system_reserve": 128,
            "crash_threshold": 0.95
        }
    }
    
    def __init__(self):
        """Initialize the platform memory monitor."""
        self.current_platform = self._detect_platform()
        self.memory_limits = self._get_platform_limits()
        self._monitoring_enabled = False
        self._monitor_thread = None
        self._callbacks: List[Callable[[PlatformMemoryStatus], None]] = []
        self._lock = threading.Lock()
        self._process = psutil.Process()
        self._last_status = None
    
    def _detect_platform(self) -> GamePlatform:
        """Detect the current gaming platform."""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Check for mobile platforms (would need additional detection in real scenario)
        if hasattr(sys, 'getandroidapilevel'):
            return GamePlatform.MOBILE_ANDROID
        
        # Check for web platform
        if hasattr(sys, '_emscripten_info'):
            return GamePlatform.WEB
        
        # Check for desktop platforms
        if system == 'windows':
            return GamePlatform.PC_WINDOWS
        elif system == 'darwin':
            return GamePlatform.PC_MAC
        elif system == 'linux':
            # Could be Linux PC or console - need additional detection
            return GamePlatform.PC_LINUX
        
        return GamePlatform.UNKNOWN
    
    def _get_platform_limits(self) -> PlatformMemoryLimits:
        """Get memory limits for the current platform."""
        config = self.PLATFORM_CONFIGS.get(self.current_platform, {})
        
        # Get actual system memory
        mem_info = psutil.virtual_memory()
        total_mb = mem_info.total // (1024 * 1024)
        
        # Calculate limits based on platform config and actual memory
        min_memory = config.get("min_memory", 1024)
        recommended = min(config.get("recommended", 2048), total_mb * 0.7)
        system_reserve = config.get("system_reserve", 512)
        crash_threshold = config.get("crash_threshold", 0.95)
        
        return PlatformMemoryLimits(
            platform=self.current_platform,
            total_memory=mem_info.total,
            recommended_limit=int(recommended * 1024 * 1024),
            critical_limit=int(mem_info.total * crash_threshold),
            reserved_system=system_reserve * 1024 * 1024,
            memory_banks=config.get("memory_banks")
        )
    
    def get_current_status(self) -> PlatformMemoryStatus:
        """Get current platform memory status."""
        mem_info = psutil.virtual_memory()
        process_info = self._process.memory_info()
        
        process_memory = process_info.rss
        memory_percentage = (process_memory / mem_info.total) * 100
        
        # Check if memory usage is critical
        is_critical = process_memory >= self.memory_limits.critical_limit
        
        # Generate platform-specific recommendations
        recommendations = self._generate_recommendations(
            process_memory, mem_info.available, memory_percentage
        )
        
        status = PlatformMemoryStatus(
            platform=self.current_platform,
            process_memory=process_memory,
            available_memory=mem_info.available,
            total_memory=mem_info.total,
            memory_percentage=memory_percentage,
            is_critical=is_critical,
            recommendations=recommendations
        )
        
        with self._lock:
            self._last_status = status
        
        return status
    
    def _generate_recommendations(self, process_memory: int, 
                                available_memory: int,
                                memory_percentage: float) -> List[str]:
        """Generate platform-specific memory optimization recommendations."""
        recommendations = []
        
        # Platform-specific recommendations
        if self.current_platform == GamePlatform.MOBILE_IOS:
            if memory_percentage > 70:
                recommendations.append("Reduce texture resolution for iOS devices")
                recommendations.append("Enable aggressive asset streaming")
                recommendations.append("Implement memory pressure handling for iOS")
            if available_memory < 100 * 1024 * 1024:  # Less than 100MB
                recommendations.append("Critical: iOS may terminate app soon")
        
        elif self.current_platform == GamePlatform.MOBILE_ANDROID:
            if memory_percentage > 80:
                recommendations.append("Enable texture compression (ETC2/ASTC)")
                recommendations.append("Reduce simultaneous asset loading")
                recommendations.append("Consider lowering audio quality")
        
        elif self.current_platform in [GamePlatform.CONSOLE_PLAYSTATION, 
                                     GamePlatform.CONSOLE_XBOX]:
            if process_memory > self.memory_limits.recommended_limit:
                recommendations.append("Optimize for console memory banks")
                recommendations.append("Use platform-specific texture formats")
                recommendations.append("Enable hardware decompression")
        
        elif self.current_platform == GamePlatform.CONSOLE_SWITCH:
            if memory_percentage > 75:
                recommendations.append("Reduce asset quality for handheld mode")
                recommendations.append("Implement dynamic resolution scaling")
        
        elif self.current_platform == GamePlatform.WEB:
            if memory_percentage > 80:
                recommendations.append("Implement progressive asset loading")
                recommendations.append("Use WebGL compressed textures")
                recommendations.append("Reduce WebAssembly heap size")
        
        # General recommendations
        if process_memory > self.memory_limits.recommended_limit:
            recommendations.append("Memory usage exceeds platform recommendation")
            recommendations.append("Consider implementing asset LOD system")
        
        if available_memory < self.memory_limits.reserved_system:
            recommendations.append("System memory critically low")
            recommendations.append("Implement emergency asset purging")
        
        return recommendations
    
    def start_monitoring(self, interval: float = 1.0) -> None:
        """Start continuous memory monitoring."""
        with self._lock:
            if self._monitoring_enabled:
                return
            
            self._monitoring_enabled = True
            self._monitor_thread = threading.Thread(
                target=self._monitor_loop,
                args=(interval,),
                daemon=True
            )
            self._monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop memory monitoring."""
        with self._lock:
            self._monitoring_enabled = False
    
    def _monitor_loop(self, interval: float) -> None:
        """Main monitoring loop."""
        while self._monitoring_enabled:
            try:
                status = self.get_current_status()
                
                # Notify callbacks if critical
                if status.is_critical:
                    for callback in self._callbacks:
                        callback(status)
                
                time.sleep(interval)
            except Exception:
                # Continue monitoring even if error occurs
                time.sleep(interval)
    
    def add_status_callback(self, callback: Callable[[PlatformMemoryStatus], None]) -> None:
        """Add a callback for memory status updates."""
        self._callbacks.append(callback)
    
    def get_platform_optimization_guide(self) -> Dict[str, Any]:
        """Get platform-specific optimization guidelines."""
        guide = {
            "platform": self.current_platform.value,
            "texture_formats": [],
            "audio_formats": [],
            "memory_techniques": [],
            "special_considerations": []
        }
        
        if self.current_platform == GamePlatform.PC_WINDOWS:
            guide["texture_formats"] = ["DXT1", "DXT5", "BC7"]
            guide["audio_formats"] = ["OGG", "MP3"]
            guide["memory_techniques"] = ["Virtual texturing", "Asset streaming"]
        
        elif self.current_platform == GamePlatform.MOBILE_IOS:
            guide["texture_formats"] = ["PVRTC", "ASTC"]
            guide["audio_formats"] = ["AAC", "CAF"]
            guide["memory_techniques"] = ["Texture atlasing", "Aggressive LOD"]
            guide["special_considerations"] = [
                "Memory pressure notifications",
                "Background app termination",
                "Metal API optimizations"
            ]
        
        elif self.current_platform == GamePlatform.MOBILE_ANDROID:
            guide["texture_formats"] = ["ETC2", "ASTC"]
            guide["audio_formats"] = ["OGG", "AAC"]
            guide["memory_techniques"] = ["On-demand loading", "Memory mapping"]
            guide["special_considerations"] = [
                "Device fragmentation",
                "Variable RAM sizes",
                "Background service limits"
            ]
        
        elif self.current_platform in [GamePlatform.CONSOLE_PLAYSTATION,
                                     GamePlatform.CONSOLE_XBOX]:
            guide["texture_formats"] = ["BC7", "Platform-specific"]
            guide["audio_formats"] = ["Platform-specific codecs"]
            guide["memory_techniques"] = ["Memory bank optimization", "Hardware decompression"]
            guide["special_considerations"] = [
                "Fixed hardware specs",
                "Certification requirements",
                "Platform-specific APIs"
            ]
        
        return guide
    
    def compare_platforms(self, target_platforms: List[GamePlatform]) -> Dict[str, Any]:
        """Compare memory constraints across platforms."""
        comparison = {}
        
        for platform in target_platforms:
            config = self.PLATFORM_CONFIGS.get(platform, {})
            comparison[platform.value] = {
                "min_memory_mb": config.get("min_memory", 0),
                "recommended_mb": config.get("recommended", 0),
                "system_reserve_mb": config.get("system_reserve", 0),
                "has_memory_banks": "memory_banks" in config,
                "crash_threshold": config.get("crash_threshold", 0.95) * 100
            }
        
        return comparison
    
    def estimate_platform_compatibility(self, memory_usage: int) -> Dict[str, bool]:
        """Estimate if current memory usage is compatible with other platforms."""
        compatibility = {}
        
        for platform, config in self.PLATFORM_CONFIGS.items():
            min_memory = config.get("min_memory", 1024) * 1024 * 1024
            recommended = config.get("recommended", 2048) * 1024 * 1024
            
            compatibility[platform.value] = {
                "meets_minimum": memory_usage <= min_memory,
                "meets_recommended": memory_usage <= recommended,
                "optimization_needed": memory_usage > recommended
            }
        
        return compatibility
    
    def get_memory_bank_usage(self) -> Optional[Dict[str, int]]:
        """Get memory bank usage for console platforms."""
        if not self.memory_limits.memory_banks:
            return None
        
        # Simulate memory bank usage (would need platform SDK in real scenario)
        total_memory = self._process.memory_info().rss
        
        bank_usage = {}
        if self.current_platform == GamePlatform.CONSOLE_PLAYSTATION:
            bank_usage["main"] = int(total_memory * 0.7)
            bank_usage["video"] = int(total_memory * 0.3)
        elif self.current_platform == GamePlatform.CONSOLE_XBOX:
            bank_usage["main"] = int(total_memory * 0.6)
            bank_usage["shared"] = int(total_memory * 0.4)
        
        return bank_usage