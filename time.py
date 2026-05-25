import matplotlib.pyplot as plt
import numpy as np
import statistics
import csv

def analyze_timestamp_intervals_simple(file_path, delimiter=None):
    """
    Analyze timestamp intervals in a trajectory file (simplified version)
    
    Parameters:
    file_path: Path to the trajectory file
    delimiter: File delimiter, default is None (auto-detect)
    """
    
    print(f"Reading file: {file_path}")
    
    # Read timestamp data
    timestamps = []
    
    try:
        with open(file_path, 'r') as f:
            # Try to auto-detect delimiter
            if delimiter is None:
                # Read first line to detect delimiter
                first_line = f.readline()
                f.seek(0)  # Return to file beginning
                
                # Common delimiter detection
                if ',' in first_line:
                    delimiter = ','
                elif '\t' in first_line:
                    delimiter = '\t'
                elif ';' in first_line:
                    delimiter = ';'
                elif ' ' in first_line and len(first_line.split()) > 1:
                    delimiter = None  # Use split() for spaces
                else:
                    # If no obvious delimiter, might be space or tab
                    delimiter = None
                    print("Warning: Cannot auto-detect delimiter, trying space splitting")
            
            # Read all lines
            for line in f:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                # Split line
                if delimiter:
                    parts = line.split(delimiter)
                else:
                    parts = line.split()  # Default: split by whitespace
                
                if parts:  # Ensure line is not empty
                    try:
                        timestamp = float(parts[0])  # First column as timestamp
                        timestamps.append(timestamp)
                    except ValueError:
                        print(f"Warning: Cannot parse timestamp: {parts[0]}")
    
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")
        return
    except Exception as e:
        print(f"Failed to read file: {e}")
        return
    
    if len(timestamps) < 2:
        print("Error: Insufficient timestamps to calculate intervals")
        return
    
    total_points = len(timestamps)
    print(f"Successfully read {total_points} data points")
    print(f"Timestamp range: {timestamps[0]} to {timestamps[-1]}")
    
    # Calculate time intervals
    intervals = []
    for i in range(1, len(timestamps)):
        interval = timestamps[i] - timestamps[i-1]
        intervals.append(interval)
    
    # Calculate statistics
    max_interval = max(intervals)
    min_interval = min(intervals)
    mean_interval = sum(intervals) / len(intervals)
    
    # Calculate standard deviation
    try:
        # Use statistics module (Python 3.4+)
        std_interval = statistics.stdev(intervals)
    except ImportError:
        # Manual calculation
        variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
        std_interval = variance ** 0.5
    
    # Output results
    print("\n" + "="*50)
    print("Timestamp Interval Statistics")
    print("="*50)
    print(f"Maximum interval: {max_interval:.6f} seconds")
    print(f"Minimum interval: {min_interval:.6f} seconds")
    print(f"Mean interval: {mean_interval:.6f} seconds")
    print(f"Interval std dev: {std_interval:.6f} seconds")
    print(f"Data points: {total_points}")
    print(f"Intervals: {len(intervals)}")
    print("="*50)
    
    # Check stability
    if mean_interval > 0:
        cv = (std_interval / mean_interval) * 100
        is_stable = cv < 5
        print(f"Coefficient of variation (CV): {cv:.2f}%")
        print(f"Sampling stability: {'Stable' if is_stable else 'Unstable'}")
    else:
        print("Warning: Mean interval is 0 or negative, cannot calculate stability")
    
    # Create plots
    plt.figure(figsize=(12, 8))
    
    # 1. Time interval sequence plot
    plt.subplot(2, 1, 1)
    plt.plot(range(len(intervals)), intervals, 'b-', linewidth=1, alpha=0.7)
    plt.axhline(y=mean_interval, color='r', linestyle='--', label=f'Mean: {mean_interval:.3f}s')
    plt.axhline(y=mean_interval + std_interval, color='g', linestyle=':', alpha=0.5)
    plt.axhline(y=mean_interval - std_interval, color='g', linestyle=':', alpha=0.5, label='±1 Std Dev')
    plt.xlabel('Sample Index')
    plt.ylabel('Time Interval (s)')
    plt.title('Time Interval Sequence')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 2. Time interval histogram
    plt.subplot(2, 1, 2)
    # Determine appropriate number of bins
    n_bins = min(30, len(intervals) // 5)
    if n_bins < 5:
        n_bins = 5
    
    plt.hist(intervals, bins=n_bins, edgecolor='black', alpha=0.7)
    plt.axvline(mean_interval, color='r', linestyle='--', label=f'Mean: {mean_interval:.3f}s')
    plt.xlabel('Time Interval (s)')
    plt.ylabel('Frequency')
    plt.title('Time Interval Distribution Histogram')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("3.png",dpi=300)
    
    # Detect abnormal intervals
    if std_interval > 0:
        threshold = mean_interval + 3 * std_interval
        outliers = [(i, intervals[i]) for i in range(len(intervals)) if intervals[i] > threshold]
        
        if outliers:
            print(f"\nFound {len(outliers)} abnormal intervals (> mean + 3σ):")
            for idx, value in outliers[:10]:  # Show only first 10
                print(f"  Index {idx}: interval = {value:.6f} seconds")
            if len(outliers) > 10:
                print(f"  ... and {len(outliers) - 10} more outliers not shown")
        else:
            print("\nNo abnormal intervals detected")
    
    return {
        'timestamps': timestamps,
        'intervals': intervals,
        'stats': {
            'max': max_interval,
            'min': min_interval,
            'mean': mean_interval,
            'std': std_interval,
            'total_points': total_points
        }
    }

# Usage example
if __name__ == "__main__":
    # Set file path
    file_path = "20260206_140109_Debug.txt"  # Replace with your file path
    
    # If file has special delimiter, specify it, e.g., delimiter=','
    # If None, auto-detect
    result = analyze_timestamp_intervals_simple(
        file_path=file_path,
        delimiter=None  # Auto-detect delimiter
    )

    