"""Performance and benchmark tests for OllamaPy."""

import pytest
import time
import threading
import sys
import gc
from unittest.mock import patch, Mock
from src.ollamapy.main import hello, greet


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    def test_function_call_performance(self):
        """Test basic function call performance."""
        iterations = 10000
        
        # Benchmark hello() function
        start_time = time.perf_counter()
        for _ in range(iterations):
            hello()
        end_time = time.perf_counter()
        
        hello_time = end_time - start_time
        hello_per_second = iterations / hello_time
        
        # Should be able to call hello() at least 50,000 times per second
        assert hello_per_second > 50000, f"hello() too slow: {hello_per_second:.0f} calls/sec"
        
        # Benchmark greet() function
        start_time = time.perf_counter()
        for i in range(iterations):
            greet(f"User{i}")
        end_time = time.perf_counter()
        
        greet_time = end_time - start_time
        greet_per_second = iterations / greet_time
        
        # Should be able to call greet() at least 30,000 times per second
        assert greet_per_second > 30000, f"greet() too slow: {greet_per_second:.0f} calls/sec"
        
        print(f"\nPerformance Results:")
        print(f"hello(): {hello_per_second:.0f} calls/sec ({hello_time:.4f}s total)")
        print(f"greet(): {greet_per_second:.0f} calls/sec ({greet_time:.4f}s total)")
    
    @pytest.mark.slow
    def test_sustained_performance(self):
        """Test sustained performance over longer period."""
        iterations = 100000
        batch_size = 10000
        times = []
        
        for batch in range(iterations // batch_size):
            start_time = time.perf_counter()
            
            for i in range(batch_size):
                hello()
                greet(f"Batch{batch}_User{i}")
            
            end_time = time.perf_counter()
            batch_time = end_time - start_time
            times.append(batch_time)
        
        # Calculate performance consistency
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        # Performance should be consistent (max shouldn't be more than 2x average)
        consistency_ratio = max_time / avg_time
        assert consistency_ratio < 2.0, f"Performance inconsistent: max/avg ratio = {consistency_ratio:.2f}"
        
        print(f"\nSustained Performance Results:")
        print(f"Average batch time: {avg_time:.4f}s")
        print(f"Min batch time: {min_time:.4f}s")
        print(f"Max batch time: {max_time:.4f}s")
        print(f"Consistency ratio: {consistency_ratio:.2f}")
    
    def test_memory_efficiency(self):
        """Test memory usage patterns."""
        import tracemalloc
        
        # Start tracing
        tracemalloc.start()
        
        # Baseline memory usage
        gc.collect()  # Force garbage collection
        snapshot1 = tracemalloc.take_snapshot()
        
        # Perform operations
        iterations = 10000
        results = []
        
        for i in range(iterations):
            result1 = hello()
            result2 = greet(f"User{i}")
            results.append((result1, result2))
        
        # Measure memory after operations
        snapshot2 = tracemalloc.take_snapshot()
        
        # Calculate memory usage
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        total_memory_mb = sum(stat.size_diff for stat in top_stats) / 1024 / 1024
        
        # Clean up
        tracemalloc.stop()
        del results
        gc.collect()
        
        # Memory usage should be reasonable (less than 10MB for 10k operations)
        assert total_memory_mb < 10, f"Excessive memory usage: {total_memory_mb:.2f}MB"
        
        print(f"\nMemory Usage: {total_memory_mb:.2f}MB for {iterations} operations")
    
    def test_string_handling_performance(self):
        """Test performance with various string sizes."""
        test_cases = [
            ("short", "Hi"),
            ("medium", "A" * 100),
            ("long", "B" * 1000),
            ("very_long", "C" * 10000),
        ]
        
        results = {}
        iterations = 1000
        
        for case_name, test_string in test_cases:
            start_time = time.perf_counter()
            
            for _ in range(iterations):
                result = greet(test_string)
                # Ensure the result is what we expect
                assert result == f"Hello, {test_string}!"
            
            end_time = time.perf_counter()
            case_time = end_time - start_time
            results[case_name] = case_time
        
        # Performance should scale reasonably with string length
        # Very long strings shouldn't be more than 10x slower than short strings
        performance_ratio = results["very_long"] / results["short"]
        assert performance_ratio < 10, f"Poor string scaling: {performance_ratio:.2f}x slower for long strings"
        
        print(f"\nString Handling Performance:")
        for case_name, case_time in results.items():
            calls_per_sec = iterations / case_time
            print(f"{case_name}: {calls_per_sec:.0f} calls/sec")


class TestConcurrencyPerformance:
    """Test performance under concurrent load."""
    
    def test_thread_safety_performance(self):
        """Test performance with multiple threads."""
        import concurrent.futures
        
        def worker(thread_id, iterations=1000):
            results = []
            start_time = time.perf_counter()
            
            for i in range(iterations):
                result1 = hello()
                result2 = greet(f"Thread{thread_id}_User{i}")
                results.append((result1, result2))
            
            end_time = time.perf_counter()
            return len(results), end_time - start_time
        
        # Test with multiple threads
        num_threads = 4
        iterations_per_thread = 1000
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            overall_start = time.perf_counter()
            
            for thread_id in range(num_threads):
                future = executor.submit(worker, thread_id, iterations_per_thread)
                futures.append(future)
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                result_count, thread_time = future.result()
                results.append((result_count, thread_time))
            
            overall_end = time.perf_counter()
        
        # Analyze results
        total_operations = sum(result[0] for result in results) * 2  # *2 for hello() and greet()
        overall_time = overall_end - overall_start
        overall_throughput = total_operations / overall_time
        
        # Should achieve good throughput with multiple threads
        expected_min_throughput = 50000  # operations per second
        assert overall_throughput > expected_min_throughput, \
            f"Poor concurrent throughput: {overall_throughput:.0f} ops/sec"
        
        print(f"\nConcurrency Performance:")
        print(f"Threads: {num_threads}")
        print(f"Total operations: {total_operations}")
        print(f"Overall time: {overall_time:.4f}s")
        print(f"Throughput: {overall_throughput:.0f} ops/sec")
    
    def test_load_handling(self):
        """Test handling of high load scenarios."""
        import queue
        import threading
        
        # Simulate a load scenario with producer-consumer pattern
        task_queue = queue.Queue()
        results_queue = queue.Queue()
        num_workers = 3
        tasks_per_worker = 1000
        
        def worker():
            while True:
                try:
                    task = task_queue.get(timeout=1)
                    if task is None:  # Poison pill
                        break
                    
                    # Simulate work
                    result1 = hello()
                    result2 = greet(f"Load_test_{task}")
                    results_queue.put((result1, result2))
                    task_queue.task_done()
                    
                except queue.Empty:
                    break
        
        # Start workers
        workers = []
        for _ in range(num_workers):
            worker_thread = threading.Thread(target=worker)
            worker_thread.start()
            workers.append(worker_thread)
        
        # Add tasks
        start_time = time.perf_counter()
        total_tasks = num_workers * tasks_per_worker
        
        for i in range(total_tasks):
            task_queue.put(i)
        
        # Wait for completion
        task_queue.join()
        
        # Stop workers
        for _ in range(num_workers):
            task_queue.put(None)
        
        for worker_thread in workers:
            worker_thread.join(timeout=5)
        
        end_time = time.perf_counter()
        
        # Collect results
        results_count = 0
        while not results_queue.empty():
            try:
                results_queue.get_nowait()
                results_count += 1
            except queue.Empty:
                break
        
        # Verify performance
        total_time = end_time - start_time
        throughput = results_count / total_time
        
        # Should handle load efficiently
        assert results_count == total_tasks, f"Lost tasks: {total_tasks - results_count}"
        assert throughput > 5000, f"Poor load handling throughput: {throughput:.0f} ops/sec"
        
        print(f"\nLoad Handling Performance:")
        print(f"Workers: {num_workers}")
        print(f"Tasks processed: {results_count}")
        print(f"Total time: {total_time:.4f}s")
        print(f"Throughput: {throughput:.0f} ops/sec")


class TestResourceUsage:
    """Test resource usage patterns."""
    
    def test_cpu_utilization(self):
        """Test CPU utilization patterns."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Baseline CPU usage
        cpu_before = process.cpu_percent()
        time.sleep(0.1)  # Let CPU measurement stabilize
        
        # Perform CPU-intensive operations
        iterations = 50000
        start_time = time.perf_counter()
        
        for i in range(iterations):
            hello()
            greet(f"CPU_test_{i}")
        
        end_time = time.perf_counter()
        
        # Measure CPU usage
        cpu_after = process.cpu_percent()
        execution_time = end_time - start_time
        
        # CPU utilization should be reasonable
        cpu_efficiency = iterations / execution_time / (cpu_after + 1)  # +1 to avoid division by zero
        
        print(f"\nCPU Utilization:")
        print(f"Execution time: {execution_time:.4f}s")
        print(f"CPU usage: {cpu_after:.2f}%")
        print(f"Operations per second: {iterations/execution_time:.0f}")
        print(f"CPU efficiency: {cpu_efficiency:.0f} ops/sec/cpu%")
    
    def test_garbage_collection_impact(self):
        """Test impact of garbage collection on performance."""
        import gc
        
        # Disable automatic garbage collection
        gc.disable()
        
        try:
            # Test without GC
            iterations = 10000
            
            start_time = time.perf_counter()
            for i in range(iterations):
                hello()
                greet(f"NoGC_{i}")
            no_gc_time = time.perf_counter() - start_time
            
            # Force garbage collection
            gc.collect()
            
            # Enable automatic garbage collection
            gc.enable()
            
            # Test with GC
            start_time = time.perf_counter()
            for i in range(iterations):
                hello()
                greet(f"WithGC_{i}")
            with_gc_time = time.perf_counter() - start_time
            
            # GC impact should be minimal for these simple functions
            gc_impact = (with_gc_time - no_gc_time) / no_gc_time
            
            assert gc_impact < 0.5, f"Excessive GC impact: {gc_impact:.2%}"
            
            print(f"\nGarbage Collection Impact:")
            print(f"Without GC: {no_gc_time:.4f}s")
            print(f"With GC: {with_gc_time:.4f}s")
            print(f"GC impact: {gc_impact:.2%}")
            
        finally:
            # Ensure GC is re-enabled
            gc.enable()
    
    @pytest.mark.slow
    def test_long_running_stability(self):
        """Test stability over long running periods."""
        duration_seconds = 10
        interval_seconds = 0.01
        
        start_time = time.time()
        call_count = 0
        error_count = 0
        
        while time.time() - start_time < duration_seconds:
            try:
                hello()
                greet(f"LongRun_{call_count}")
                call_count += 2  # Two function calls
                
                time.sleep(interval_seconds)
                
            except Exception as e:
                error_count += 1
                if error_count > 10:  # Too many errors
                    pytest.fail(f"Too many errors during long run: {e}")
        
        actual_duration = time.time() - start_time
        calls_per_second = call_count / actual_duration
        
        # Should maintain consistent performance over time
        assert error_count == 0, f"Errors during long run: {error_count}"
        assert calls_per_second > 100, f"Performance degradation: {calls_per_second:.1f} calls/sec"
        
        print(f"\nLong Running Stability:")
        print(f"Duration: {actual_duration:.1f}s")
        print(f"Total calls: {call_count}")
        print(f"Errors: {error_count}")
        print(f"Calls per second: {calls_per_second:.1f}")


@pytest.mark.slow
class TestStressTests:
    """Stress tests for edge conditions."""
    
    def test_extreme_string_sizes(self):
        """Test with extremely large strings."""
        # Test with very large string (1MB)
        large_string = "X" * (1024 * 1024)
        
        start_time = time.perf_counter()
        result = greet(large_string)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        
        # Should handle large strings reasonably
        assert result == f"Hello, {large_string}!"
        assert execution_time < 1.0, f"Too slow for large string: {execution_time:.4f}s"
        
        print(f"\nExtreme String Test:")
        print(f"String size: 1MB")
        print(f"Execution time: {execution_time:.4f}s")
    
    def test_rapid_fire_calls(self):
        """Test rapid succession of function calls."""
        iterations = 100000
        
        start_time = time.perf_counter()
        
        for i in range(iterations):
            hello()
            if i % 2 == 0:
                greet(str(i))
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        calls_per_second = (iterations + iterations//2) / execution_time  # iterations + iterations/2 calls
        
        # Should handle rapid fire calls efficiently
        assert calls_per_second > 100000, f"Poor rapid fire performance: {calls_per_second:.0f} calls/sec"
        
        print(f"\nRapid Fire Test:")
        print(f"Total calls: {iterations + iterations//2}")
        print(f"Execution time: {execution_time:.4f}s")
        print(f"Calls per second: {calls_per_second:.0f}")