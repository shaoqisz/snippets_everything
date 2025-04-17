pyinstaller -F -w snippets.py  -i="pen.ico" -n snippets_everything --distpath dist
xcopy /i /y pen.ico                      dist\

