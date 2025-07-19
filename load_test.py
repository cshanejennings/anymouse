#!/usr/bin/env python3
"""
Load testing script for Anymouse API.
Tests the 10-100 requests/sec requirement with various scenarios.
"""

import asyncio
import aiohttp
import time
import json
import argparse
import statistics
from dataclasses import dataclass
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import pandas as pd


@dataclass
class TestResult:
    """Container for test result metrics."""
    timestamp: float
    status_code: int
    response_time: float
    request_size: int
    response_size: int
    error: str = None


class LoadTester:
    """Async load tester for Anymouse API."""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.results: List[TestResult] = []
    
    async def make_request(self, session: aiohttp.ClientSession, payload: Dict[str, Any]) -> TestResult:
        """Make a single API request and record metrics."""
        start_time = time.time()
        request_data = json.dumps(payload)
        request_size = len(request_data.encode('utf-8'))
        
        try:
            async with session.post(
                f"{self.api_url}/anonymize",
                json=payload,
                headers={"X-API-Key": self.api_key},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_text = await response.text()
                response_time = time.time() - start_time
                response_size = len(response_text.encode('utf-8'))
                
                return TestResult(
                    timestamp=start_time,
                    status_code=response.status,
                    response_time=response_time,
                    request_size=request_size,
                    response_size=response_size
                )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                timestamp=start_time,
                status_code=0,
                response_time=response_time,
                request_size=request_size,
                response_size=0,
                error=str(e)
            )
    
    async def run_load_test(self, requests_per_second: int, duration_seconds: int, payload_type: str = "small"):
        """Run load test with specified RPS for given duration."""
        print(f"🚀 Starting load test: {requests_per_second} RPS for {duration_seconds}s with {payload_type} payloads")
        
        # Generate test payloads
        payloads = self._generate_payloads(payload_type)
        
        # Calculate request interval
        interval = 1.0 / requests_per_second
        
        # Run test
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            request_count = 0
            
            while time.time() < end_time:
                # Select payload (round-robin)
                payload = payloads[request_count % len(payloads)]
                
                # Create and schedule task
                task = asyncio.create_task(self.make_request(session, payload))
                tasks.append(task)
                request_count += 1
                
                # Wait for next request time
                next_request_time = start_time + (request_count * interval)
                current_time = time.time()
                if next_request_time > current_time:
                    await asyncio.sleep(next_request_time - current_time)
            
            # Wait for all requests to complete
            print(f"⏳ Waiting for {len(tasks)} requests to complete...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, TestResult):
                    self.results.append(result)
                else:
                    # Handle exceptions
                    self.results.append(TestResult(
                        timestamp=time.time(),
                        status_code=0,
                        response_time=0,
                        request_size=0,
                        response_size=0,
                        error=str(result)
                    ))
        
        print(f"✅ Load test completed: {len(self.results)} requests processed")
    
    def _generate_payloads(self, payload_type: str) -> List[Dict[str, Any]]:
        """Generate test payloads of different sizes."""
        if payload_type == "small":
            return [
                {"payload": "Hello Dr. Smith"},
                {"payload": "Message for Jane Doe"},
                {"payload": "Appointment with Dr. Johnson"},
                {"payload": "Call from Mary Wilson"},
                {"payload": "Note about John Davis"}
            ]
        elif payload_type == "medium":
            base_text = "Hello Dr. Smith, I have a question about my prescription. Please call me back at your earliest convenience. Thank you, Jane Doe."
            return [
                {"payload": base_text},
                {"payload": base_text.replace("Dr. Smith", "Dr. Johnson").replace("Jane Doe", "Mary Wilson")},
                {"payload": base_text.replace("Dr. Smith", "Dr. Brown").replace("Jane Doe", "John Davis")},
                {"payload": base_text + " Additional notes about the patient's condition and medical history."},
                {"payload": base_text + " Please review the attached lab results and imaging studies."}
            ]
        elif payload_type == "large":
            # Large email-like payloads
            email_template = """
            From: {sender}
            To: medical-staff@clinic.com
            Subject: Patient Consultation Request
            
            Dear {doctor},
            
            I hope this message finds you well. I am writing to request a consultation regarding my recent medical concerns. Over the past few weeks, I have been experiencing some symptoms that I believe warrant professional medical attention.
            
            My current symptoms include:
            - Persistent headaches that occur mainly in the morning
            - Occasional dizziness when standing up quickly
            - Mild fatigue throughout the day
            - Some difficulty concentrating during work hours
            
            I have been taking the medications you prescribed during my last visit on {date}, but I'm not sure if they are helping with these new symptoms. I would appreciate the opportunity to discuss these concerns with you at your earliest convenience.
            
            Please let me know when you might have an opening in your schedule. I am flexible with timing and can accommodate most weekday appointments.
            
            Thank you for your time and continued care.
            
            Best regards,
            {patient}
            
            Contact Information:
            Phone: (555) 123-4567
            Email: patient@email.com
            Address: 123 Main Street, Anytown, State 12345
            """
            
            return [
                {"payload": email_template.format(
                    sender="jane.doe@email.com",
                    doctor="Dr. Smith",
                    date="March 15, 2024",
                    patient="Jane Doe"
                )},
                {"payload": email_template.format(
                    sender="john.wilson@email.com", 
                    doctor="Dr. Johnson",
                    date="March 20, 2024",
                    patient="John Wilson"
                )},
                {"payload": email_template.format(
                    sender="mary.davis@email.com",
                    doctor="Dr. Brown", 
                    date="March 25, 2024",
                    patient="Mary Davis"
                )}
            ]
        else:
            raise ValueError(f"Unknown payload type: {payload_type}")
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze test results and return metrics."""
        if not self.results:
            return {}
        
        # Filter successful requests
        successful = [r for r in self.results if r.status_code == 200]
        failed = [r for r in self.results if r.status_code != 200]
        
        # Calculate metrics
        response_times = [r.response_time for r in successful]
        
        metrics = {
            "total_requests": len(self.results),
            "successful_requests": len(successful),
            "failed_requests": len(failed),
            "success_rate": len(successful) / len(self.results) * 100 if self.results else 0,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "p50_response_time": statistics.median(response_times) if response_times else 0,
            "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else 0,
            "p99_response_time": statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "total_duration": max(r.timestamp for r in self.results) - min(r.timestamp for r in self.results) if self.results else 0,
            "actual_rps": len(self.results) / (max(r.timestamp for r in self.results) - min(r.timestamp for r in self.results)) if len(self.results) > 1 else 0
        }
        
        return metrics
    
    def print_results(self):
        """Print formatted test results."""
        metrics = self.analyze_results()
        
        print("\n" + "="*60)
        print("📊 LOAD TEST RESULTS")
        print("="*60)
        print(f"Total Requests:      {metrics['total_requests']:,}")
        print(f"Successful:          {metrics['successful_requests']:,} ({metrics['success_rate']:.1f}%)")
        print(f"Failed:              {metrics['failed_requests']:,}")
        print(f"Actual RPS:          {metrics['actual_rps']:.1f}")
        print(f"Test Duration:       {metrics['total_duration']:.1f}s")
        print()
        print("Response Times:")
        print(f"  Average:           {metrics['avg_response_time']*1000:.0f}ms")
        print(f"  Median (P50):      {metrics['p50_response_time']*1000:.0f}ms")
        print(f"  P95:               {metrics['p95_response_time']*1000:.0f}ms")
        print(f"  P99:               {metrics['p99_response_time']*1000:.0f}ms")
        print(f"  Min:               {metrics['min_response_time']*1000:.0f}ms")
        print(f"  Max:               {metrics['max_response_time']*1000:.0f}ms")
        print("="*60)
        
        # Performance assessment
        if metrics['success_rate'] >= 99 and metrics['p95_response_time'] < 1.0:
            print("✅ EXCELLENT: Meets performance requirements")
        elif metrics['success_rate'] >= 95 and metrics['p95_response_time'] < 2.0:
            print("✅ GOOD: Acceptable performance")
        elif metrics['success_rate'] >= 90:
            print("⚠️  WARNING: Performance degraded but functional")
        else:
            print("❌ POOR: Performance requirements not met")
    
    def save_results(self, filename: str):
        """Save detailed results to CSV for analysis."""
        df = pd.DataFrame([
            {
                'timestamp': r.timestamp,
                'status_code': r.status_code,
                'response_time_ms': r.response_time * 1000,
                'request_size_bytes': r.request_size,
                'response_size_bytes': r.response_size,
                'error': r.error
            }
            for r in self.results
        ])
        df.to_csv(filename, index=False)
        print(f"📁 Results saved to {filename}")


async def main():
    """Main load testing function."""
    parser = argparse.ArgumentParser(description="Load test Anymouse API")
    parser.add_argument("--api-url", required=True, help="API Gateway URL")
    parser.add_argument("--api-key", required=True, help="API key")
    parser.add_argument("--rps", type=int, default=50, help="Requests per second")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--payload-type", choices=["small", "medium", "large"], default="medium", help="Payload size")
    parser.add_argument("--output", help="CSV file to save results")
    
    args = parser.parse_args()
    
    # Validate RPS requirement
    if args.rps > 100:
        print("⚠️  WARNING: Testing beyond the 100 RPS design requirement")
    
    # Run load test
    tester = LoadTester(args.api_url, args.api_key)
    await tester.run_load_test(args.rps, args.duration, args.payload_type)
    
    # Analyze and display results
    tester.print_results()
    
    # Save results if requested
    if args.output:
        tester.save_results(args.output)


if __name__ == "__main__":
    # Install required packages if missing
    try:
        import aiohttp
        import matplotlib.pyplot as plt
        import pandas as pd
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("📦 Install with: pip install aiohttp matplotlib pandas")
        exit(1)
    
    asyncio.run(main())