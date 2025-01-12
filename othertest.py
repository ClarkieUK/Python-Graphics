from datetime import datetime
t = datetime.fromtimestamp(1735689600+(2*3600)).strftime("%A, %B %d, %Y %H:%M:%S")


print(t)