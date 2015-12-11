# -*- coding: utf-8 -*-
from fabric.api import env, run, local, settings
from datetime import datetime

def gitmaster(f='src', m='Commit something to master...', b = 'fix-html'):
	'''gitmaster:f = "ADD FILENAMES"\t(default as 'src && README.md'), 
	          m = "COMMIT LOGGING"\t(default as 'Commit something to master...')
	          b = "Branch name"\t(default as 'fix-html')
	'''	
	local('pwd '
		'&& date '
		'&& touch worklog.md '
		'&& git add {file} '
		'&& git commit -am "{msg}" '
		'&& git push origin fix-html '
		'&& echo "- {msg}" >> worklog.md'.format(msg = m, file=f, branch=b)
        )

def deploysae():
	local('')