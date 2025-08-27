from django.db import models

class Log(models.Model):
    EVENT_TYPES = [
        ("LOGIN_FAIL", "Login Failed"),
        ("LOGIN_SUCCESS", "Login Success"),
        ("BRUTE_FORCE", "Brute Force Attempt"),
        ("PORT_SCAN", "Port Scan Detected"),
        ("MALWARE", "Malware Alert"),
    ]
    SEVERITY_LEVELS = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    source_ip = models.GenericIPAddressField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    description = models.TextField()

    def __str__(self):
        return f"[{self.event_type}] {self.source_ip} - {self.severity}"
