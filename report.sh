find tests | egrep 'py$' | awk '{print("coverage run  -a ") $1}' | bash >/dev/null 2>/dev/null
coverage report
echo '' .coverage