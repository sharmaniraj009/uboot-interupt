#!/usr/bin/env python3
"""
Aggressive U-Boot Interrupt Script
Continuously spams interrupt characters to force U-Boot entry
"""

import serial
import time
import sys
import threading
import signal

class AggressiveUBootInterrupter:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.running = False
        self.interrupt_thread = None
        
    def connect(self):
        """Establish serial connection with minimal timeout for speed"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.01,  # Very short timeout for aggressive mode
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            # Flush any existing data
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()
            print(f"Connected to {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Close connection"""
        self.running = False
        if self.interrupt_thread and self.interrupt_thread.is_alive():
            self.interrupt_thread.join(timeout=1)
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("\nSerial connection closed")
    
    def aggressive_spam(self, duration=30):
        """
        Aggressively spam interrupt characters
        Uses multiple interrupt methods simultaneously
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            print("Serial connection not available")
            return False
        
        print(f"AGGRESSIVE MODE: Spamming interrupts for {duration} seconds...")
        print("Press Ctrl+C to stop early")
        
        # Multiple interrupt characters that different U-Boot versions respond to
        interrupt_chars = [
            b' ',      # Space (most common)
            b'\r',     # Carriage return
            b'\n',     # Newline
            b'\x03',   # Ctrl+C
            b'\x1b',   # ESC
            b'q',      # 'q' key
            b's',      # 's' key (sometimes used)
        ]
        
        start_time = time.time()
        char_index = 0
        
        try:
            while time.time() - start_time < duration and self.running:
                # Rapid fire different characters
                for _ in range(10):  # Send 10 of each character type
                    char = interrupt_chars[char_index % len(interrupt_chars)]
                    self.serial_conn.write(char)
                
                # Flush immediately for speed
                self.serial_conn.flush()
                
                # Cycle through different characters
                char_index += 1
                
                # Very short delay - just enough to not overwhelm
                time.sleep(0.001)  # 1ms delay
                
                # Check for any response
                if self.serial_conn.in_waiting > 0:
                    response = self.serial_conn.read(self.serial_conn.in_waiting)
                    try:
                        decoded = response.decode('utf-8', errors='ignore')
                        print(f"\nRESPONSE DETECTED: {repr(decoded)}")
                        # Look for U-Boot prompt indicators
                        if any(indicator in decoded.lower() for indicator in 
                               ['=>', 'u-boot>', '#', 'uboot>', 'boot>']):
                            print("SUCCESS: U-Boot prompt detected!")
                            return True
                    except:
                        pass
        
        except KeyboardInterrupt:
            print("\nInterrupt spam stopped by user")
            return False
        
        print(f"\nSpam completed after {duration} seconds")
        return False
    
    def continuous_spam_with_monitor(self):
        """
        Continuous spam mode with real-time monitoring
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            return False
        
        print("CONTINUOUS SPAM MODE - Will spam until U-Boot prompt detected")
        print("Press Ctrl+C to stop")
        
        def spam_worker():
            """Worker thread for continuous spamming"""
            spam_chars = b' \r\n\x03'  # Space, CR, LF, Ctrl+C
            char_index = 0
            
            while self.running:
                try:
                    # Send burst of characters
                    for _ in range(5):
                        if not self.running:
                            break
                        char = spam_chars[char_index % len(spam_chars)]
                        self.serial_conn.write(bytes([char]))
                        char_index += 1
                    
                    self.serial_conn.flush()
                    time.sleep(0.002)  # 2ms between bursts
                    
                except:
                    break
        
        # Start spam thread
        self.running = True
        self.interrupt_thread = threading.Thread(target=spam_worker, daemon=True)
        self.interrupt_thread.start()
        
        # Monitor for responses
        try:
            buffer = ""
            while self.running:
                if self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.read(self.serial_conn.in_waiting)
                    try:
                        decoded = data.decode('utf-8', errors='ignore')
                        print(decoded, end='', flush=True)
                        buffer += decoded.lower()
                        
                        # Check for success indicators
                        success_indicators = [
                            '=>', 'u-boot>', 'uboot>', 'boot>',
                            '# ', 'login:', 'stopped in',
                            'hit any key', 'press any key'
                        ]
                        
                        for indicator in success_indicators:
                            if indicator in buffer:
                                print(f"\n\nSUCCESS: Detected '{indicator}'")
                                print("U-Boot interrupt successful!")
                                self.running = False
                                return True
                        
                        # Keep buffer manageable
                        if len(buffer) > 500:
                            buffer = buffer[-250:]
                            
                    except:
                        pass
                
                time.sleep(0.001)
                
        except KeyboardInterrupt:
            print("\nStopped by user")
        
        self.running = False
        return False
    
    def nuclear_option(self, duration=10):
        """
        Nuclear option - maximum aggression
        Sends everything possible as fast as possible
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            return False
        
        print(f"NUCLEAR OPTION: Maximum aggression for {duration} seconds!")
        print("WARNING: This will flood the serial port")
        
        # Every possible interrupt character
        nuclear_payload = (b' ' * 50 + b'\r' * 10 + b'\n' * 10 + 
                          b'\x03' * 5 + b'\x1b' * 5 + b'q' * 10 + 
                          b's' * 10 + b'a' * 10)
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                # Send the entire payload
                self.serial_conn.write(nuclear_payload)
                self.serial_conn.flush()
                
                # Check for immediate response
                if self.serial_conn.in_waiting > 0:
                    response = self.serial_conn.read_all()
                    try:
                        decoded = response.decode('utf-8', errors='ignore')
                        if any(x in decoded.lower() for x in ['=>', 'u-boot>', '#']):
                            print(f"\nNUCLEAR SUCCESS: {decoded}")
                            return True
                    except:
                        pass
                
                # Minimal delay
                time.sleep(0.005)  # 5ms
                
        except KeyboardInterrupt:
            print("\nNuclear option stopped")
        
        return False


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down...")
    sys.exit(0)


def main():
    import argparse
    
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(description='Aggressive U-Boot Interrupt')
    parser.add_argument('--port', '-p', default='/dev/ttyUSB0',
                       help='Serial port')
    parser.add_argument('--baudrate', '-b', type=int, default=115200,
                       help='Baud rate')
    parser.add_argument('--mode', '-m', choices=['spam', 'continuous', 'nuclear'],
                       default='continuous', help='Interrupt mode')
    parser.add_argument('--duration', '-d', type=int, default=30,
                       help='Duration for spam/nuclear modes')
    
    args = parser.parse_args()
    
    interrupter = AggressiveUBootInterrupter(args.port, args.baudrate)
    
    if not interrupter.connect():
        sys.exit(1)
    
    try:
        if args.mode == 'spam':
            success = interrupter.aggressive_spam(args.duration)
        elif args.mode == 'nuclear':
            success = interrupter.nuclear_option(args.duration)
        else:  # continuous
            success = interrupter.continuous_spam_with_monitor()
        
        if success:
            print("\n U-Boot interrupt successful!")
            print("You should now be at the U-Boot prompt")
        else:
            print("\n Could not confirm U-Boot interrupt")
            
    finally:
        interrupter.disconnect()


if __name__ == "__main__":
    main()
