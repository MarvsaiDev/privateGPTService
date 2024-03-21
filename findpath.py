import sys;
#print(sys.executable)
#print("\n".join(sys.path))
for x in sys.path:
    if 'site-package' in x:
        print(x.split(' ')[0])
