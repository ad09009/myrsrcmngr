from models import scans
import threading

targetsOptions = [(scan.get_target(), scan.ScanTemplate) for scan in scans.objects.filter(active=True).exclude(status=2) if scan.next_execution_at <= timezone.now()]
threads = []
for target, options in targetsOptions:    
    print("target", target, '|', "option", options)
    thread = threading.Thread(target=scan_call, args=(target, options))
    threads.append(thread)


for thread in threads:
    thread.start()
    
    
for thread in threads:
    thread.join()
    
print("Done")

def scan_call(target, options):
    print("Scanning", target, "with options", options)
    # Do the scan here
    
    
