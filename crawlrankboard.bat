@echo off
setlocal
:PROMPT
SET /P AREYOUSURE=This operation will delete existed output file, are you sure (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO END

del output\dianping_rankboard_%1.jl
rem scrapy crawl dianping_rankboard -o output/dianping_rankboard_%1.jl -t jsonlines -a city=%1 --logfile=running.log --loglevel=DEBUG
scrapy crawl dianping_rankboard -o output/dianping_rankboard_%1.jl -t jsonlines -a city=%1 --logfile=running.log

:END
endlocal


