"""
Cost Anomaly Detection - Identify where tokens are "leaking"
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean, stdev

LOGS_DIR = Path.home() / ".openclaw" / "workspace" / ".learnings"
COST_LOG = LOGS_DIR / "COST_LOG.json"
ANOMALY_REPORT = LOGS_DIR / "COST_ANOMALIES.json"


class AnomalyDetector:
    """Detect cost anomalies by area"""
    
    @staticmethod
    def load_costs():
        """Load all cost logs"""
        if not COST_LOG.exists():
            return []
        
        with open(COST_LOG) as f:
            return json.load(f)
    
    @staticmethod
    def group_by_type(entries):
        """Group costs by type"""
        grouped = {}
        
        for entry in entries:
            cost_type = entry['type']
            if cost_type not in grouped:
                grouped[cost_type] = []
            grouped[cost_type].append(entry)
        
        return grouped
    
    @staticmethod
    def get_daily_average(entries, days=7):
        """Calculate average daily cost for past N days"""
        if not entries:
            return 0, 0
        
        today = datetime.now().date()
        daily_costs = {}
        
        for entry in entries:
            entry_date = datetime.fromisoformat(entry['timestamp']).date()
            if (today - entry_date).days < days:
                if entry_date not in daily_costs:
                    daily_costs[entry_date] = 0
                daily_costs[entry_date] += entry['cost']
        
        if not daily_costs:
            return 0, 0
        
        costs = list(daily_costs.values())
        avg = mean(costs)
        
        # Standard deviation (or 0 if only 1 data point)
        std = stdev(costs) if len(costs) > 1 else 0
        
        return avg, std
    
    @staticmethod
    def get_today_cost(entries):
        """Get total cost today"""
        today = datetime.now().date()
        return sum(
            e['cost'] for e in entries
            if datetime.fromisoformat(e['timestamp']).date() == today
        )
    
    @staticmethod
    def detect_anomalies():
        """
        Detect cost anomalies.
        Returns: List of anomalies with severity
        """
        entries = AnomalyDetector.load_costs()
        grouped = AnomalyDetector.group_by_type(entries)
        
        anomalies = []
        today = datetime.now().date()
        
        for cost_type, type_entries in grouped.items():
            # Calculate baseline
            avg, std = AnomalyDetector.get_daily_average(type_entries, days=7)
            
            # Get today's cost for this type
            today_cost = sum(
                e['cost'] for e in type_entries
                if datetime.fromisoformat(e['timestamp']).date() == today
            )
            
            if avg == 0:
                # No baseline yet
                if today_cost > 0.01:  # Arbitrary threshold
                    anomalies.append({
                        'type': cost_type,
                        'severity': 'warning',
                        'today_cost': today_cost,
                        'baseline': 0,
                        'deviation': 'No baseline (new feature)',
                        'count': len([e for e in type_entries if datetime.fromisoformat(e['timestamp']).date() == today])
                    })
            else:
                # Compare to baseline
                threshold = avg + (2 * std) if std > 0 else avg * 1.5
                
                if today_cost > threshold:
                    deviation_pct = ((today_cost - avg) / avg) * 100
                    
                    severity = 'error' if deviation_pct > 100 else 'warning'
                    
                    anomalies.append({
                        'type': cost_type,
                        'severity': severity,
                        'today_cost': today_cost,
                        'baseline_avg': avg,
                        'deviation_pct': deviation_pct,
                        'threshold': threshold,
                        'count': len([e for e in type_entries if datetime.fromisoformat(e['timestamp']).date() == today])
                    })
        
        return anomalies
    
    @staticmethod
    def get_cost_breakdown_today():
        """Get detailed cost breakdown for today"""
        entries = AnomalyDetector.load_costs()
        today = datetime.now().date()
        
        today_entries = [
            e for e in entries
            if datetime.fromisoformat(e['timestamp']).date() == today
        ]
        
        breakdown = {}
        for entry in today_entries:
            cost_type = entry['type']
            if cost_type not in breakdown:
                breakdown[cost_type] = {
                    'total_cost': 0,
                    'count': 0,
                    'avg_cost': 0,
                    'entries': []
                }
            
            breakdown[cost_type]['total_cost'] += entry['cost']
            breakdown[cost_type]['count'] += 1
            breakdown[cost_type]['entries'].append({
                'timestamp': entry['timestamp'],
                'cost': entry['cost'],
                'details': entry.get('details', {})
            })
        
        # Calculate averages
        for cost_type in breakdown:
            if breakdown[cost_type]['count'] > 0:
                breakdown[cost_type]['avg_cost'] = (
                    breakdown[cost_type]['total_cost'] / breakdown[cost_type]['count']
                )
        
        return breakdown
    
    @staticmethod
    def get_cost_by_area():
        """
        Get cost attribution by area/feature.
        Looks at 'details' field to identify root cause.
        """
        entries = AnomalyDetector.load_costs()
        today = datetime.now().date()
        
        today_entries = [
            e for e in entries
            if datetime.fromisoformat(e['timestamp']).date() == today
        ]
        
        by_area = {}
        
        for entry in today_entries:
            details = entry.get('details', {})
            
            # Extract area from details
            area = None
            if 'subject' in details:
                area = f"Email: {details['subject'][:30]}"
            elif 'task' in details:
                area = f"Task: {details['task'][:30]}"
            elif 'from' in details:
                area = f"Email from: {details['from']}"
            else:
                area = entry['type']
            
            if area not in by_area:
                by_area[area] = {'cost': 0, 'count': 0}
            
            by_area[area]['cost'] += entry['cost']
            by_area[area]['count'] += 1
        
        # Sort by cost
        return sorted(
            by_area.items(),
            key=lambda x: x[1]['cost'],
            reverse=True
        )
    
    @staticmethod
    def generate_report():
        """Generate anomaly report"""
        anomalies = AnomalyDetector.detect_anomalies()
        breakdown = AnomalyDetector.get_cost_breakdown_today()
        by_area = AnomalyDetector.get_cost_by_area()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'anomalies': anomalies,
            'breakdown_today': breakdown,
            'cost_by_area': [
                {'area': area, 'cost': data['cost'], 'count': data['count']}
                for area, data in by_area[:10]  # Top 10
            ],
            'total_today': sum(e['cost'] for e in AnomalyDetector.load_costs() 
                             if datetime.fromisoformat(e['timestamp']).date() == datetime.now().date()),
            'alerts': []
        }
        
        # Generate alerts
        for anomaly in anomalies:
            if anomaly['severity'] == 'error':
                report['alerts'].append({
                    'level': 'ERROR',
                    'message': f"{anomaly['type']} cost is {anomaly['deviation_pct']:.0f}% above baseline ({anomaly['count']} operations)"
                })
            elif anomaly['severity'] == 'warning':
                report['alerts'].append({
                    'level': 'WARNING',
                    'message': f"{anomaly['type']} may be over baseline (today: ${anomaly['today_cost']:.4f})"
                })
        
        # Save report
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(ANOMALY_REPORT, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report


if __name__ == "__main__":
    print("[*] Cost Anomaly Detection\n")
    
    report = AnomalyDetector.generate_report()
    
    print(f"Total cost today: ${report['total_today']:.4f}\n")
    
    print("Anomalies detected:")
    if report['anomalies']:
        for anomaly in report['anomalies']:
            print(f"  - {anomaly['type']}: {anomaly['severity']}")
    else:
        print("  None (costs normal)")
    
    print("\nTop cost drivers:")
    for area, cost, count in report['cost_by_area']:
        print(f"  - {area}: ${cost:.4f} ({count} ops)")
    
    print("\nAlerts:")
    if report['alerts']:
        for alert in report['alerts']:
            print(f"  [{alert['level']}] {alert['message']}")
    else:
        print("  None")
